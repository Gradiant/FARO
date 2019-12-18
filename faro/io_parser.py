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


def parse_file(file_path):
    """ Parses a file and returns the list of sentences

    Keyword arguments:
    file_path -- path to file
    threshold_filesize_chars_ratio -- filesize per char ratio in order to force OCR

    """

    # Retrieve envvars
    timeout = int(os.getenv('FARO_REQUESTS_TIMEOUT', 60))
    pdf_ocr_ratio = int(os.getenv('FARO_PDF_OCR_RATIO', 150))
    disable_ocr = os.getenv('FARO_DISABLE_OCR', False)

    # OCR is time consuming we will need to raise the request timeout to allow for processing
    requestOptions = {'timeout': timeout}

    parsed = {'content': None, 'metadata': None}

    try:
        parsed.update(parser.from_file(file_path,
                                       requestOptions=requestOptions))

    except Exception as e:
        logger.error(
            "Unexpected exception during parsing {}".format(e))

        raise e
    filesize = os.path.getsize(file_path)

    # try to implement a smarter strategy for OCRing PDFs
    force_ocr = False
    if parsed['metadata']:
        # Add filesize to metadata
        parsed['metadata']['filesize'] = filesize
        # First check if OCR is disabled by envvar
        if disable_ocr:
            return parsed['content'], parsed['metadata']

        try:
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
                    force_ocr = True
                else:
                    filesize_chars_ratio = filesize / chars
                    if filesize_chars_ratio > pdf_ocr_ratio:
                        force_ocr = True
                        logger.debug('size: {}, chars: {}, ratio: {}'.format(
                            filesize,
                            chars,
                            filesize_chars_ratio))

                if force_ocr:
                    parsed['metadata']['ocr_parsing'] = True
                    # TODO: Grab only content if tika-python merges our PR
                    logger.info("PDF file is big but did not get much content...forcing OCR")
                    parsed_ocr_text = parser.from_file(
                        file_path,
                        headers={'X-Tika-PDFOcrStrategy':
                        'ocr_only'},
                        requestOptions=requestOptions)
                    if parsed['content'] is None:
                        parsed['content'] = parsed_ocr_text['content']
                    else:
                        parsed['content'] += parsed_ocr_text['content']
        except KeyError as e:
            logger.debug("Did not find key {} in metadata".format(e))
            raise e
        except Exception as e:
            logger.error(
                "Unexpected exception while treating PDF OCR strategy {}".format(e))
            raise e

    return parsed['content'], parsed['metadata']
