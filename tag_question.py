import spacy

nlp = spacy.load("en_core_web_sm")
operators= ['am', 'is', 'are', 'was', 'were', 'have', 'has', 'had', 'can', 'could', 'shall', 'should', 'will', 'would', 'may', 'might', 'must', 'dare', 'need', 'used', 'ought']
exceptional_neg_verbs = {'am': "aren't", 'can': "can't", 'shall': "shan't", 'will': "won't",'need':'need'}
negative_words= ['nothing', 'nobody', 'none', 'never', 'hardly', 'scarcely', 'seldom', 'rarely', 'barely', 'few', 'little']
imp_replacement=['me','him','her','them', 'it']
# Pronouns: I, you, he, she, it, we, they, there

class Fake_Token: morph = {}; dep_ = ''; pos_ = ''; tag_ = ''

def print_subtrees(sent:str):
    print('SUBTREE START')
    doc = nlp(sent)
    for token in doc:
        print(token.text + ',', ' '.join([t.text for t in list(token.subtree)]) + ',', token.morph)
    print('SUBTREE END')

def get_last_sent(sent:str):
    doc = nlp(sent)
    doc = list(doc.sents)[-1]
    return doc.text

def get_simple_sent(sent:str):
    sent=get_last_sent(sent).lower().replace('let us', 'we shall not').replace("let's", 'we shall not').replace("'ll",' will').replace("'m", ' am').replace("'s", ' is').replace("can't","can not").replace("aren't","am not").replace("ain't","am not").replace("shan't","shall not").replace("won't","will not").replace("n't", " not").replace("'re"," are").replace("'ve"," have").split(' ')
    if sent[0] == 'let':
        if sent[1] != 'us':
            sent[0] = 'you'
            sent[1] = 'will not'
    sent=' '.join(sent)
    doc=nlp(sent.capitalize())
    i=0
    for token in doc:
        if i==0 and token.tag_ == 'VB':
            sent = 'you will not ' + sent
        if i==0 and token.pos_ == "ADJ":
            sent = "i wish you " + sent
        i+=1
    if "'d" in sent:
        doc=nlp(sent.capitalize())
        prev_tok=Fake_Token()
        for token in doc:
            if token.tag_ == 'VBN' and prev_tok.text=="'d": sent = sent.replace("'d", ' had')
            if token.tag_ == 'VB' and prev_tok.text=="'d": sent = sent.replace("'d", ' would')
            prev_tok=token
    return sent.lower()

def get_exact_sent(sent:str):
    doc = nlp(get_simple_sent(sent))
    for token in doc:
        if token.dep_ in ['relcl', 'ccomp', 'acomp', 'advcl', 'csubjpass']:
            sub_or_cls = ' '.join([t.text for t in list(token.subtree)])
            if len(sub_or_cls.split(' '))<2:
                continue
            # print('Removed:', sub_or_cls)
            return doc.text.replace(sub_or_cls, '').replace('  ', ' ')
    return doc.text

def get_explain(sent:str) -> list:
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
        elif token.lemma_ in negative_words:
            token_index=sent.split(' ').index(token.text)
            if sent.split(' ')[token_index - 1] in ['a','the'] and token.lemma_ in ['few', 'little']:
                return False
            return True
    if 'who' in sent: return True
    return False

def get_verb_from_sent(sent:str) -> list:
    doc = nlp(sent)
    verbs=[]
    for token in doc:
        if token.dep_ == 'ROOT':
            if token.tag_ == 'VBP': verbs.append('do')
            if token.tag_ == 'VBD': verbs.append('did')
            if token.tag_ == 'VBN': verbs.append('did')
            if token.tag_ == 'VBZ': verbs.append('does')
        if token.dep_ == 'pobj':
            if token.tag_ == 'NNS': verbs.append('does')
    return verbs

def get_aux_verb_from_sent(sent:str) -> list:
    doc = nlp(sent)
    aux_verbs=[]
    i=0
    for token in doc:
        if token.pos_ == 'AUX' and token.text not in ['be']: aux_verbs.append(token.text)
        if token.dep_ == 'ROOT' and token.text.lower() in ['need'] and len(aux_verbs) == 0: aux_verbs.append(token.text)
        if sent.split(' ')[0].lower() == 'how' and i==1 and token.pos_ == 'ADJ': aux_verbs.append('is')
        i+=1
    if 'need not' not in sent and 'need' in aux_verbs: aux_verbs.remove('need')
    return aux_verbs

def get_subject_from_sent(sent:str) -> list:
	doc = nlp(sent)
	verb=list(doc.sents)[0].root
	full_sub_text=''
	subject=Fake_Token()
	found_sub=False
	aux_verb=Fake_Token()
	preposition='yugieirugykbvkiy'
	found_aux=False
	for token in doc:
		if token.dep_ in ['nsubj', 'nsubjpass']:
			full_sub_text = ' '.join([t.text for t in list(token.subtree)])
		if token.dep_ in ['nsubj', 'nsubjpass', 'expl']:
			if not found_sub: subject = token; found_sub = True
		if token.dep_ in ['aux']:
			if not found_aux: aux_verb = token; found_aux = True
		if token.dep_ == 'prep': preposition = token.text
	# print(subject)
	if 'of us' in full_sub_text: return 'we'
	elif 'of them' in full_sub_text: return 'they'
	elif 'who' == full_sub_text: return 'they'
	elif 'this' == full_sub_text or 'that' == full_sub_text: return 'it'
	elif 'these' == full_sub_text or 'those' == full_sub_text: return 'they'
	# elif subject.pos_ == 'ADJ' and sent.split(' ')[0] in ['the', 'a', 'an']: return 'they'
	# elif subject.pos_ == 'NOUN' and sent.split(' ')[0] in ['the', 'a', 'an']: return 'they'
	elif subject.dep_ in ['nsubj'] and subject.pos_ == 'NOUN' and subject.tag_ == 'NN' and subject.text == 'none': return 'they'
	elif subject.dep_ in ['expl', 'nsubj'] and subject.pos_ == 'PRON' and subject.tag_ == 'NN' and 'thing' in subject.text.lower(): return 'it'
	elif subject.dep_ in ['expl', 'nsubj'] and subject.pos_ == 'PRON' and subject.tag_ == 'NN' and 'one' in subject.text.lower(): return 'they'
	elif subject.dep_ in ['expl', 'nsubj'] and subject.pos_ == 'PRON' and subject.tag_ == 'NN' and 'body' in subject.text.lower(): return 'they'
	elif subject.dep_ in ['expl', 'nsubj'] and subject.pos_ == 'PRON': return subject.text.lower() if subject.text != 'i' else 'I'
	elif verb.morph.get('Person') == ['1'] and verb.morph.get('Number') == ['Sing']: return 'I'
	elif verb.morph.get('Person') == ['1'] and verb.morph.get('Number') == ['Plur']: return 'we'
	elif verb.morph.get('Person') == ['2'] and verb.morph.get('Number') == ['Sing']: return 'you'
	elif verb.morph.get('Person') == ['2'] and verb.morph.get('Number') == ['Plur']: return 'you'
	elif verb.morph.get('Person') == ['3'] and verb.morph.get('Number') == ['Sing']: return 'he/she/it'
	elif verb.morph.get('Person') == ['3'] and verb.morph.get('Number') == ['Plur']: return 'they'
	elif subject.morph.get('Person') == ['1'] and subject.morph.get('Number') == ['Sing']: return 'I'
	elif subject.morph.get('Person') == ['1'] and subject.morph.get('Number') == ['Plur']: return 'we'
	elif subject.morph.get('Person') == ['2'] and subject.morph.get('Number') == ['Sing']: return 'you'
	elif subject.morph.get('Person') == ['2'] and subject.morph.get('Number') == ['Plur']: return 'you'
	elif subject.morph.get('Person') == ['3'] and subject.morph.get('Number') == ['Sing']: return 'he/she/it'
	elif subject.morph.get('Person') == ['3'] and subject.morph.get('Number') == ['Plur']: return 'they'
	elif aux_verb.morph.get('Person') == ['1'] and aux_verb.morph.get('Number') == ['Sing']: return 'I'
	elif aux_verb.morph.get('Person') == ['1'] and aux_verb.morph.get('Number') == ['Plur']: return 'we'
	elif aux_verb.morph.get('Person') == ['2'] and aux_verb.morph.get('Number') == ['Sing']: return 'you'
	elif aux_verb.morph.get('Person') == ['2'] and aux_verb.morph.get('Number') == ['Plur']: return 'you'
	elif aux_verb.morph.get('Person') == ['3'] and aux_verb.morph.get('Number') == ['Sing']: return 'he/she/it'
	elif aux_verb.morph.get('Person') == ['3'] and aux_verb.morph.get('Number') == ['Plur']: return 'they'
	else:
		if subject.morph.get('Number') == ['Plur']: return 'they'
		elif subject.dep_ in ['nsubj'] and subject.pos_ == 'PROPN' and subject.tag_ == 'NNP': return 'he/she/it'
		else: return 'it'

def get_pronoun_from_subject(subject:str) -> str:
    doc = nlp(subject.lower())
    for token in doc:
        # print(list(token.subtree))
        if token.dep_ in ['nsubj', 'nsubjpass'] and token.pos_ == 'PRON': return subject
    return subject

def solve_tag_question(sent:str) -> str:
    # print_subtrees(sent)
    # print(get_explain(sent))
    sentence = get_exact_sent(sent)
    subject=get_subject_from_sent(sentence)
    # print(sentence)

    # loc={}
    # exec(open('practice.py','r').read(), globals(), loc)
    # subject=loc['get_subject_from_sent'](nlp, sentence)

    aux_verbs=get_aux_verb_from_sent(sentence)
    main_verbs=get_verb_from_sent(sentence)
    negative=get_if_negative_sent(sentence)
    # print('Subject:', subject)
    # print('Auxilary Verbs:', aux_verbs)
    # print('Main Verbs:', main_verbs)
    # print('Negative:', negative)
    if aux_verbs: verb=aux_verbs[0]
    else:
        try:
            verb=main_verbs[0]
        except:
            verb='is'
    if subject=='they':
        if verb == 'does': verb = 'do'
        if verb == 'is': verb = 'are'
        if verb == 'has': verb = 'have'
    if not negative: verb=get_negative_verb(verb)
    return f'{verb} {subject}'

if __name__ == '__main__':
    while 1:
        str_in = input('\nSentence: ')
        if str_in == 'exit': quit()
        elif 'python -u' in str_in:continue
        print('Answer:', solve_tag_question(str_in))
