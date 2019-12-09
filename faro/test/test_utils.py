# Copyright (c) 2019 by Gradiant. All rights reserved.

# This code cannot be used, copied, modified and/or distributed without

# the express permission of the authors.

'''

Created on 1st of October (2019)

@author: Hector Cerezo

'''

import unittest

from .. import utils


class UtilsTest(unittest.TestCase):

    def setUp(self):
        """ Setting up for the test """
        pass

    def tearDown(self):
        """ Cleaning up after the test """
        pass

    def test_normalize_text_proximity_v0(self):
        """ Test the normalization to find words in the proximity """

        message = "este es mi N.I.F.: 4576889J"

        norm_text = utils.normalize_text_proximity(message)

        self.assertEqual(norm_text, "este es mi nif.: 4576889j",
                         "{} Normalized text is not the expected result {}".format(
                             self.shortDescription(),
                             norm_text))
