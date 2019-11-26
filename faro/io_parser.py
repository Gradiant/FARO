import os
os.environ['TIKA_SERVER_JAR'] = "https://repo1.maven.org/maven2/org/apache/tika/tika-server/1.22/tika-server-1.22.jar"
import tika
from tika import parser
import logging
import xml.etree.ElementTree as ET


logger = logging.getLogger(__name__)


TAG_DICT = {'p': "paragraph",
            "table": "table"}


def get_text_and_tag(xml_element, tag_list, text_list):
    """ TODO """

    if xml_element.text is None:
        if (xml_element.tag.endswith('table') or
            xml_element.tag.endswith('td') or
            xml_element.tag.endswith('tr')):
            content = ET.tostring(xml_element, encoding='utf-8',
                                  method='text').decode('utf-8')
            tag_list.append("table")
            text_list.append(content)

            return tag_list, text_list
        
        else:
            for _elm in xml_element:
                tag_list, text_list = get_text_and_tag(
                    _elm, tag_list, text_list)

            return tag_list, text_list

    tag_list.append("paragraph")
    text_list.append(xml_element.text)
    
    for _elm in xml_element:
        tag_list, text_list = get_text_and_tag(
            _elm, tag_list, text_list)
    
    return tag_list, text_list


def get_augmented_content(parsed_content):
    """ It extracts sentences, tables and paragraphs
    
    Keyword arguments:
    parsed_content -- content with xml tags parsed with tika

    """

    tree = ET.fromstring(parsed_content)

    for _elem in tree:
        # Find body element
        if _elem.tag.endswith("body"):
            tag_list, text_list = get_text_and_tag(_elem, [], [])
            break

    logger.info("TAG_LIST {}".format(tag_list))
    logger.info("TEXT_LIST {}".format(text_list))
    
    # get tag and text
    # content = ET.tostring(tree, encoding='utf-8', method='text')
    # return content.decode('utf-8')

    return text_list, tag_list


def parse_file(file_path):
    """ Parses a file and returns the list of sentences

    Keyword arguments:
    file_path -- path to file

    """

    parsed = parser.from_file(file_path, xmlContent=True)
    content, content_tags = get_augmented_content(parsed['content'])

    return content, content_tags, parsed['metadata']
