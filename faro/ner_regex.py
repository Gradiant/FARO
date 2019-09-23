import regex as re
from collections import OrderedDict


CP_EMAIL_ADDRESS_V0 = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"

CP_CREDIT_CARD_V0 = (r"(?:(?P<visa>((?<![0-9])(?<![0-9][,.]))4[0-9]{12}(?:[0-9]{3})?)|(?P<mastercard>((?<![0-9])(?<![0-9][,.]))5[1-5][0-9]{14})|(?P<discover>((?<![0-9])(?<![0-9][,.]))6(?:011|5[0-9][0-9])[0-9]{12}))")

CP_CREDIT_CARD_GEN_V0 = (r"([0-9]{13}(?:[0-9]{3})?)|([0-9]{4}\s[0-9]{4}\s[0-9]{4}\s[0-9]{4})")
CP_IBAN_V0 = r"\b[A-Z]{2}[0-9]{2}(?:\s+?[0-9]{4}){5}(?!(?:\s+?[0-9]){3})(?:\s+?[0-9]{1,2})?\b"

CP_IBAN_V1 = r"\b[a-zA-Z]{2}[\s\-_]*[0-9]{2}([\s\-_]*[0-9]{4}){5}\b"
CP_IBAN_APPROX_V0 = r"(?i)\biban.*?\K[A-Z][A-Z]([0-9].{0,3}){4,}\b"

CP_DNI_V0 = r"(\b|[\(])[0-9,X,M,L,K,Y][\-\. ]?[0-9]{7}[\-\. ]?[A-Z](\s+|[\)\.\],:])"
CP_CIF_V0 = r"(\b|[\(])[A-Za-z][\-\.\s]?[0-9]{2}(\.?)[0-9]{3}(\.?)[0-9]{3}(\b|[\)\.\],:])"

CP_NI_UK_V0 = r"\b[A-CEGHJ-PR-TW-Z][A-CEGHJ-NPR-TW-Z]{1}[0-9]{6}[A-DFM]?\b"

CP_PHONE_NUMBER_V0 = r"\b(\(?\s*(\+34|0034|34)\s*\)?\s*)?(?<![0-9])[\s|\-|\.]?[8|9][\s+|\-|\.]?([0-9][\s+|\-|\.]?){8}(\s+|\b)(?!(?:\s?[0-9]){1,})"

CP_PHONE_NUMBER_APPROX_V0 = r"(?i)\b(?:(?<=tfno).*?)([0-9][\s\-.]*){6,}\b"
CP_PHONE_NUMBER_APPROX_V1 = r"(?i)\b(?:(?<=teléfono).*?)([0-9][\s\-.]*){6,}\b"
CP_PHONE_NUMBER_APPROX_V2 = r"(?i)\b(?:(?<=tel.).*?)([0-9][\s\-.]*){6,}\b"
CP_PHONE_NUMBER_APPROX_V3 = r"(?i)\b(tfno|tel\.|teléfono).*?\K([0-9][\s\-.]*){6,}\b"

CP_MOBILE_PHONE_NUMBER_V0 = r"\b(\+34|0034|34|\(\+34\))?[\s|\-|\.]?(?<![0-9])[6|7][\s|\-|\.]?([0-9][\s|\-|\.]?){8}\b"

CP_MOBILE_PHONE_NUMBER_V1 = r"\b(?<![\d])\b[6|7][\s|\-|\.]?([0-9][\s|\-|\.]?){8}\b"
CP_MOBILE_PHONE_NUMBER_APPROX_V0 = r"(?i)\bmóvil.*?\K([0-9][\s\-.]*){6,}\b"

CP_MONEY_V0 = r"\b(?<!\.)\d+(\.\d{3,})+(,\d{2,})*(\.\d*)?\b"
CP_MONEY_V1 = r"\b\d+(,\d{2,})\b"
CP_EURO_V0 = r"(?i)(\d+\.)*\d+(,\d{2,})*(\.\d*)?(?=(\s*€|\s*euros|\s*de\s+euros|\s*eur))"
CP_FIRMA_V0 = r"Firmado por|Firmado|Fdo\.|Signed by|Firma\s|firma del representante"

DICT_REGEX = {"Email": [(CP_EMAIL_ADDRESS_V0, "CP_EMAIL_ADDRESS_V0")],
              "CreditCard": [(CP_CREDIT_CARD_V0, "CP_CREDIT_CARD_V0")],
              "FinancialData": [(CP_IBAN_V1, "CP_IBAN_V1"),
                                (CP_IBAN_APPROX_V0, "CP_IBAN_APPROX_V0")],
              "DNI_SPAIN": [(CP_DNI_V0, "CP_DNI_V0"),
                            (CP_CIF_V0, "CP_CIF_V0"),
                            ],
              "NI_UK": [(CP_NI_UK_V0, "CP_NI_UK_V0")],
              "PHONE": [(CP_PHONE_NUMBER_V0, "CP_PHONE_NUMBER_V0"),
                        (CP_PHONE_NUMBER_APPROX_V3, "CP_PHONE_NUMBER_APPROX_V3"),
              ],
              "MOBILE": [(CP_MOBILE_PHONE_NUMBER_V1,
                          "CP_MOBILE_PHONE_NUMBER_V0"),
                         (CP_MOBILE_PHONE_NUMBER_APPROX_V0,
                          "CP_MOBILE_PHONE_NUMBER_APPROX_V0")],
              "MONEY": [(CP_MONEY_V0, "CP_MONEY_V0"),
                        (CP_MONEY_V1, "CP_MONEY_V1"),
                        (CP_EURO_V0, "CP_EURO_V0")],
              "SIGNATURE": [(CP_FIRMA_V0, "CP_FIRMA_V0")]}


class Regex_Ner(object):
    """ Detection of some number-based entities with regular expressions """

    def regex_detection(self, sentence):
        """ Detect entities with a regex in sentence

        Keyword arguments:
        sentence -- a sentence in plain text

        """

        result_dict = OrderedDict()

        for _regex_key in self.regex_compiler_dict:
            for _regex in self.regex_compiler_dict[_regex_key]:
                it = _regex[0].finditer(sentence)

                for match in it:
                    if _regex_key not in result_dict:
                        result_dict[_regex_key] = []

                    result_dict[_regex_key].append(
                        (sentence[match.start():match.end()],
                         _regex[1], match.start(), match.end()))
        return result_dict

    def __init__(self, dict_regex=DICT_REGEX):
        """ Initialization

        Keyword arguments:
        dict_regex -- a dict containing regex for detecting hacks

        """

        self.regex_compiler_dict = OrderedDict()

        # compile the regex in a dict
        for _regex_key in dict_regex:
            self.regex_compiler_dict[_regex_key] = []
            for _regex in dict_regex[_regex_key]:
                self.regex_compiler_dict[_regex_key].append(
                    (re.compile(_regex[0]), _regex[1]))
