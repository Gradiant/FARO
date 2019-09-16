import json
from collections import OrderedDict


class Sensitivity_Scorer(object):
    """ Class to obtain the score of confidentiality based on the entities extracted """

    def _get_ranking(self, summary_dict):
        """ Obtain the ranking from the summary of detected entities

        Keyword arguments:
        summary_dict -- dict with deteted entities (aggregated by type)

        """

        if len(summary_dict) == 0:
            return self.sensitivity_list[0]

        reached_min = False
        current_idx = 0

        for key in summary_dict:
            while (self.ranking_dict[self.sensitivity_list[
                    current_idx]][key]["max"] <= summary_dict[key]):
                current_idx += 1
                reached_min = True
                # check if we are already in the max level of sensitivity
                if current_idx == len(self.sensitivity_list) - 1:
                    break

            if summary_dict[key] >= self.ranking_dict[
                    self.sensitivity_list[current_idx]][key]["min"]:
                reached_min = True

        if reached_min:
            # check if two or more index surpass the min specified
            above_min = 0

            for key in summary_dict:
                if summary_dict[key] >= self.ranking_dict[
                        self.sensitivity_list[current_idx]][key]["min"]:
                    above_min += 1

            if (above_min > self.sensitivity_multiple_kpis and
                    current_idx < len(self.sensitivity_list) - 1):
                current_idx += 1

            return self.sensitivity_list[current_idx]

        # None is not allowded (returning the lowest value in the list)
        return self.sensitivity_list[0]

    def get_sensitivity_score(self, entity_dict):
        """ Obtain the sensitivity score from a list of entities

        Keyword arguments:
        entity_dict -- dictionary of entities

        """

        result_dict = OrderedDict()

        for key in entity_dict:
            if key == "Email":
                if "personal_email" not in result_dict:
                    result_dict["personal_email"] = 0

                result_dict["personal_email"] = len(entity_dict[key])

            elif key == "MONEY":
                if "monetary_quantity" not in result_dict:
                    result_dict["monetary_quantity"] = 0

                result_dict["monetary_quantity"] = len(entity_dict[key])

            elif key == "PER_PROF_ORG":
                if "person_position_organization" not in result_dict:
                    result_dict["person_position_organization"] = 0

                result_dict["person_position_organization"] = len(
                    entity_dict[key])

            elif key == "SIGNATURE":
                if "signature" not in result_dict:
                    result_dict["signature"] = 0

                result_dict["signature"] = len(entity_dict[key])

            elif key in ["DNI_SPAIN", "NI_UK"]:
                if "id_document" not in result_dict:
                    result_dict["document_id"] = 0

                result_dict["document_id"] = len(entity_dict[key])

            elif key == "FinancialData":
                if "financial_data" not in result_dict:
                    result_dict["financial_data"] = 0

                result_dict["financial_data"] = len(entity_dict[key])

            elif key == "MOBILE":
                if "mobile_phone_number" not in result_dict:
                    result_dict["mobile_phone_number"] = 0

                result_dict["mobile_phone_number"] = len(entity_dict[key])

            elif key == "CUSTOM":
                if "custom_words" not in result_dict:
                    result_dict["custom_words"] = 0

                result_dict["custom_words"] = len(entity_dict[key])
                    
        score = self._get_ranking(result_dict)

        return {"score": score, "summary": result_dict}

    def __init__(self, ranking_dict, sensitivity_list,
                 sensitivity_multiple_kpis=3):
        """ Initialization

        Keyword arguments:
        ranking_dict -- dict with type of sensitivity
        sensitivity_list -- list of sensitivity keys (ranked from least to highest)

        """

        self.ranking_dict = ranking_dict
        self.sensitivity_list = sensitivity_list
        self.sensitivity_multiple_kpis = sensitivity_multiple_kpis
