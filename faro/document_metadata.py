import logging
import re
from langdetect import detect, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException
from .utils import preprocess_text
from .io_parser import parse_file
from collections import OrderedDict

# init the seeed of the lang detection algorithm
DetectorFactory.seed = 0

logger = logging.getLogger(__name__)


class FARO_Document(object):
    """ Class to store information of the faro documents in an homogeneous format

    The current information per document is:
    - lang -- language detected
    - num_of_pages -- number of pages in the document
    - content_type -- type of content of the document

    """

    def get_metadata_dict(self):
        """ Extract a dictionary with metadata"""

        dict_result = OrderedDict()

        # Adding metadata of fyle type to output
        dict_result["meta:content-type"] = self.content_type
        dict_result["meta:author"] = self.author
        dict_result["meta:pages"] = self.num_of_pages
        dict_result["meta:lang"] = self.lang
        dict_result["meta:date"] = self.creation_date
        dict_result["meta:filesize"] = self.filesize
        dict_result["meta:num_words"] = self.num_words
        dict_result["meta:num_chars"] = self.num_chars
        dict_result["meta:ocr"] = self.ocr_parsing

        return dict_result

    def _get_document_metadata(self, metadata):
        """ Extract relevant document metadata from a tika metadata dict

        Keyword arguments:
        meta_dict -- dict of metadata (as returned by tika)

        """

        logger.info("METADATA DICT {}".format(metadata))

        # extract content type
        if isinstance(metadata["Content-Type"], list):
            self.content_type = str(metadata["Content-Type"][0])
        else:
            self.content_type = metadata["Content-Type"]

        # pick author
        self.author = None
        if "Author" in metadata:
            self.author = metadata["Author"]

        elif "meta:author" in metadata:
            self.author = metadata["meta:author"]

        elif "creator" in metadata:
            self.author = metadata["creator"]

        elif "dc:creator" in metadata:
            self.author = metadata["dc:creator"]

        elif "pdf:docinfo:creator" in metadata:
            self.author = metadata["pdf:docinfo:creator"]

        elif "producer" in metadata:
            self.author = metadata["producer"]

        elif "pdf:docinfo:producer" in metadata:
            self.author = metadata["pdf:docinfo:producer"]

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

        self.filesize = None
        if "filesize" in metadata:
            self.filesize = metadata["filesize"]

        # OCRed
        self.ocr_parsing = False
        if "ocr_parsing" in metadata:
            self.ocr_parsing = metadata["ocr_parsing"]

        # Creation date
        self.creation_date = None
        if "Creation-Date" in metadata:
            self.creation_date = metadata["Creation-Date"]

        elif "meta:creation_date" in metadata:
            self.creation_date = metadata["meta:creation_date"]

        elif "created" in metadata:
            self.creation_date = metadata["created"]

        # get the number of words/chars in the document
        self.num_words = 0
        self.num_chars = 0

        if self.file_lines is not None:
            for line in self.file_lines:
                self.num_words += len(re.sub("[^\w]", " ",  line).split())
                self.num_chars += len(line)

        # detect language of file with langdetect (overwrite the tika detection)
        if "language" in metadata:
            self.lang = metadata["language"]

        try:
            self.lang = detect(" ".join(self.file_lines))

        except LangDetectException:
            self.lang = "unk"

    def _preprocess_file_lines(self, file_lines, join_lines):
        """ Preprocess the text and join the lines if requested

        Keyword arguments:
        file_lines: list of text lines extracted with Tika
        join_lines: should lines be joined (e.g. a paragraph)

        """

        if file_lines is not None:
            file_lines = file_lines.strip().split("\n")
        else:
            file_lines = []

        new_file_lines = []
        for line in file_lines:
            if not join_lines:
                if len(line.strip("")) == 0 or len(new_file_lines) == 0:
                    new_file_lines.append(preprocess_text(line))

                else:
                    new_file_lines[-1] = "{} {}".format(new_file_lines[-1],
                                                        preprocess_text(line))
            else:
                new_file_lines.append(preprocess_text(line))

        file_lines = new_file_lines

        return file_lines

    def __init__(self, document_path, split_lines,
                 threshold_filesize_chars_ratio):
        """ Initialization

        Keyword arguments:
        document_path -- path to the document
        split_lines -- wether to split lines or not
        threshold_chars_per_page -- maximum chars per page in order to not apply OCR
        threshold_filesize_per_page -- maximum filesize per page in order to not apply OCR

        """

        # parse input file and join sentences if requested
        file_lines, metadata = parse_file(document_path,
                                          threshold_filesize_chars_ratio)

        self.file_lines = self._preprocess_file_lines(file_lines, split_lines)
        self._get_document_metadata(metadata)

        # store the document path
        self.document_path = document_path
