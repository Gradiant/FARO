import os
os.environ['TIKA_SERVER_JAR'] = "https://repo1.maven.org/maven2/org/apache/tika/tika-server/1.22/tika-server-1.22.jar"
import tika
from tika import parser


def parse_file(file_path):
    """ Parses a file and returns the list of sentences

    Keyword arguments:
    file_path -- path to file

    """

    parsed = parser.from_file(file_path)
    return parsed['content'], parsed['metadata']
