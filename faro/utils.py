import re


def to_unicode(text, errors='strict'):
    """Convert `text` (bytestring in given encoding or unicode) to unicode.
    
    Keyword arguments:
    text -- Input text
    errors --   Error handling behaviour if `text` is a bytestring. (optional)
 
    Returns Unicode version of `text`.
    """
    if isinstance(text, str):
        return text
    return str(text, "utf-8", errors=errors)


def normalize_text_proximity(message):
    """ Clean text of dots between words

    Keyword arguments:
    message -- a plain sentence or paragraph

    """

    sent = message.lower()
    sent = sent.replace("á", "a")
    sent = sent.replace("é", "e")
    sent = sent.replace("í", "i")
    sent = sent.replace("ó", "o")
    sent = sent.replace("ú", "u")
    sent = re.sub(r'(?i)(?<=[a-z])\.(?=[a-z])', "", sent)

    return sent


def clean_text(message):
    """ Delete extra characters from text before validation

    Keyword arguments:
    message -- a plain sentence or paragraph

    """

    sent = re.sub(r'[\-_*+,\(\).:]{1,}', "", message)
    sent = re.sub(r'[ ]{1,}', "", sent)
    sent = re.sub(r'(?i)\bnº', "", sent)

    return sent


def preprocess_text(message):
    """ Delete some artifacts from text

    Keyword arguments:
    message -- a plain sentence or paragraph

    """

    uni_message = to_unicode(message)
    uni_message = uni_message.replace("\t", " ")
    uni_message = uni_message.replace("\r\n", " ")
    uni_message = uni_message.replace("\r", " ")
    uni_message = uni_message.replace("\n", " ")

    return uni_message


def word2features(sent, i):
    """ Extract features of a node in the "sent" list for a CRF

    Keyword arguments:
    sent -- a list of triples <word, PoS tag, label>
    i -- index of the node to extract the featues

    """

    word = sent[i][0]
    postag = sent[i][1]

    features = {
        'bias': 1.0,
        'word': word,
        'word.lower()': word.lower(),
        'word.istitle()': word.istitle(),
        'word[-3:]': word[-3:],
        'word[:3]': word[:3],
        'word.isdigit()': word.isdigit(),
        'postag': postag,

    }

    if i > 0:
        word1 = sent[i-1][0]
        postag1 = sent[i-1][1]
        features.update({
            '-1:word': word1,
            '-1:word.lower()': word1.lower(),
            '-1:word.istitle': word1.istitle(),
            '-1:postag': postag1,
        })

    else:
        features['BOS'] = True

    # EXTRA

    if i > 2:
        word1 = sent[i-2][0]
        postag1 = sent[i-2][1]
        features.update({
            '-2:word': word1,
            '-2:word.lower()': word1.lower(),
            '-2:word.istitle': word1.istitle(),
            '-2:word.postag': postag1,
        })

    if i > 3:
        word1 = sent[i-3][0]
        postag1 = sent[i-3][1]
        features.update({
            '-3:word': word1,
            '-3:word.lower()': word1.lower(),
            '-3:word.istitle': word1.istitle(),
            '-3:word.postag': postag1,
        })

    if i > 2:
        word0 = sent[i][0]
        postag0 = sent[i][1]
        word1 = sent[i-1][0]
        postag1 = sent[i-1][1]

        features.update({
            '-01:word': word1 + word0,
            '-01:word.lower()': (word1 + " " + word0).lower(),
            '-01:word0_postag1': postag1 + word0,
            '-01:word1_postag0': postag0 + word1,
            })

    if i > 3:
        word0 = sent[i][0]
        word1 = sent[i-2][0]
        postag0 = sent[i][1]
        postag1 = sent[i-2][1]

        features.update({
            '-02:word': word1 + word0,
            '-02:word.lower()': (word1 + " " + word0).lower(),
            '-02:word0_postag1': postag1 + word0,
            '-02:word1_postag0': postag0 + word1,

            })

    if i < len(sent) - 2:
        word1 = sent[i+2][0]
        postag1 = sent[i+2][1]
        features.update({
            '+2:word': word1,
            '+2:word.lower()': word1.lower(),
            '+2:word.istitle': word1.istitle(),
            '+2:word.postag': postag1,
            })

    if i < len(sent)-1:
        word1 = sent[i+1][0]
        postag1 = sent[i+1][1]
        features.update({
            '+1:word': word1,
            '+1:word.lower()': word1.lower(),
            '+1:word.istitle()': word1.istitle(),
            '+1:postag': postag1,
        })
    else:
        features['EOS'] = True

    return features


def char2features_mail(sent, i):
    """ Extract features of a node (for the mail CRF)

    Keyword arguments:
    sent -- a list of pairs <word, label>
    i -- index of the node to extract the featues

    """

    word = sent[i][0]

    features = {
        'bias': 1.0,
        'char.lower()': word.lower(),
    }

    if i > 0:
        word1 = sent[i-1][0]
        features.update({
            '-1:char.lower()': word1.lower(),
        })
    else:
        features['BOS'] = True

    if i < len(sent)-1:
        word1 = sent[i+1][0]
        features.update({
            '+1:char.lower()': word1.lower(),
        })
    else:
        features['EOS'] = True

    # EXTRA

    if i > 2:
        word1 = sent[i-2][0]
        features.update({
            '-2:char.lower()': word1.lower(),
        })

    if i > 3:
        word1 = sent[i-3][0]
        features.update({
            '-3:char.lower()': word1.lower(),
        })

    if i > 4:
        word1 = sent[i-4][0]
        features.update({
            '-4:char.lower()': word1.lower(),
        })

    if i > 5:
        word1 = sent[i-5][0]
        features.update({
            '-5:char.lower()': word1.lower(),
        })

    if i > 6:
        word1 = sent[i-6][0]
        features.update({
            '-6:char.lower()': word1.lower(),
        })

    if i > 7:
        word1 = sent[i-7][0]
        features.update({
            '-7:char.lower()': word1.lower(),
        })

    if i > 8:
        word1 = sent[i-8][0]
        features.update({
            '-8:char.lower()': word1.lower(),
        })

    if i < len(sent) - 2:
        word1 = sent[i+2][0]
        features.update({
            '+2:char.lower()': word1.lower(),
            })

    if i < len(sent) - 3:
        word1 = sent[i+3][0]
        features.update({
            '+3:char.lower()': word1.lower(),
        })

    if i < len(sent) - 4:
        word1 = sent[i+4][0]
        features.update({
            '+4:char.lower()': word1.lower(),
        })

    if i < len(sent) - 5:
        word1 = sent[i+5][0]
        features.update({
            '+5:char.lower()': word1.lower(),
        })

    if i < len(sent) - 6:
        word1 = sent[i+6][0]
        features.update({
            '+6:char.lower()': word1.lower(),
        })

    if i < len(sent) - 7:
        word1 = sent[i+7][0]
        features.update({
            '+7:char.lower()': word1.lower(),
        })

    if i < len(sent) - 8:
        word1 = sent[i+8][0]
        features.update({
            '+8:char.lower()': word1.lower(),
        })

    return features


def char2features_space(sent, i):
    """ Extract features of a node (for the whitespace-CRF detector)

    Keyword arguments:
    sent -- a list of pairs <word, label>
    i -- index of the node to extract the featues

    """

    word = sent[i][0]

    features = {
        'bias': 1.0,
        'char': word,
        'char.lower()': word.lower(),
    }

    if i > 0:
        word1 = sent[i-1][0]
        features.update({
            '-1:char': word1,
            '-1:char.lower()': word1.lower(),
            '-1:char.isdigit()': word1.isdigit(),
        })
    else:
        features['BOS'] = True

    if i < len(sent)-1:
        word1 = sent[i+1][0]
        features.update({
            '+1:char': word1,
            '+1:char.lower()': word1.lower(),
            '+1:char.isdigit()': word1.isdigit(),
        })
    else:
        features['EOS'] = True

    # EXTRA
    if i > 2:
        word1 = sent[i-2][0]
        features.update({
            '-2:char': word1,
            '-2:char.lower()': word1.lower(),
            '-2:char.isdigit()': word1.isdigit(),
        })

    if i > 2:
        word1 = sent[i-2][0]
        word2 = sent[i-1][0]
        features.update({
            '-21:char.lower()': word1.lower() + word2.lower(),
            '-21:char.isdigit()': word1.isdigit() and word2.isdigit(),
        })

    if i > 3:
        word1 = sent[i-3][0]
        features.update({
            '-3:char': word1,
            '-3:char.lower()': word1.lower(),
            '-3:char.isdigit()': word1.isdigit(),
        })

    if i > 3:
        word1 = sent[i-3][0]
        word2 = sent[i-2][0]
        features.update({
            '-32:char.lower()': word1.lower() + word2.lower(),
            '-32:char.isdigit()': word1.isdigit() and word2.isdigit(),
        })

    if i < len(sent) - 2:
        word1 = sent[i+2][0]
        features.update({
            '+2:char': word1,
            '+2:char.lower()': word1.lower(),
            '+2:char.isdigit()': word1.isdigit(),
            })

    if i < len(sent) - 2:
        word1 = sent[i+1][0]
        word2 = sent[i+2][0]
        features.update({
            '+21:char.lower()': word1.lower() + word2.lower(),
            '+21:char.isdigit()': word1.isdigit() and word2.isdigit(),
            })

    if i < len(sent) - 3:
        word1 = sent[i+3][0]
        features.update({
            '+3:char': word1,
            '+3:char.lower()': word1.lower(),
            '+3:char.isdigit()': word1.isdigit(),
            })

    if i < len(sent) - 3:
        word1 = sent[i+2][0]
        word2 = sent[i+3][0]

        features.update({
            '+32:char.lower()': word1.lower() + word2.lower(),
            '+32:char.isdigit()': word1.isdigit() and word2.isdigit(),
            })

    if i < len(sent) - 3:
        word0 = sent[i][0]
        word1 = sent[i+1][0]
        word2 = sent[i+2][0]

        features.update({
            '+02:lower()': (word0 + word1 + word2).lower(),
            '+02:isdigit()': (word0 + word1 + word2).isdigit(),
            })

    return features
