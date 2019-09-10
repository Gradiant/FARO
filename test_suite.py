# Copyright (c) 2019 by Gradiant. All rights reserved.

# This code cannot be used, copied, modified and/or distributed without

# the express permission of the authors.

'''                                                                                                             

Created on 24th of April (2019)

@author: Hector Cerezo

'''

import os
import logging
import unittest
import xmlrunner


from faro.test import test_regex

suite = unittest.TestSuite()
suite.addTest(unittest.makeSuite(test_regex.RegexTest))

test_runner = xmlrunner.XMLTestRunner(output='test-reports').run(suite)
       
