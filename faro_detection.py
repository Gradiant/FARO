#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2018 by Gradiant. All rights reserved.

# This code cannot be used, copied, modified and/or distributed without

# the express permission of the authors.

'''

Created on 13th of March of 2018

@author: hcerezo

'''
import yaml
import os
import sys
import argparse
import logging
from faro.faro_commons import Defaults
from faro.faro_entrypoint import faro_execute as execute


def process_args(args, defaults, description):
    """ Handle input commands
    args - list of command line arguments
    default - default command line values
    description - a string to display at the top of the help message

    """
    parser = argparse.ArgumentParser(description=description)

    # Decoder parameters
    parser.add_argument('--input_file', '-i', dest="input_file",
                        type=str, default=defaults.INPUT_FILE,
                        help=('A confidential document ' +
                              '(defaults: %(default)s)'))

    parser.add_argument('--output_entity_file', dest="output_entity_file",
                        type=str, default=defaults.OUTPUT_ENTITY_FILE,
                        help=('Json file with detected entities ' +
                              '(defaults: %(default)s)'))

    parser.add_argument('--output_score_file',
                        dest="output_score_file",
                        type=str, default=defaults.OUTPUT_SCORE_FILE,
                        help=('Json with sensitivity score and ' +
                              'summary information ' +
                              '(defaults: %(default)s)'))

    parser.add_argument('--split_lines', dest="split_lines",
                        action="store_true", default=defaults.SPLIT_LINES,
                        help=("Do not join sentences of a document " +
                              " (use only if every line in the document " +
                              "is already line in the document " +
                              "(e.g. a raw text file) " +
                              "(defaults: %(default)s)"))

    parser.add_argument('--verbose', dest="verbose",
                        action="store_true", default=defaults.VERBOSE,
                        help=("Store all entities in json " +
                              "(defaults: %(default)s)"))

    parser.add_argument('--dump', dest="dump",
                        action="store_true", default=defaults.DUMP,
                        help=("Dump information to stdout instead of file" +
                              "(defaulits: %(default)s"))

    parameters = parser.parse_args(args)
    return parameters


def launch(args, defaults, description):
    """ Basic launch functionality """

    log_level = os.getenv('FARO_LOG_LEVEL', "INFO")
    log_file = os.getenv('FARO_LOG_FILE', None)

    handlers = [logging.StreamHandler()]
    if log_file is not None:
        handlers.append(logging.FileHandler(log_file))

    logging.basicConfig(
        level=log_level,
        format="%(levelname)s: %(name)20s: %(message)s",
        handlers = handlers
    )

    parameters = process_args(args, defaults, description)
    execute(parameters)


if __name__ == "__main__":
    launch(sys.argv[1:], Defaults, __doc__)
