import os
os.environ['TIKA_SERVER_JAR'] = "https://repo1.maven.org/maven2/org/apache/tika/tika-server/1.22/tika-server-1.22.jar"
import tika
from tika import parser
import re
import logging
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import ParseError
from .utils import preprocess_text

logger = logging.getLogger(__name__)


TAG_DICT = {'p': "paragraph",
            "table": "table"}


def parse_file_no_xml(file_path):
    """ TODO """
    
    parsed = parser.from_file(file_path,
                              headers={'X-Tika-PDFOcrStrategy': 'no_ocr'})

    file_lines = parsed['content']
    
    if file_lines is not None:
        file_lines = file_lines.split("\n")
    else:
        file_lines = []
        
    new_file_lines = []
    for line in file_lines:
        if len(line.strip("")) == 0 or len(new_file_lines) == 0:
            new_file_lines.append(preprocess_text(line))

        else:
            new_file_lines[-1] = "{} {}".format(new_file_lines[-1],
                                                preprocess_text(line))
    
    text_list = new_file_lines
    tag_list = ["paragraph" for line in text_list]
    
    return text_list, tag_list


def get_text_and_tag(xml_element, tag_list, text_list):
    """ TODO """

    if xml_element.text is None:
        if (xml_element.tag.endswith('table') or
            xml_element.tag.endswith('td') or
            xml_element.tag.endswith('tr')):
            content = re.sub("\n", " ",
                             ET.tostring(xml_element, encoding='utf-8',
                                         method='text').decode('utf-8'))
            tag_list.append("table")
            text_list.append(content)

            return tag_list, text_list
        
        else:
            for _elm in xml_element:
                tag_list, text_list = get_text_and_tag(
                    _elm, tag_list, text_list)

            return tag_list, text_list

    tag_list.append("paragraph")
    text_list.append(re.sub("\n", " ", xml_element.text))
    
    for _elm in xml_element:
        tag_list, text_list = get_text_and_tag(
            _elm, tag_list, text_list)
    
    return tag_list, text_list


def get_augmented_content(parsed_content, file_path):
    """ It extracts sentences, tables and paragraphs
    
    Keyword arguments:
    parsed_content -- content with xml tags parsed with tika

    """

    try:
        parsed_content = parsed_content.split("</html>")[0] + "</html>"
        
        tree = ET.fromstring(parsed_content)
    
        for _elem in tree:
            # Find body element
            if _elem.tag.endswith("body"):
                tag_list, text_list = get_text_and_tag(_elem, [], [])
                break

        logger.info("TAG_LIST {}".format(tag_list))

    except ParseError:
        logger.error("Error parsing file {}".format(parsed_content))

        text_list, tag_list = parse_file_no_xml(file_path)
            
    return text_list, tag_list


def parse_file(file_path):
    """ Parses a file and returns the list of sentences

    Keyword arguments:
    file_path -- path to file

    """

    parsed = parser.from_file(file_path, xmlContent=True,
                              headers={'X-Tika-PDFOcrStrategy': 'no_ocr'})
    content, content_tags = get_augmented_content(parsed['content'], file_path)

    return content, content_tags, parsed['metadata']
