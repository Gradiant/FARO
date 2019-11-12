from langdetect.detector_factory import DetectorFactory
from langdetect.lang_detect_exception import LangDetectException


class DocProfiler(object):

    def detect(self, text):
        """ Obtain the doc class with the highest probability

        Keyword arguments:
        text -- the string to analyze

        """
        detector = self.factory.create()
        detector.append(text)

        try:
            doc_class = self.translation_dict[detector.detect()]
            return doc_class
            
        except LangDetectException:
            pass
            
        return None

    def detect_probs(self, text):

        detector = self.factory.create()
        detector.append(text)
        return detector.get_probabilities()
        
    def __init__(self, profile_path, translation_dict):
        """ Initialization

        Keyword Arguments:
        profile_path: path to the folder where the doc profiles are stored
        translation_dict: dictionary to translate the profile class to the dumped class

        """
        
        self.factory = DetectorFactory()
        self.factory.load_profile(profile_path)
        self.translation_dict = translation_dict
        
