import logging
import copy
import regex as re
from collections import OrderedDict


logger = logging.getLogger(__name__)

CP_EMAIL_ADDRESS_V0 = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"

CP_CREDIT_CARD_V0 = (r"(?:(?P<visa>((?<![0-9])(?<![0-9][,.]))4[0-9]{12}(?:[0-9]{3})?)|(?P<mastercard>((?<![0-9])(?<![0-9][,.]))5[1-5][0-9]{14})|(?P<discover>((?<![0-9])(?<![0-9][,.]))6(?:011|5[0-9][0-9])[0-9]{12}))")

CP_CREDIT_CARD_GEN_V1 = r"([0-9][\s\-_\.]*){10,}"

CP_CREDIT_CARD_GEN_V0 = (r"([0-9]{13}(?:[0-9]{3})?)|([0-9]{4}\s[0-9]{4}\s[0-9]{4}\s[0-9]{4})")
CP_IBAN_V0 = r"\b[A-Z]{2}[0-9]{2}(?:\s+?[0-9]{4}){5}(?!(?:\s+?[0-9]){3})(?:\s+?[0-9]{1,2})?\b"

CP_IBAN_V1 = r"\b[a-zA-Z]{2}[\s\-_]*[0-9]{2}([\s\-_]*[0-9]{4}){5}\b"
CP_IBAN_APPROX_V0 = r"\b(?i)iban.*?\K[A-Z][A-Z]([0-9].{0,3}){4,}\b"
CP_IBAN_APPROX_V1 = r"(ES)([0-9].{0,3}){4,}"

CP_DNI_V0 = r"(\b|[\(]|\bnº|\bNº)[0-9,X,M,L,K,Y][\-\. ]?[0-9]{7}[\-\. ]?[A-Z](\b|[\)\.\],:])"
CP_CIF_V0 = r"(\b|[\(]|\bnº|\bNº)[A-Za-z][\-\.\s]?[0-9]{2}(\.?)[0-9]{3}(\.?)[0-9]{3}(\b|[\)\.\],:])"

CP_DNI_GEN_V0 = r"[0-9,X,M,L,K,Y][\-\. ]?[0-9]{7}[\-\. ]?[A-Z]?"
CP_CIF_GEN_V0 = r"[A-Za-z][\-\.\s]?[0-9]{2}([\.\-\s]?)[0-9]{3}([\-\.\s]?)[0-9]{3}"

CP_NI_UK_V0 = r"\b[A-CEGHJ-PR-TW-Z][A-CEGHJ-NPR-TW-Z]{1}[0-9]{6}[A-DFM]?\b"

CP_PHONE_NUMBER_V0 = r"\b(\(?\s*(\+34|0034|34)\s*\)?\s*)?(?<![0-9])[\s|\-|\.]?[8|9][\s+|\-|\.]?([0-9][\s+|\-|\.]?){8}(\s+|\b)(?!(?:\s?[0-9]){1,})"

CP_PHONE_NUMBER_APPROX_V0 = r"(?i)\b(?:(?<=tfno).*?)([0-9][\s\-.]*){6,}\b"
CP_PHONE_NUMBER_APPROX_V1 = r"(?i)\b(?:(?<=teléfono).*?)([0-9][\s\-.]*){6,}\b"
CP_PHONE_NUMBER_APPROX_V2 = r"(?i)\b(?:(?<=tel.).*?)([0-9][\s\-.]*){6,}\b"
CP_PHONE_NUMBER_APPROX_V3 = r"(?i)\b(tfno|tel\b|teléfono).*?\K([0-9][\s\-.]*){6,}\b"

CP_PHONE_NUMBER_GEN_V3 = r"(?i)([0-9][\s\-.]*){6,}"
CP_MOBILE_NUMBER_GEN_V3 = r"(?i)([0-9][\s\-.]*){6,}"

CP_MOBILE_PHONE_NUMBER_V0 = r"\b(\+34|0034|34|\(\+34\))?[\s|\-|\.]?(?<![0-9])[6|7][\s|\-|\.]?([0-9][\s|\-|\.]?){8}\b"

CP_MOBILE_PHONE_NUMBER_V1 = r"\b(?<![\d])\b[6|7][\s|\-|\.]?([0-9][\s|\-|\.]?){8}\b"
CP_MOBILE_PHONE_NUMBER_APPROX_V0 = r"(?i)\b(móvil|móv\b|mov\b).*?\K([0-9][\s\-.]*){6,}\b"

CP_MONEY_V0 = r"\b(?<!\.)\d+(\.\d{3,})+(,\d{2,})*(\.\d*)?\b"
CP_MONEY_V1 = r"\b(?<![,\.])\d+(,\d{2,})\b"
CP_EURO_V0 = r"(?i)(\d+\.)*\d+(,\d{2,})*(\.\d*)?(?=(\s*€|\s*euros|\s*de\s+euros|\s*eur))"
CP_FIRMA_V0 = r"Firmado por|Firmado|Fdo\.|Signed by|Firma\s|firma del representante"

DICT_REGEX_STRICT = {"Email": [(CP_EMAIL_ADDRESS_V0, "CP_EMAIL_ADDRESS_V0")],
                     "CreditCard": [(CP_CREDIT_CARD_V0, "CP_CREDIT_CARD_V0")],
                     "FinancialData": [(CP_IBAN_V1, "CP_IBAN_V1")],
                     "DNI_SPAIN": [(CP_DNI_V0, "CP_DNI_V0"),
                                   (CP_CIF_V0, "CP_CIF_V0"),
                     ],
                     "NI_UK": [(CP_NI_UK_V0, "CP_NI_UK_V0")],
                     "PHONE": [
                         (CP_PHONE_NUMBER_APPROX_V3, "CP_PHONE_NUMBER_APPROX_V3"),
                     ],
                     "MOBILE": [
                         (CP_MOBILE_PHONE_NUMBER_APPROX_V0,
                          "CP_MOBILE_PHONE_NUMBER_APPROX_V0")],
                     "MONEY": [(CP_EURO_V0, "CP_EURO_V0")],
                     "PROB_CURRENCY": [(CP_MONEY_V0, "CP_MONEY_V0"),
                                       (CP_MONEY_V1, "CP_MONEY_V1")],
                     "SIGNATURE": [(CP_FIRMA_V0, "CP_FIRMA_V0")]}


DICT_REGEX_BROAD = {"CreditCard": [(CP_CREDIT_CARD_GEN_V1,
                                    "CP_CREDIT_CARD_GEN_V1")],
                    "FinancialData": [(CP_IBAN_APPROX_V1, "CP_IBAN_APPROX_V1")],
                    "DNI_SPAIN": [(CP_DNI_GEN_V0, "CP_DNI_GEN_V0"),
                                  (CP_CIF_GEN_V0, "CP_CIF_GEN_V0"),
                    ],
                    "NI_UK": [(CP_NI_UK_V0, "CP_NI_UK_V0")],
                    "PHONE": [
                        (CP_PHONE_NUMBER_GEN_V3, "CP_PHONE_NUMBER_GEN_V3"),
                    ],
                    "MOBILE": [
                        (CP_MOBILE_NUMBER_GEN_V3,
                         "CP_MOBILE_NUMBER_GEN_V3")]}


class Regex_Ner(object):
    """ Detection of some number-based entities with regular expressions """

    def _detect_regexp(self, sentence, _type):
        """ Use broad/strict coverage regexp to detect possible entities

        Keyword arguments:
        sentence -- string containing the sentence
        _type -- type of regexp [broad or strict]

        """

        result_dict = OrderedDict()
        
        for _regexp_key in self.regexp_compiler_dict[_type]:
            for _regexp in self.regexp_compiler_dict[_type][_regexp_key]:
                it = _regexp[0].finditer(sentence)

                for match in it:
                    if _regexp_key not in result_dict:
                        result_dict[_regexp_key] = []

                    result_dict[_regexp_key].append(
                        (sentence[match.start():match.end()],
                         _regexp[1], match.start(), match.end()))

        return result_dict

    def _check_proximity_conditions(self, unconsolidated_dict,
                                    result_dict,
                                    full_text,
                                    offset):
        """ Check the proximity of keywords to a regexp detection
        
        Keyword arguments:
        unconsolidated_dict -- dict with entities that were not consolidated
        result_dict -- dict to store consolidated entities
        full_text -- a full document
        offset -- offset in the full document of the current sentence

        """
        
        for key in unconsolidated_dict:
            if key in self.regexp_config_dict:
                span_len = self.regexp_config_dict[key]["span_len"]
                word_list = self.regexp_config_dict[key]["word_list"]

                for _regexp in unconsolidated_dict[key]:
                    idx_reg_start = _regexp[2] + offset
                    idx_reg_end = _regexp[3] + offset

                    span_start = idx_reg_start - span_len
                    span_end = idx_reg_end + span_len

                    # safety check: span_start cannot be lower than 0 (beginning of file)
                    if span_start < 0:
                        span_start = 0

                    span_text = full_text[span_start:span_end]

                    match_found = False
                    for _word in word_list:
                        if _word in span_text:
                            match_found = True
                            break

                    if match_found:
                        if key not in result_dict:
                            result_dict[key] = []

                        result_dict[key].append(_regexp)

        return result_dict

    def regex_detection(self, sentence, full_text=None, offset=0):
        """ Detect entities with a regex in sentence

        Keyword arguments:
        sentence -- a sentence in plain text

        """

        # dict to store the consolidated detections
        result_dict = OrderedDict()
        unconsolidated_dict = OrderedDict()
    
        result_broad_dict = self._detect_regexp(sentence, "broad")
        result_strict_dict = self._detect_regexp(sentence, "strict")

        # entities that pass the strict regexp are automatically validated
        result_dict = copy.deepcopy(result_strict_dict)
        
        for key in result_broad_dict:
            consolidated_list = []
            
            if key in result_dict:
                # get the consolidated regexp
                consolidated_list = [regexp[0] for regexp in result_dict[key]]

            for _broad_regexp in result_broad_dict[key]:
                if _broad_regexp[0] not in consolidated_list:
                    if key not in unconsolidated_dict:
                        unconsolidated_dict[key] = []

                    unconsolidated_dict[key].append(_broad_regexp)

        # check proximity conditions of broad regexp detections
        self._check_proximity_conditions(unconsolidated_dict,
                                         result_dict,
                                         full_text,
                                         offset)
                
        return result_dict

    def __init__(self, broad_regexp_dict=DICT_REGEX_BROAD,
                 strict_regexp_dict=DICT_REGEX_STRICT,
                 regexp_config_dict={}):
        """ Initialization

        The process of the application of the regexp is the following:
        First and wide coverage regexp is applied to extract as many
        candidates as possible. ["broad"

        Keyword arguments:
        broad_regexp_dict -- a dict containing the broad coverage regexp
        strict_regexp_dict -- a dict containing stricter regexp
        regexp_config_dict -- a dict containing the configuration
                              on the proximity conditions

        """
        self.regexp_compiler_dict = OrderedDict()

        self.regexp_compiler_dict["broad"] = OrderedDict()
        for _regexp_key in broad_regexp_dict:
            self.regexp_compiler_dict["broad"][_regexp_key] = []

            for _regexp in broad_regexp_dict[_regexp_key]:
                self.regexp_compiler_dict["broad"][_regexp_key].append(
                    (re.compile(_regexp[0]), _regexp[1]))
            
        self.regexp_compiler_dict["strict"] = OrderedDict()
        for _regexp_key in strict_regexp_dict:
            self.regexp_compiler_dict["strict"][_regexp_key] = []

            for _regexp in strict_regexp_dict[_regexp_key]:
                self.regexp_compiler_dict["strict"][_regexp_key].append(
                    (re.compile(_regexp[0]), _regexp[1]))
                
        self.regexp_config_dict = regexp_config_dict
