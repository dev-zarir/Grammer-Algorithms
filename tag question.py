import nltk
from nltk import word_tokenize

nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')

auxiliary_verbs=["am","is","are","was","were","have","has","had"]

def get_verb_from_sent(sent):
    tokens = nltk.word_tokenize(sent.lower().replace("'m", " am"))
    pos_tags = nltk.pos_tag(tokens)
    print("pos_tags", pos_tags)
    for word, pos in pos_tags:
        if pos == "MD":
            return word
        elif pos == "VBP":
            if word in auxiliary_verbs:
                return word
            else:
                return "do"
        elif pos == "VBZ":
            if word in auxiliary_verbs:
                return word
            else:
                return "does"
        elif pos == "VBD":
            if word in auxiliary_verbs:
                return word
            else:
                return "did"
    return False

while True:
    sentence = "He likes to swim"
    print("Verb:", get_verb_from_sent(sentence))

