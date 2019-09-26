import re
import logging
from tabula import read_pdf
from collections import OrderedDict
import numpy as np


logger = logging.getLogger(__name__)


def check_validity(substr, value, idx):
    
    len_substr = len(substr)
    if idx > 0:
        # check no number is before the substring
        for match in re.finditer(r"[0-9]", value[0:idx]):
            return False
        
    # check no number is after the substring
    for match in re.finditer(r"[0-9]", value[idx + len_substr:]):
        return False

    return True


class Doc_Profiler(object):

    def validate_currency(self, input_file, content_type, entity_dict, key):
        """ Validate numbers as currency if they cooccur in tables with keywords
        that typically appear in invoices

        Keyword arguments:
        input_file -- path to the file
        content_type -- metadata of the file (as extracted by tika)
        entity_dict -- dictionary with the entities extracted in a file
        key -- key where there are entities to be validated

        """

        if content_type == "application/pdf":
            if key in entity_dict:
                if "MONEY" in entity_dict:
                    money_dict = entity_dict["MONEY"]
                else:
                    money_dict = None
                probcurrency_dict = entity_dict[key]
                
                unverified_quant_list = []

                # build the list of unverified currency
                for key in probcurrency_dict.keys():
                    # add only if not already verified
                    if money_dict is not None and key not in money_dict:
                        unverified_quant_list.append(key)

                if len(unverified_quant_list) > 0:
                    consolidated_dict = self.process_input(
                        input_file, unverified_quant_list)
                    
                    for key in consolidated_dict:
                        if consolidated_dict[key]:
                            if "MONEY" not in entity_dict:
                                entity_dict["MONEY"] = OrderedDict()
                            entity_dict["MONEY"][key] = probcurrency_dict[key]
                            del probcurrency_dict[key]
    
    def has_keywords(self, values):
        """ Search for one match of the keyword list in the table values

        Keyword arguments:
        values -- list of unique values in the table

        """

        for profiler in self.profiler_list:
            for value in values:
                if value.find(profiler) >= 0:
                    return True
        
        return False

    def process_input(self, input_file, quantity_list):
        """ Obtain the quantity values that appear on tables

        Keyword arguments:
        input_file -- a string containing the path to a pdf file
        quantity_list -- a list with quantity numbers extracted from the text

        """

        print ("Quantity list ", quantity_list)
        
        # build a dict with quantity list and detections
        consolidated_dict = OrderedDict()
        for quantity_key in quantity_list:
            consolidated_dict[quantity_key] = False
        
        df_table_list = read_pdf(input_file,
                                 **{'pages': "all", 'guess': False,
                                    "multiple_tables": True})

        # process individually each table
        for idx, df_table in enumerate(df_table_list):
            # logger.info("TABLE {}: {}".format(idx, df_table))

            unique_values_df = np.unique(
                df_table.to_numpy(dtype="str")).tolist()
            
            # logger.info("UNIQUE VALUES {}".format(np.unique(df_table.to_numpy(dtype="str")).tolist()))
            
            if self.has_keywords(unique_values_df):
                for value in unique_values_df:
                    for _key in consolidated_dict:
                        if not consolidated_dict[_key]:
                            idx = value.find(_key)
                            if (idx >= 0) and check_validity(_key, value, idx):
                                consolidated_dict[_key] = True
                                
        return consolidated_dict
            
    def __init__(self, config):
        """ Initialization

        Keyword arguments:
        config -- a dictionary with configuratin parameters

        """
        
        if "profiler_list" in config:
            self.profiler_list = [str(token.strip().lower())for token
                                  in config["profiler_list"]]
        

