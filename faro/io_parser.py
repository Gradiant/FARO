import os
os.environ['TIKA_SERVER_JAR'] = "https://repo1.maven.org/maven2/org/apache/tika/tika-server/1.22/tika-server-1.22.jar"
import tika
import logging
from tika import parser
from statistics import mean

logger = logging.getLogger(__name__)


def parse_file(file_path, threshold_chars_per_page=100,
               threshold_filesize_per_page=30000):
    """ Parses a file and returns the list of sentences

    Keyword arguments:
    file_path -- path to file
    threshold_chars_per_page -- maximum chars per page in order to not apply OCR
    threshold_filesize_per_page -- maximum filesize per page in order to not apply OCR
    
    """
    parsed = {'content': None, 'metadata': None}
    parsed.update(parser.from_file(file_path))
    logger.debug(parsed['metadata'])

    # try to implement a smarter strategy for OCRing PDFs
    if parsed['metadata']:
        try:
            if any('TesseractOCRParser' in s for s in parsed['metadata']['X-Parsed-By']):
                # OCR already executed, return
                parsed['metadata']['ocr_parsing'] = True
                
                return parsed['content'], parsed['metadata']
            if parsed['metadata']['Content-Type'] == 'application/pdf':
                # Determine whether or not to run OCR based on the following variables
                #   - Use size of file
                #   - Use number of pages (xmpTPg:NPages)
                #   - Use chars per page (pdf:charsPerPage)
                if isinstance(parsed['metadata']['pdf:charsPerPage'], list):
                    charsperpage = mean(
                        [int(chars_in_page) for chars_in_page in
                         parsed['metadata']['pdf:charsPerPage']])
                else:
                    charsperpage = int(parsed['metadata']['pdf:charsPerPage'])
                    
                if charsperpage <= threshold_chars_per_page:
                    filesize = os.path.getsize(file_path)
                    npages = int(parsed['metadata']['xmpTPg:NPages'])
                    filesizeperpage = filesize / npages
                    # If in average we have less than threshold chars per page
                    # and the average filesize per page is greater 500KB
                    # run OCR and append to content
                    if filesizeperpage >= threshold_filesize_per_page:
                        # TODO: Grab only content if tika-python merges our PR
                        logger.info("File is big but did not get much content...running OCR")
                        parsed_ocr_text = parser.from_file(file_path,
                                                           headers={'X-Tika-PDFOcrStrategy':
                                                                    'ocr_only'})
                        
                        parsed['metadata']['ocr_parsing'] = True
                    
                        if parsed['content'] is None:
                            parsed['content'] = parsed_ocr_text['content']
                        else:
                            parsed['content'] += parsed_ocr_text['content']
        except KeyError as e:
            logger.debug("Did not find key {} in metadata".format(e))
        except Exception as e:
            logger.error("Unexpected exception while treating PDF OCR strategy {}".format(e))

    return parsed['content'], parsed['metadata']
