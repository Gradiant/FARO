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
from langdetect import detect, DetectorFactory
from faro.detector import Detector
from faro.sensitivity_score import Sensitivity_Scorer
from joblib import load
from .io_parser import parse_file
from .utils import preprocess_text

# init the seeed of the lang detection algorithm
DetectorFactory.seed = 0
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

    my_detector = Detector(nlp,
                           crf_model_list,
                           load(config[
                               "detection"]["personal_email_detection"]),
                           crf_ner_classic,
                           corp_mail_list=corp_mail_list)

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
    file_lines = parse_file(input_file).split("\n")

    new_file_lines = []
    for line in file_lines:
        if not params.split_lines:
            if len(line.strip("")) == 0 or len(new_file_lines) == 0:
                new_file_lines.append(preprocess_text(line))

            else:
                new_file_lines[-1] = "{} {}".format(new_file_lines[-1],
                                                    preprocess_text(line))
        else:
            new_file_lines.append(preprocess_text(line))

    file_lines = new_file_lines

    # detect language of file
    lang = detect(" ".join(file_lines))

    # reading commons configuration
    with open(_COMMONS_YAML, "r") as f_stream:
        commons_config = yaml.load(f_stream, Loader=yaml.FullLoader)

    if lang in ACCEPTED_LANGS:
        with open("config/" + lang + ".yaml", "r") as stream:
            config = yaml.load(stream, Loader=yaml.FullLoader)

    else:
        logger.debug(("Language {} is not fully supported. All the " +
                      "functionality is only implemented for these languages: {}").format(
                          lang,
                          " ".join(ACCEPTED_LANGS)))

        with open("config/nolanguage.yaml", "r") as stream:
            config = yaml.load(stream, Loader=yaml.FullLoader)

    # joining two configurations dict
    config = {**config, **commons_config}

    my_detector = init_detector(config)

    logger.info("Analysing {}".format(params.input_file))

    accepted_entity_dict = my_detector.analyse(file_lines)

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
            f_out.write("{}\n".format(json.dumps(entity_dict)))

    # score the document, given the extracted entities
    scorer = Sensitivity_Scorer(config["sensitivity"],
                                config["sensitivity_list"],
                                config["sensitivity_multiple_kpis"])

    dict_result = scorer.get_sensitivity_score(accepted_entity_dict)

    # dump the score to file or stdout (if dump flag is activated)
    logging.debug("JSON (Entities detected) {}".format(
        json.dumps(dict_result)))

    if output_score_file is not None and not params.dump:
        with open(output_score_file, "w+") as f_out:
            # show all entities detected
            f_out.write("{}\n".format(json.dumps(dict_result)))

    else:
        dump_keys_list = config["sensitivy_keys_dump"]

        panda_dict = OrderedDict()
        panda_dict["id_file"] = params.input_file
        panda_dict["score"] = dict_result["score"]

        for _key in dump_keys_list:
            if _key in dict_result["summary"]:
                panda_dict[_key] = dict_result["summary"][_key]

            else:
                if (_key == "person_position_organization" and
                        lang not in ACCEPTED_LANGS):

                    panda_dict[_key] = None
                else:
                    panda_dict[_key] = 0

        df = pd.DataFrame(panda_dict, index=[0])
        print(df.to_csv(header="False", index=False).split("\n")[1])
