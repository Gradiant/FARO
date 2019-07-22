# Copyright (c) 2019 by Gradiant. All rights reserved.

# This code cannot be used, copied, modified and/or distributed without

# the express permission of the authors.

'''

Created on 24th of April (2019)

@author: Hector Cerezo

'''

from collections import OrderedDict
from .utils import word2features
from .utils import preprocess_text


class NER(object):
    """ A class to extract entities using different NERs """

    def obtain_entities_from_crf_list(self, token_list, crf_ner_list,
                                      ent_list):
        """ Extract entitites with a CRF model

        Keyword arguments:
        token_list -- the list of words, PoS, starting character in sentence and relative position
        crf_ner_list -- list of ners
        ent_list -- a list with extracted entities (from other NERs)

        """

        # obtains the input feats of a sentence
        # (common for all custom crf ners)
        tr_sentence = [word2features(token_list, i)
                       for i in range(len(token_list))]

        for crf_ner in crf_ner_list:
            token_labels = crf_ner.predict([tr_sentence])[0]

            new_entity = None
            label_entity = None

            start_idx = 0
            end_idx = 0
            start_id = 0

            for token, label in zip(token_list, token_labels):
                if label.startswith("B"):
                    start_idx = token[2]
                    start_id = token[3]
                    label_entity = label[2:]
                    end_idx = token[2] + len(token[0])

                    if new_entity is not None:
                        ent_list.append((" ".join(new_entity),
                                         label_entity, start_idx, end_idx,
                                         start_id))

                    new_entity = []
                    new_entity.append(token[0])

                elif label.startswith("O"):
                    if new_entity is not None:
                        ent_list.append((" ".join(new_entity),
                                         label_entity, start_idx, end_idx,
                                         start_id))
                        new_entity = None
                        label_entity = None

                else:
                    if new_entity is not None:
                        end_idx = token[2] + len(token[0])
                        new_entity.append(token[0])

            if new_entity is not None and len(new_entity) > 0:
                new_entity.append((" ".join(new_entity),
                                   label_entity, start_idx, end_idx,
                                   start_id))

        return ent_list

    def _discard_nonfreq_entities(self, ent_list, num_freq):
        """ Frequence of appearance of an entity

        Keyword arguements:
        ent_list -- list with entities detected
        num_freq -- number of repetitions of an entity

        """
        ent_dict = OrderedDict()
        new_ent_list = []

        for ent in ent_list:
            key = "{}_{}_{}_{}".format(ent[0],
                                       ent[1],
                                       ent[2],
                                       ent[3])
            if key not in ent_dict:
                ent_dict[key] = [0, ent]

            ent_dict[key][0] += 1

        for ent_key in ent_dict.keys():
            if ent_dict[ent_key][0] >= num_freq:
                new_ent_list.append(ent_dict[ent_key][1])

        return new_ent_list

    def get_model_entities(self, sentence):
        """ Get enttities with a NER ML model (Spacy)

        Keyword arguments:
        sentence -- a string with a sentence or paragraph

        """

        u_text = preprocess_text(sentence)

        doc = self.nlp(u_text)

        # extracting entities with spacy
        ent_list = []

        if self.crf_ner_classic is None:
            # using SpaCy
            for ent in doc.ents:
                if ent.label_.upper() in ["PER", "ORG"]:
                    ent_list.append((ent.text, ent.label_.upper(),
                                     ent.start_char, ent.end_char,
                                     ent.start))

        else:
            # using custom crfs
            token_list = [(token.text, token.pos_, token.idx, token.i)
                          for token in doc]

            ent_list = self.obtain_entities_from_crf_list(
                token_list, self.crf_ner_classic, ent_list)

            # discard entities that do not exceed a certain number
            ent_list = self._discard_nonfreq_entities(
                ent_list, len(self.crf_ner_classic) - 2)

        # extracting entities with crfs
        if self.crf_ner_list is not None:
            token_list = [(token.text, token.pos_, token.idx, token.i)
                          for token in doc]

            ent_list = self.obtain_entities_from_crf_list(
                token_list, self.crf_ner_list, ent_list)

        if self.nlp_extra is not None:
            for nlp_e in self.nlp_extra:
                doc = nlp_e(u_text)

                for ent in doc.ents:
                    ent_list.append((ent.text, ent.label_,
                                     ent.start_char, ent.end_char, ent.start))

        rel_prof_entity_list = self.search_entity_relations(ent_list, doc,
                                                            ["PROF"], "PER",
                                                            "PER_PROF")
        rel_org_entity_list = self.search_entity_relations(ent_list, doc,
                                                           ["ORG", "LOC"],
                                                           "PER",
                                                           "PER_ORG")

        rel_prof_org_entity_list = self._find_multiple_rels(
            rel_prof_entity_list, rel_org_entity_list, "PER_PROF_ORG")

        for ent in rel_prof_entity_list:
            ent_str = "{} ({})".format(ent[0], ent[2])
            ent_list.append([ent_str, ent[1], ent[3], ent[4]])

        for ent in rel_org_entity_list:
            ent_str = "{} ({})".format(ent[0], ent[2])
            ent_list.append([ent_str, ent[1], ent[3], ent[4]])

        for ent in rel_prof_org_entity_list:
            ent_str = "{} ({}) [{}]".format(ent[0], ent[2], ent[3])
            ent_list.append([ent_str, ent[1], ent[4], ent[5]])

        return ent_list

    def _find_multiple_rels(self, prof_list, org_list, predicate):
        """ Search relations between (PER, PROF and ORG)

        Keyword Arguments:
        prof_list -- list of person-professions pairs extracted
        org_list -- list of person-organization pairs extracted
        predicate -- description of the relation

        """
        rel_prof_org_entity_list = []

        for ent_prof in prof_list:
            for ent_org in org_list:
                if ent_prof[0] == ent_org[0]:
                    rel_prof_org_entity_list.append([
                        ent_prof[0], predicate,
                        ent_prof[2], ent_org[2],
                        ent_prof[3], ent_prof[4]])
                    break

        return rel_prof_org_entity_list

    def search_entity_relations(self, entity_list, doc, object_ent_list,
                                subject_ent, predicate):
        """ Search relations between subject and object entities

        subject_ent and  object_ent entities must be in the same sentence

        Keyword arguments:
        entity_list -- a list with entities
        doc -- a sentence processed with spacy (Doc object)
        object_ent_list -- a list of accepted values of the triple relation
        subject_ent -- the entity the predicate describes
        predicate -- represents the relation between the entities

        """
        rel_entity_list = []

        for ent in entity_list:
            doc_id = ent[4]
            label = ent[1]

            if label in object_ent_list:
                # pick ids till a root node is found
                id_to_root_list = []
                token = doc[doc_id]

                while token.i != token.head.i:
                    id_to_root_list.append(token.i)
                    token = token.head

                id_to_root_list.append(token.i)

                min_common_root = len(doc)
                min_common_chain = len(doc)
                min_ent = None

                # search for the first coincident node whilst
                # going upwards in the graph
                for oth_ent in entity_list:
                    oth_doc_id = oth_ent[4]
                    oth_label = oth_ent[1]

                    if oth_label in subject_ent:
                        token = doc[oth_doc_id]
                        total_jumps = 0
                        chain_found = False
                        chain_found_i = 0

                        while token.i != token.head.i:
                            if token.i in id_to_root_list:
                                chain_found = True
                                for i in range(len(id_to_root_list)):
                                    idx = id_to_root_list[i]
                                    if idx != token.i:
                                        total_jumps += 1
                                    else:
                                        chain_found_i = i
                                        break

                                break

                            total_jumps += 1
                            token = token.head

                        if not chain_found and token.i in id_to_root_list:
                            chain_found = True
                            for i in range(len(id_to_root_list)):
                                idx = id_to_root_list[i]
                                if idx != token.i:
                                    total_jumps += 1
                                else:
                                    chain_found_i = i
                                    break

                        # update only if this is the minimum found of
                        # all the entities
                        if (((total_jumps <= min_common_root and
                              chain_found_i == min_common_chain) or
                             (chain_found_i < min_common_chain)) and
                                chain_found):
                            min_common_root = total_jumps
                            min_common_chain = chain_found_i
                            min_ent = oth_ent[0]

                if min_ent is not None:
                    rel_entity_list.append([min_ent, predicate, ent[0],
                                            str(ent[2]), str(ent[3])])

        return rel_entity_list

    def __init__(self, nlp, nlp_extra=None, crf_ner_list=None,
                 crf_ner_classic=None):
        """ Initialization

        Keyword arguments:
        nlp: spacy model
        nlp_extra: additional spacy models (e.g. with custom entities) (default None)
        crf_ner_list: a list with ner models trained with CRFs (default None)
        crf_ner_classic: a CRF that extract the classic entities (PER, ORG, LOC)

        """

        self.nlp = nlp
        self.nlp_extra = nlp_extra
        self.crf_ner_list = crf_ner_list
        self.crf_ner_classic = crf_ner_classic
