from rapidfuzz import process, fuzz


class Corporative_Detection(object):

    def is_not_corp_email(self, email):
        """ Detect if an email is not corporative

        Keyword arguments:
        email -- the first part on an email (before the @)

        """

        email_parts = email.split("@")

        if self.corp_list is not None:
            # search for corporative mail in list
            for _corp in self.corp_list:
                if _corp in email_parts:
                    return False

        # searching for corporative mails of the type <company>@<company>.com
        _choice = process.extractOne(
            email_parts[0], [email_parts[1]], scorer=fuzz.ratio, score_cutoff=60)

        if not _choice:
            return False

        return self.email_model.predict([email_parts[0]])[0] == "1"

    def __init__(self, email_model, corp_list=None):
        """ Initalization

        Keyword arguments:
        email_model -- a model that detects corporative emails

        """
        self.email_model = email_model
        self.corp_list = corp_list
