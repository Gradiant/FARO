# Copyright (c) 2019 by Gradiant. All rights reserved.

# This code cannot be used, copied, modified and/or distributed without

# the express permission of the authors.

'''                                                                                                             

Created on 24th of April (2019)

@author: Hector Cerezo

'''

import unittest

from .. import ner_regex
from ..utils import clean_text


class RegexTest(unittest.TestCase):

    def setUp(self):
        """ Setting up for the test """
        pass

    def tearDown(self):
        """ Cleaning up after the test """
        pass

    def test_regexinit(self):
        """ Test the initialization of the regex detection class """

        ner_regex.Regex_Ner()

    def test_0_CP_PHONE_NUMBER_V0(self):
        """ Test the detection of a phone number """

        test = "Mi teléfono es 988 888 888 "
        ner = ner_regex.Regex_Ner()
        
        result = ner.regex_detection(test)

        self.assertTrue("PHONE" in result,
                        "{} Phone was not detected {}".format(
                            self.shortDescription(),
                            result))

        self.assertEqual(clean_text(result["PHONE"][0][0].strip()),
                         "988888888",
                         "{} phone was not detected. Extracted {}".format(
                             self.shortDescription(),
                             result["PHONE"][0]))

    def test_1_CP_PHONE_NUMBER_V0(self):
        """ Test the detection of a phone number """

        test = "Mi teléfono es +34 988 888 888 "
        ner = ner_regex.Regex_Ner()
        
        result = ner.regex_detection(test)

        self.assertTrue("PHONE" in result,
                        "{} Phone was not detected {}".format(
                            self.shortDescription(),
                            result))

        self.assertEqual(clean_text(result["PHONE"][0][0].strip()),
                         "34988888888",
                         "{} phone was not detected. Extracted {}".format(
                             self.shortDescription(),
                             result["PHONE"][0]))

    def test_2_CP_PHONE_NUMBER_V0(self):
        """ Test the detection of a wrong phone number """

        test = "Mi teléfono es +34 988 888 888 456"
        ner = ner_regex.Regex_Ner()
        
        result = ner.regex_detection(test)

        self.assertTrue("PHONE" not in result,
                        "{} Phone was detected {}".format(
                            self.shortDescription(),
                            result))

    def test_3_CP_PHONE_NUMBER_V0(self):
        """ Test the detection of a wrong phone number """

        test = "Mi teléfono es 45 988 888 888"
        ner = ner_regex.Regex_Ner()
        
        result = ner.regex_detection(test)

        self.assertTrue("PHONE" not in result,
                        "{} Phone was detected {}".format(
                            self.shortDescription(),
                            result))

    def test_0_CP_MOBILE_NUMBER_V0(self):
        """ Test the detection of a phone number """

        test = "Mi teléfono es 688 888 888 "
        ner = ner_regex.Regex_Ner()
        
        result = ner.regex_detection(test)

        self.assertTrue("MOBILE" in result,
                        "{} Mobile phone was not detected {}".format(
                            self.shortDescription(),
                            result))

        self.assertEqual(result["MOBILE"][0][0].strip(),
                         "688 888 888",
                         "{} Mobile phone was not detected. Extracted {}".format(
                             self.shortDescription(),
                             result["MOBILE"][0]))

    def test_1_CP_MOBILE_NUMBER_V0(self):
        """ Test the detection of a mobile phone number """

        test = "Mi teléfono es 45 688 888 888 "
        ner = ner_regex.Regex_Ner()
        
        result = ner.regex_detection(test)

        print ("xxxxxxxxxxxxxxxxxxxxx RESULT xxxxxxxxxxxxx ", result)
        
        self.assertTrue("MOBILE" not in result,
                        "{} Mobile phone was detected {}".format(
                            self.shortDescription(),
                            result))
        
    def test_iban_CP_IBAN_V0(self):
        """ Test the detection of the IBAN account """

        test = "This is the IBAN of the account ES91 2100 0418 4502 0005 1332 ."
        ner = ner_regex.Regex_Ner()

        result = ner.regex_detection(test)

        self.assertTrue("FinancialData" in result,
                        "{} IBAN was not detected {}".format(
                            self.shortDescription(),
                            result))

        self.assertEqual(result["FinancialData"][0][0],
                         "ES91 2100 0418 4502 0005 1332",
                         "{} wrong IBAN detected. Detected {}".format(
                             self.shortDescription(),
                             result["FinancialData"][0]))

    def test_is_not_iban_CP_IBAN_V0(self):
        """ Test IBAN is not detected """
        
        test = "This is the IBAN of the account ES91 2100 0418 4502 0005 1332 4576 ."
        ner = ner_regex.Regex_Ner()

        result = ner.regex_detection(test)

        self.assertTrue("FinancialData" not in result,
                        "{} IBAN was detected but it should not{}".format(
                            self.shortDescription(),
                            result))
        
    def test_email_CP_EMAIL_ADDRESS_V0(self):
        """ Detection of email v0 rule """

        test = "the email of John is deadbeaf@foo.bar"
        ner = ner_regex.Regex_Ner()
        result = ner.regex_detection(test)

        self.assertTrue("Email" in result,
                        "{} email was not detected {}".format(
                            self.shortDescription(),
                            result))
        self.assertEqual(result["Email"][0][0], "deadbeaf@foo.bar",
                         "{} wrong email detected. Detected {}".format(
                             self.shortDescription(),
                             result["Email"][0]))
        
    def test_card_CP_CREDIT_CARD_V0(self):
        """ Detection of card v0 rule """

        test = "the visa card is 4111111111111111."

        ner = ner_regex.Regex_Ner()
        result = ner.regex_detection(test)

#        print ("Result ", result)
        
        self.assertTrue("CreditCard" in result,
                        "{} credit card was not detected {}".format(
                            self.shortDescription(),
                            result))

        self.assertEqual(result["CreditCard"][0][0], "4111111111111111",
                         " {} wrong credit card detected. Detected {}".format(
                             self.shortDescription(),
                             result["CreditCard"][0]))

    def test_card_CP_DNI_V0(self):
        """ Detection of DNI v0 rule """

        test = "el dni de Juan es 66666666Y."

        ner = ner_regex.Regex_Ner()
        result = ner.regex_detection(test)
        
        self.assertTrue("DNI_SPAIN" in result,
                        "{} DNI_SPAIN was not detected {}".format(
                            self.shortDescription(),
                            result))

        self.assertEqual(clean_text(result["DNI_SPAIN"][0][0]), "66666666Y",
                         " {} wrong dni detected. Detected {}".format(
                             self.shortDescription(),
                             result["DNI_SPAIN"][0]))

    def test_card_CP_DNI_V0_with_dash(self):
        """ Detection of DNI v0 rule with letter separated by dash """

        test = "el dni de Juan es 66666666-Y."

        ner = ner_regex.Regex_Ner()
        result = ner.regex_detection(test)

        self.assertTrue("DNI_SPAIN" in result, "{} DNI_SPAIN was not detected {}".format(
            self.shortDescription(),
            result))

        self.assertEqual(clean_text(result["DNI_SPAIN"][0][0]), "66666666Y",
                         " {} wrong dni detected. Detected {}".format(
                             self.shortDescription(),
                             result["DNI_SPAIN"][0]))
        
    def test_card_CP_NI_UK_V0(self):
        """ Detection of NI v0 rule """

        test = "el ni de Juan es JG103759A."

        ner = ner_regex.Regex_Ner()
        result = ner.regex_detection(test)
        
        self.assertTrue("NI_UK" in result, "{} NI_UK was not detected {}".format(
            self.shortDescription(),
            result))

        self.assertEqual(result["NI_UK"][0][0], "JG103759A",
                         " {} wrong ni detected. Detected {}".format(
                             self.shortDescription(),
                             result["NI_UK"][0]))
        
    def test_card_CP_PHONE_NUMBER_V0(self):
        """ Detection of phone number """

        test = "el teléfono de Juan es +34 986 000000"

        ner = ner_regex.Regex_Ner()
        result = ner.regex_detection(test)
        
        self.assertTrue("PHONE" in result, "{} PHONE was not detected {}".format(
            self.shortDescription(),
            result))

        self.assertEqual(clean_text(result["PHONE"][0][0]), "34986000000",
                         " {} wrong phone detected. Detected {}".format(
                             self.shortDescription(),
                             result["PHONE"][0]))

    def test_money_CP_EURO_V0(self):
        """ Detection of euro currency """

        test = "este aparato cuesta 1,000€"

        ner = ner_regex.Regex_Ner()
        result = ner.regex_detection(test)

        self.assertTrue("MONEY" in result, "{} MONEY was not detected {}".format(
            self.shortDescription(),
            result))

        # search where euro is rules matches the sentence
        for i in range(len(result["MONEY"])):
            if result["MONEY"][i][1] == "CP_EURO_V0":
                idx = i
        
        self.assertEqual(result["MONEY"][idx][0], "1,000€",
                         " {} wrong currency detected. Detected {}".format(
                             self.shortDescription(),
                             result["MONEY"]))

    def test_money_CP_EURO_V0_euros(self):
        """ Detection of euro currency using the word euro """

        test = "este aparato cuesta 1,000 euros"

        ner = ner_regex.Regex_Ner()
        result = ner.regex_detection(test)

        self.assertTrue("MONEY" in result, "{} MONEY was not detected {}".format(
            self.shortDescription(),
            result))

        # search where euro is rules matches the sentence
        for i in range(len(result["MONEY"])):
            if result["MONEY"][i][1] == "CP_EURO_V0":
                idx = i
        
        self.assertEqual(result["MONEY"][idx][0], "1,000 euros",
                         " {} wrong currency detected. Detected {}".format(
                             self.shortDescription(),
                             result["MONEY"]))

    def test_money_CP_EURO_V0_euros_v1(self):
        """ Detection of euro currency using the word euro """

        test = "este aparato cuesta 1000 euros"

        ner = ner_regex.Regex_Ner()
        result = ner.regex_detection(test)

        self.assertTrue("MONEY" in result, "{} MONEY was not detected {}".format(
            self.shortDescription(),
            result))

        # search where euro is rules matches the sentence
        for i in range(len(result["MONEY"])):
            if result["MONEY"][i][1] == "CP_EURO_V0":
                idx = i
        
        self.assertEqual(result["MONEY"][idx][0], "1000 euros",
                         " {} wrong currency detected. Detected {}".format(
                             self.shortDescription(),
                             result["MONEY"]))

    def test_money_CP_EURO_V0_euros_v2(self):
        """ Detection of euro currency using the word euro """

        test = "este aparato cuesta 1,000.00 euros"

        ner = ner_regex.Regex_Ner()
        result = ner.regex_detection(test)

        self.assertTrue("MONEY" in result, "{} MONEY was not detected {}".format(
            self.shortDescription(),
            result))

        # search where euro is rules matches the sentence
        for i in range(len(result["MONEY"])):
            if result["MONEY"][i][1] == "CP_EURO_V0":
                idx = i
        
        self.assertEqual(result["MONEY"][idx][0], "1,000.00 euros",
                         " {} wrong currency detected. Detected {}".format(
                             self.shortDescription(),
                             result["MONEY"]))

    def test_money_CP_EURO_V0_euros_v3(self):
        """ Detection of euro currency using the word euro """

        test = "este aparato cuesta 1,000.00 Euros"

        ner = ner_regex.Regex_Ner()
        result = ner.regex_detection(test)

        self.assertTrue("MONEY" in result, "{} MONEY was not detected {}".format(
            self.shortDescription(),
            result))

        # search where euro is rules matches the sentence
        for i in range(len(result["MONEY"])):
            if result["MONEY"][i][1] == "CP_EURO_V0":
                idx = i
        
        self.assertEqual(result["MONEY"][idx][0], "1,000.00 Euros",
                         " {} wrong currency detected. Detected {}".format(
                             self.shortDescription(),
                             result["MONEY"]))


        
    def test_cif_company(self):
        """ Test the detection of the CIF of the company """
        
        test = "El CIF de la compañía es A99151276"

        ner = ner_regex.Regex_Ner()
        result = ner.regex_detection(test)

        self.assertTrue("DNI_SPAIN" in result, "{} DNI_SPAIN was not detected {}".format(
            self.shortDescription(),
            result))

        # search where euro is rules matches the sentence
        for i in range(len(result["DNI_SPAIN"])):
            if result["DNI_SPAIN"][i][1] == "CP_DNI_CIF_NIE_V0":
                idx = i
        
        self.assertEqual(result["DNI_SPAIN"][idx][0], "A99151276",
                         " {} wrong NIF detected. Detected {}".format(
                             self.shortDescription(),
                             result["DNI_SPAIN"]))

    def test_email_hack_regex(self):
        """ Test the detection of mail hacks """

        test = "Enviar todos vuestros datos a infoAThacktextDOTcom"
        
        ner = ner_regex.Regex_Ner(dict_regex=ner_regex.HACK_REGEX)
        result = ner.regex_detection(test)

        print ("EMAIL HACK ", result)
        self.assertTrue("Email_Hack" in result,
                        "{} Email Hack was not detected {}. Text {}".format(
                            self.shortDescription(),
                            result,
                            test))

        test = "Enviar todos vuestros datos a info AT hacktext DOT com"

        ner = ner_regex.Regex_Ner(dict_regex=ner_regex.HACK_REGEX)
        result = ner.regex_detection(test)
        
        print ("EMAIL HACK ", result)
        self.assertTrue("Email_Hack" in result,
                        "{} Email Hack was not detected {}. Text {}".format(
                            self.shortDescription(),
                            result,
                            test))

        test = "Enviar todos vuestros datos a info (AT) hacktext (DOT) com"

        ner = ner_regex.Regex_Ner(dict_regex=ner_regex.HACK_REGEX)
        result = ner.regex_detection(test)

        print ("EMAIL HACK ", result)
        self.assertTrue("Email_Hack" in result,
                        "{} Email Hack was not detected {}. Text {}".format(
                            self.shortDescription(),
                            result,
                            test))

        test = "Enviar todos vuestros datos a info-AT-hacktext-DOT-com"

        ner = ner_regex.Regex_Ner(dict_regex=ner_regex.HACK_REGEX)
        result = ner.regex_detection(test)

        print ("EMAIL HACK ", result)
        self.assertTrue("Email_Hack" in result,
                        "{} Email Hack was not detected {}. Text {}".format(
                            self.shortDescription(),
                            result,
                            test))
        
        test = "Enviar todos vuestros datos a info-at-hacktext-dot-com"
                
        ner = ner_regex.Regex_Ner(dict_regex=ner_regex.HACK_REGEX)
        result = ner.regex_detection(test)

        print ("EMAIL HACK ", result)
        self.assertTrue("Email_Hack" in result,
                        "{} Email Hack was not detected {}. Text {}".format(
                            self.shortDescription(),
                            result,
                            test))

        test = "Enviar todos vuestros datos a at-dot"
                
        ner = ner_regex.Regex_Ner(dict_regex=ner_regex.HACK_REGEX)
        result = ner.regex_detection(test)

        print ("EMAIL HACK ", result)
        self.assertTrue("Email_Hack" not in result,
                        "{} Wrong email Hack was detected {}. Text {}".format(
                            self.shortDescription(),
                            result,
                            test))

        
