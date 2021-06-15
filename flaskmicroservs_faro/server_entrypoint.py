import logging
import yaml
from .server import Flask_Server


logger = logging.getLogger(__name__)


def execute(flask_port, upload_folder):
    """ Configuration of the flask API server 

    FLASK_PORT -- port of the flask API
    UPLOAD_FOLDER -- folder to upload files in the server

    """

    Flask_Server(
        flask_port=flask_port,
        upload_folder=upload_folder)
