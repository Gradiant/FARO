import io
import yaml
import json
import spacy
import time
import datetime
import logging
import pandas as pd
from collections import OrderedDict
import gensim.utils as gensim_utils
from faro.detector import Detector
from faro.sensitivity_score import Sensitivity_Scorer
from joblib import load
from .utils import normalize_text_proximity
from .document_metadata import FARO_Document

_COMMONS_YAML = "config/commons.yaml"

ACCEPTED_LANGS = ["es"]

logger = logging.getLogger(__name__)


def init_detector(config):
    """ Initialize an entity detector system

    Keyword arguments:
    config -- a dict with yaml configuration parameters

    """

    crf_list = config["detection"]["crf_ner_list"].split(",")
    crf_model_list = [load(crf) for crf in crf_list]

    crf_ner_classic = None
    if "crf_ner_classic" in config["detection"]:
        crf_ner_classic_list = config["detection"][
            "crf_ner_classic"].split(",")
        crf_ner_classic = [load(crf) for crf in crf_ner_classic_list]

    # search for mail list
    corp_mail_list = []
    if config["detection"]["corp_mail_list"]:
        with open(config["detection"]["corp_mail_list"], "r") as f_in:
            for line in f_in:
                line = line.rstrip("\n")
                corp_mail_list.append(line)

    # build the system here
    nlp = None
    if "nlp_model" in config["detection"]:
        nlp = spacy.load(config["detection"]["nlp_model"])

    custom_word_list = []

    if "custom_word_list" in config:
        with open(config["custom_word_list"], "r") as f_in:
            custom_word_list = [line.rstrip("\n") for line in f_in]

    # configuration of the proximity regexp
    regexp_config_dict = OrderedDict()
    if "proximity_regexp_config" in config:
        for key in config["proximity_regexp_config"]:
            regexp_config_dict[key] = OrderedDict()
            regexp_config_dict[key]["left_span_len"] = int(
                config["proximity_regexp_config"][key]["left_span_len"])

            regexp_config_dict[key]["right_span_len"] = int(
                config["proximity_regexp_config"][key]["right_span_len"])

            with open(config[
                    "proximity_regexp_config"][key]["word_file"], "r") as f_in:
                word_list = [normalize_text_proximity(
                    line.rstrip("\n").strip()) for line in f_in]

            regexp_config_dict[key]["word_list"] = word_list

    low_priority_list = None
    if "low_priority_list" in config:
        low_priority_list = config["low_priority_list"]

    my_detector = Detector(nlp,
                           crf_model_list,
                           load(config[
                               "detection"]["personal_email_detection"]),
                           crf_ner_classic,
                           corp_mail_list=corp_mail_list,
                           custom_word_list=custom_word_list,
                           regexp_config_dict=regexp_config_dict,
                           signature_max_distance=config["signature_max_distance"],
                           low_priority_list=low_priority_list)

    return my_detector


def translate_dict(entity_dict, config):
    """ Translate the keys for coherent json dumping """

    dump_accepted_entity_dict = OrderedDict()

    for key in entity_dict:
        if key in config["ent_keys_dump"]:
            dump_accepted_entity_dict[config[
                "ent_keys_dump"][key]] = entity_dict[key]

        else:
            dump_accepted_entity_dict[key] = entity_dict[key]

    return dump_accepted_entity_dict


def faro_execute(params):
    """ Execution of the main loop """

    # choose the input/output file
    input_file = params.input_file
    if params.output_score_file is None:
        output_score_file = "{}{}".format(params.input_file, ".score")
    else:
        output_score_file = params.output_score_file

    if params.output_entity_file is None:
        output_entity_file = "{}{}".format(params.input_file, ".entity")
    else:
        output_entity_file = params.output_entity_file

    logger.debug("OUTPUTENTITYFILE {}".format(output_entity_file))
    
    # parse input file and join sentences if requested
    logger.info("Analysing {}".format(params.input_file))

    faro_doc = FARO_Document(input_file, params.split_lines)

    # reading commons configuration
    with open(_COMMONS_YAML, "r") as f_stream:
        commons_config = yaml.load(f_stream, Loader=yaml.FullLoader)

    if faro_doc.lang in ACCEPTED_LANGS:
        with open("config/" + lang + ".yaml", "r") as stream:
            config = yaml.load(stream, Loader=yaml.FullLoader)

    else:
        logger.debug(("Language {} is not fully supported. All the " +
                      "functionality is only implemented for these languages: {}").format(
                          faro_doc.lang,
                          " ".join(ACCEPTED_LANGS)))

        with open("config/nolanguage.yaml", "r") as stream:
            config = yaml.load(stream, Loader=yaml.FullLoader)

    # joining two dicts with configurations
    config = {**config, **commons_config}

    # instantiate detector with current configuration
    my_detector = init_detector(config)

    accepted_entity_dict = my_detector.analyse(faro_doc.file_lines)

    # TODO: translate dictionary keys to build a coherent tool
    with io.open(output_entity_file, "a+") as f_out:
        ts = time.time()
        st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

        if params.verbose:
            dump_accepted_entity_dict = translate_dict(
                accepted_entity_dict, config)

            entity_dict = {"filepath": input_file,
                           "entities": dump_accepted_entity_dict,
                           "datetime": st}
            entity_dict = {**entity_dict, **faro_doc.get_metadata_dict()}
                   
            f_out.write("{}\n".format(json.dumps(entity_dict)))

        else:
            # Only show entities appearing in logfilter_entity_list
            filtered_json = OrderedDict()

            for key in accepted_entity_dict:
                if key in config["logfilter_entity_list"]:
                    filtered_json[key] = accepted_entity_dict[key]

            dump_accepted_entity_dict = translate_dict(filtered_json,
                                                       config)

            entity_dict = {"filepath": input_file,
                           "entities": dump_accepted_entity_dict,
                           "datetime": st}

            entity_dict = {**entity_dict, **faro_doc.get_metadata_dict()}
            f_out.write("{}\n".format(json.dumps(entity_dict)))

    # score the document, given the extracted entities
    scorer = Sensitivity_Scorer(config["sensitivity"],
                                config["sensitivity_list"],
                                config["sensitivity_multiple_kpis"])

    dict_result = scorer.get_sensitivity_score(accepted_entity_dict)

    # Adding metadata of fyle type to output

    dict_result.update(faro_doc.get_metadata_dict())

    # dump the score to file or stdout (if dump flag is activated)
    logging.debug("JSON (Entities detected) {}".format(
        json.dumps(dict_result)))

    if output_score_file is not None and not params.dump:
        with open(output_score_file, "w+") as f_out:
            # show all entities detected
            f_out.write("{}\n".format(json.dumps(dict_result)))

    else:
        dump_keys_list = config["sensitivity_keys_dump"]
        panda_dict = OrderedDict()
        panda_dict["id_file"] = params.input_file
        panda_dict["score"] = dict_result["score"]

        for _key in dump_keys_list:
            if _key in dict_result["summary"]:
                panda_dict[_key] = dict_result["summary"][_key]

            else:
                if (_key == "person_position_organization" and
                        faro_doc.lang not in ACCEPTED_LANGS):

                    panda_dict[_key] = None
                else:
                    panda_dict[_key] = 0

        panda_dict.update(faro_doc.get_metadata_dict())
                    
        df = pd.DataFrame(panda_dict, index=[0])
        print(df.to_csv(header="False", index=False).split("\n")[1])
