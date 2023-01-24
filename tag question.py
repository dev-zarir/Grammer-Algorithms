import spacy

nlp = spacy.load("en_core_web_sm")
operators=['am', 'is', 'are', 'was', 'were', 'have', 'has', 'had', 'can', 'could', 'shall', 'should', 'will', 'would', 'may', 'might', 'must', 'dare', 'need', 'used', 'ought']
exceptional_neg_verbs = {'am': "aren't", 'can': "can't", 'shall': "shan't", 'will': "won't"}

def get_dep_pos_tag(sent:str) -> list:
    doc = nlp(sent)
    data=[]
    for token in doc:
        data.append((token.text, token.dep_, token.pos_, token.tag_))
    return data

def get_negative_verb(verb:str) -> list:
    if verb in exceptional_neg_verbs:
        return exceptional_neg_verbs.get(verb)
    else:
        return verb + "n't"

def get_if_negative_sent(sent:str) -> bool:
    doc = nlp(sent)
    for token in doc:
        if token.dep_ == 'neg':
            return True
    return False

def get_verb_from_sent(sent:str) -> list:
    doc = nlp(sent)
    verbs=[]
    for token in doc:
        if token.dep_ == 'ROOT':
            if token.tag_ == 'VBP': verbs.append('do')
            if token.tag_ == 'VBD': verbs.append('did')
            if token.tag_ == 'VBZ': verbs.append('does')
    return verbs

def get_aux_verb_from_sent(sent:str) -> list:
    doc = nlp(sent)
    aux_verbs=[]
    for token in doc:
        if token.pos_ == 'AUX': aux_verbs.append(token.text)
    return aux_verbs

def get_subject_from_sent(sent:str) -> list:
    doc = nlp(sent)
    subjects=[]
    for token in doc:
        # if token.dep_ == 'nsubj': subjects.append(token.text)
        if token.dep_ == 'nsubj': subjects.append(' '.join([t.text for t in list(token.subtree)]))
    return subjects

def solve_tag_question(sent:str) -> str:
    sentence = sent
    subjects=get_subject_from_sent(sentence)
    aux_verbs=get_aux_verb_from_sent(sentence)
    main_verbs=get_verb_from_sent(sentence)
    negative=get_if_negative_sent(sentence)
    print(get_dep_pos_tag(sentence))
    print('Subjects:', subjects)
    print('Auxilary Verbs:', aux_verbs)
    print('Main Verbs:', main_verbs)
    print('Negative:', negative)
    if aux_verbs: verb=aux_verbs[0]
    else: verb=main_verbs[0]
    if not negative: verb=get_negative_verb(verb)
    return f'{verb} {subjects[0]}'

while 1:
    str_in = input('Sentence: ')
    if str_in == 'exit': quit()
    print('Answer:', solve_tag_question(str_in))

