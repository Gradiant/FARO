# Copyright (c) 2019 by Gradiant. All rights reserved.

# This code cannot be used, copied, modified and/or distributed without

# the express permission of the authors.

'''

Created on 6th of May (2019)

@author: Hector Cerezo

'''

import logging
from collections import OrderedDict
from .ner import NER
from .email import Corporative_Detection
from .ner_regex import Regex_Ner
from .utils import clean_text
from .custom_word import Custom_Word_Detector
from stdnum import get_cc_module
from stdnum.luhn import validate
from stdnum.exceptions import InvalidChecksum, InvalidFormat

logger = logging.getLogger(__name__)


class Detector(object):
    """ Main class for extracting KPIs of confidential documents

    """

    def _get_kpis(self, sent_list):
        """ Extract KPIs from document """

        # full_text is used for proximity detection
        full_text = "".join(sent_list)

        total_ent_list = []

        # Flag to indicate that a sign entity is expected (if True)
        next_person_has_signed = False
        person_signed_idx = 0

        offset = 0

        for sent in sent_list:
            # extract entities (ML)
            if self.ml_ner is not None:
                ent_list_ner = self.ml_ner.get_model_entities(sent)

                for ent in ent_list_ner:
                    # storing as entity/label pair

                    new_ent = [ent[0], ent[1], "NER",
                               str(int(ent[2]) + offset),
                               str(int(ent[3]) + offset)]

                    total_ent_list.append(new_ent)

            # extract entities (Regex)
            ent_list_regex = self.regex_ner.regex_detection(
                sent, full_text, offset)

            for ent_key in ent_list_regex.keys():
                for ent in ent_list_regex[ent_key]:
                    # We treat differently common corporative/personal emails
                    if ent_key == "Email":
                        if not self.corp_email_class.is_not_corp_email(
                                ent[0]):
                            total_ent_list.append((
                                ent[0], "Corp_Email",
                                ent[1], str(ent[2] + offset),
                                str(ent[3] + offset)))

                        else:
                            total_ent_list.append((ent[0], "Email",
                                                   ent[1],
                                                   str(ent[2] + offset),
                                                   str(ent[3] + offset)))

                    elif ent_key == "SIGNATURE":
                        next_person_has_signed = True
                        person_signed_idx = int(ent[3]) + offset

                    elif ent_key == "CreditCard":
                        sent = clean_text(ent[0])
                        try:
                            if validate(sent):
                                logger.debug(
                                    "Credit card accepted {}.{}".format(
                                        sent, ent[0]))

                                total_ent_list.append((ent[0], "FinancialData",
                                                       ent[1],
                                                       str(ent[2] + offset),
                                                       str(ent[3] + offset)))

                        except (InvalidChecksum, InvalidFormat):
                            logger.debug("Wrong credit card {}.{}.".format(
                                sent, ent[0]))

                    elif ent_key in ["FinancialData", "DNI_SPAIN"]:
                        sent = clean_text(ent[0])

                        if (get_cc_module('es', 'dni').is_valid(sent) or
                            get_cc_module('es', 'ccc').is_valid(sent) or
                            get_cc_module('es', 'cif').is_valid(sent) or
                            get_cc_module('es', 'iban').is_valid(sent) or
                                get_cc_module('es', 'nie').is_valid(sent)):

                            total_ent_list.append((ent[0], ent_key, ent[1],
                                                   str(ent[2] + offset),
                                                   str(ent[3] + offset)))
                        else:
                            logger.debug("Invalid data {}.{}".format(
                                sent, ent[0]))

                    else:
                        total_ent_list.append((ent[0], ent_key, ent[1],
                                               str(ent[2] + offset),
                                               str(ent[3] + offset)))

            if next_person_has_signed:
                min_itx_signed = self.signature_max_distance
                id_min_itx = -1

                for i in range(len(total_ent_list)):
                    _ent = total_ent_list[i]

                    if _ent[1] == "PER":
                        if int(_ent[3]) > person_signed_idx:
                            if (int(_ent[3]) - person_signed_idx <
                                    min_itx_signed):
                                min_itx_signed = (int(_ent[3]) -
                                                  person_signed_idx)
                                id_min_itx = i
                                next_person_has_signed = False

                if id_min_itx != -1:
                    _ent = total_ent_list[id_min_itx]

                    total_ent_list.append((_ent[0], "SIGNATURE", _ent[2],
                                           _ent[3], _ent[4]))

            # detection of custom words
            custom_list = self.custom_detector.search_custom_words(sent)
            for _ent in custom_list:
                total_ent_list.append((_ent[0], _ent[1], _ent[0],
                                       str(_ent[2] + offset),
                                       str(_ent[3] + offset)))

            offset += len(sent)

        if next_person_has_signed:
            min_itx_signed = self.signature_max_distance
            id_min_itx = -1

            for i in range(len(total_ent_list)):
                ent = total_ent_list[i]
                if ent[1] == "PER":
                    if int(ent[3]) > person_signed_idx:
                        if int(ent[3]) - person_signed_idx < min_itx_signed:
                            min_itx_signed = int(ent[3]) - person_signed_idx
                            id_min_itx = i
                            next_person_has_signed = False

            if id_min_itx != -1:
                ent = total_ent_list[id_min_itx]

                total_ent_list.append((ent[0], "SIGNATURE", ent[2],
                                       ent[3], ent[4]))

        return total_ent_list

    def _get_unique_ents(self, ent_list):
        """ Process the entities to obtain a json object """

        unique_ent_dict = OrderedDict()
        for _ent in ent_list:
            if _ent[1] not in unique_ent_dict:
                unique_ent_dict[_ent[1]] = OrderedDict()

            if _ent[0] not in unique_ent_dict[_ent[1]]:
                unique_ent_dict[_ent[1]][_ent[0]] = 0

            unique_ent_dict[_ent[1]][_ent[0]] += 1

        return unique_ent_dict

    def _discard_nonunique_kpis(self, ent_list):
        """ Discard non priority entities

        Keyword arguments:
        ent_list -- list of entities extracted by the detector

        """

        visited_entities_dict = OrderedDict()

        if self.low_priority_list is not None:
            for _ent in ent_list:
                if _ent[1] not in self.low_priority_list:
                    visited_entities_dict[_ent[0]] = True

            filtered_entities = []

            for _ent in ent_list:
                if _ent[1] in self.low_priority_list:
                    if _ent[0] not in visited_entities_dict:
                        filtered_entities.append(_ent)

                else:
                    filtered_entities.append(_ent)

            return filtered_entities

        else:
            return ent_list

    def analyse(self, sent_list):
        """ Obtain KPIs from a document and obtain the output in the right format (json)

        Keyword arguments:
        sent_list -- list of sentences to obtain the entities

        """

        total_ent_list = self._get_kpis(sent_list)

        total_ent_list = self._discard_nonunique_kpis(total_ent_list)

        unique_ent_dict = self._get_unique_ents(total_ent_list)

        return unique_ent_dict

    def __init__(self, nlp, crf_list, email_detector, crf_ner_classic,
                 corp_mail_list, custom_word_list, regexp_config_dict,
                 signature_max_distance, low_priority_list):
        """ Intialization

        Keyword Arguments:
        nlp -- a spacy model or None
        crf_list -- list of crfs for custom entities detection
        email_detector -- detector of corporative emails
        crf_ner_classic -- list of crfs for classic ner detection
        corp_mail_list -- list with typical corporative names
        custom_word_list -- list with custom words
        regexp_config_dict -- configuration of the proximity detections
        signature_max_distance -- maximum distance between distance and signature
        low_priority_list -- list of entity types with low priority

        """

        if nlp is not None:
            self.ml_ner = NER(nlp, None, crf_list, crf_ner_classic)
        else:
            self.ml_ner = None

        self.custom_detector = Custom_Word_Detector(nlp, custom_word_list)

        self.regex_ner = Regex_Ner(regexp_config_dict=regexp_config_dict)
        self.corp_email_class = Corporative_Detection(
            email_detector, corp_mail_list)

        self.signature_max_distance = signature_max_distance
        self.low_priority_list = low_priority_list
