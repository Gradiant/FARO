import re
from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException
from .io_parser import parse_file


class FARO_Document(object):
    """ Class to store information of the faro documents in an homogeneous format

    The current information per document is:
    - lang -- language detected
    - num_of_pages -- number of pages in the document
    - content_type -- type of content of the document

    """

    def _get_document_metadata(self, metadata):
        """ Extract relevant document metadata from a tika metadata dict

        Keyword arguments:
        meta_dict -- dict of metadata (as returned by tika)

        """

        # FIXME I want lang, num of pages, num_chars, num_words to go here
        
        # extract content type
        if isinstance(metadata["Content-Type"], list):
            self.content_type = str(metadata["Content-Type"][0])
        else:
            self.content_type = metadata["Content-Type"]

        # number of pages
        if "xmpTPg:NPages" in metadata:
            self.num_of_pages = metadata["xmpTPg:NPages"]

        elif "Page-Count" in metadata:
            self.num_of_pages = metadata["Page-Count"]

        elif "meta:page-count" in metadata:
            self.num_of_pages = metadata["meta:page-count"]
            
        else:
            # not supported yet (we consider the document as one page)
            self.num_of_pages = 1

        if "language" in metadata:
            self.lang = metadata["language"]

        # get the number of words/chars in the document
        self.num_words = 0
        self.num_chars = 0
        for line in self.file_lines:
            self.num_words += len(re.sub("[^\w]", " ",  line).split())
            self.num_chars += len(line)
            
        # detect language of file with langdetect (overwrite the tika detection)
        try:
            self.lang = detect(" ".join(self.file_lines))
        except LangDetectException:
            self.lang = "unk"
                    
    def __init__(self, document_path, split_lines):
        """ Initialization
        
        Keyword arguments:
        document_path -- path to the document
        split_lines -- wether to split lines or not

        """
        
        # parse input file and join sentences if requested
        file_lines, file_tag_list, metadata = parse_file(document_path)

        self.file_lines = file_lines
        self.file_tag_list = file_tag_list

        self._get_document_metadata(metadata)

        # store the document path
        self.document_path = document_path
