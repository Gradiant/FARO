import werkzeug
import os
import json
import tempfile
import threading
import logging
from flask import Flask
from flask_restful import Resource, abort, reqparse, Api
from flask_cors import CORS


logger = logging.getLogger(__name__)


parser_analyse = reqparse.RequestParser()
parser_analyse.add_argument('file', type=werkzeug.datastructures.FileStorage,
                            location='files',
                            help='Definition cannot be converted.',
                            required=True)


class Flask_Analyse(Resource):
    """ Implements the classification API """

    def __init__(self, **kwargs):
        # FIXME: use the condition lock
        self.upload_folder = kwargs["upload_folder"]
        self.condition_lock = kwargs["condition_lock"]
        
    def post(self):
        """ Analyse a new file """

        args = parser_analyse.parse_args()

        logger.info("Analysing REQ {}".format(args))

        if args["file"] is None:
            abort(400)

        _file = args["file"]
        file_name, file_extension = os.path.splitext(_file.name)
        
        logger.info("File Contents? {}".format(_file.read()))

        # Create a temporal file
        temp_name = next(tempfile._get_candidate_names())

        # add the right extension
        temp_name = temp_name + file_extension

        # save the file contents
        args["file"].save(temp_name)

        # TODO: execute FARO

        # TODO: delete files
        
        return "OK", 201
    
        
class Flask_Server:
    """ Implements the Flask server """

    def init_views(self):
        """ Init views """

        self.api_rest.add_resource(
            Flask_Analyse,
            "/faro/analyse",
            resource_class_kwargs={'condition_lock': self.condition_lock})

    def __init__(self, service_name="flask_faro",
                 flask_port=5000,
                 upload_folder="/tmp/"):
        """ Initialization stuff

        Keyword arguments:
        service_name -- name of the service
        flask_port -- port used by the API
        upload_folder -- folder to upload files in the server

        """
        
        # Init the flask API
        self.app_rest = Flask(service_name)

        cors = CORS(self.app_rest,
                    resources={r"/faro/*": {"origins": "*"}})

        self.app_rest.config['CORS_HEADERS'] = 'Content-Type'
        
        self.api_rest = Api(self.app_rest)
        
        # Create the lock for multithreading
        self.condition_lock = threading.Condition()
        self.upload_folder = upload_folder

        # Now build the views           
        self.init_views()    
        
        logger.info("Running the API")
        
        # Run the API
        self.app_rest.run(host='0.0.0.0', port=flask_port)




        

