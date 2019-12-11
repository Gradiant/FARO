from tika import parser
import logging
import collections
import os
os.environ['TIKA_SERVER_JAR'] = "https://repo1.maven.org/maven2/org/apache/tika/tika-server/1.22/tika-server-1.22.jar"

logger = logging.getLogger(__name__)

def flatten(iterable):
    for el in iterable:
        if isinstance(el, collections.Iterable) and not isinstance(el, str):
            yield from flatten(el)
        else:
            yield el

def parse_file(file_path, threshold_filesize_chars_ratio):
    """ Parses a file and returns the list of sentences

    Keyword arguments:
    file_path -- path to file
    threshold_filesize_chars_ratio -- filesize per char ratio in order to force OCR

    """

    parsed = {'content': None, 'metadata': None}
    parsed.update(parser.from_file(file_path))
    filesize = os.path.getsize(file_path)

    # try to implement a smarter strategy for OCRing PDFs
    forceOCR = False
    if parsed['metadata']:
        # Add filesize to metadata
        parsed['metadata']['filesize'] = filesize
        try:
            # First check if OCR is disabled by envvar
            if os.getenv('FARO_DISABLE_OCR'):
                return parsed['content'], parsed['metadata']

            flat_parsed = list(flatten(parsed['metadata']['X-Parsed-By']))
            if any('TesseractOCRParser' in s for s in flat_parsed):
                # OCR already executed, return
                parsed['metadata']['ocr_parsing'] = True
                return parsed['content'], parsed['metadata']

            if parsed['metadata']['Content-Type'] == 'application/pdf':
                # Determine whether or not to run OCR based on the following variables
                #   - Use total number of chars recognized (pdf:charsPerPage)
                #   - Use size of file
                if isinstance(parsed['metadata']['pdf:charsPerPage'], list):
                    chars = sum(map(int,parsed['metadata']['pdf:charsPerPage']))
                else:
                    chars = int(parsed['metadata']['pdf:charsPerPage'])

                if chars == 0:
                    forceOCR = True
                else:
                    filesize_chars_ratio = filesize / chars
                    if filesize_chars_ratio > threshold_filesize_chars_ratio:
                        forceOCR = True
                        logger.debug('size: {}, chars: {}, ratio: {}'.format(
                            filesize,
                            chars,
                            filesize_chars_ratio))

                if forceOCR:
                    parsed['metadata']['ocr_parsing'] = True
                    # TODO: Grab only content if tika-python merges our PR
                    logger.info("PDF file is big but did not get much content...forcing OCR")
                    parsed_ocr_text = parser.from_file(
                        file_path,
                        headers={'X-Tika-PDFOcrStrategy':
                        'ocr_only'})
                    if parsed['content'] is None:
                        parsed['content'] = parsed_ocr_text['content']
                    else:
                        parsed['content'] += parsed_ocr_text['content']
        except KeyError as e:
            logger.debug("Did not find key {} in metadata".format(e))
        except Exception as e:
            logger.error(
                "Unexpected exception while treating PDF OCR strategy {}".format(e))

    return parsed['content'], parsed['metadata']
