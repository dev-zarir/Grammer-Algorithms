import spacy
from json import load
import warnings

warnings.filterwarnings("ignore")
nlp = spacy.load("en_core_web_sm")
animals_file=open('animals.json','r')
animals_list=load(animals_file)
gender_file=open("all_gender_noun.json", "r")
gender_list=load(gender_file)

subor_conj=['after', 'although', 'as', 'as if', 'as long as', 'because', 'before', 'despite', 'even', 'even if', 'even though', 'if', 'in order that', 'rather', 'rather than', 'since', 'so', 'so that', 'that', 'though', 'unless', 'until', 'whereas', 'whether', 'while', 'what', 'when', 'where', 'who', 'whom', 'which', 'whose', 'why' ,'how']
operators= ['am', 'is', 'are', 'was', 'were', 'have', 'has', 'had', 'can', 'could', 'shall', 'should', 'will', 'would', 'may', 'might', 'must', 'dare', 'need', 'used', 'ought']
exceptional_neg_verbs = {'am': "aren't", 'can': "can't", 'shall': "shan't", 'will': "won't",'need':'need'}
negative_words= ['nothing', 'nobody', 'none', 'never', 'hardly', 'scarcely', 'seldom', 'rarely', 'barely', 'few', 'little', 'no']
imp_replacement=['me','him','her','them', 'it']
# Pronouns: I, you, he, she, it, we, they, there

class Fake_Token: morph = {}; dep_ = ''; pos_ = ''; tag_ = ''; text=''; lemma_=''

def get_gender(noun:str):
    for gender, gender_words in gender_list.items():
        if noun in gender_words:
            return gender 
    return "neuter"

def get_gendered_pronoun_from_subject(subject:str):
    print('given sub:',subject)
    if subject in ['allah', 'god']: return 'He'
    if not subject: return 'it (he/she/it)'
    gender=get_gender(subject)
    if gender=='masculine' or gender=='common': return 'he'
    elif gender=='feminine': return 'she'
    else: return 'it (he/she/it)'

def match_pos(structure:str, sent:str, start_with=False, end_with=False, outsource=[]):
    structure=structure.lower()
    doc = nlp(sent)
    sentence_structure=[]
    for token in doc:
        sentence_structure.append(token.text.lower() if token.text.lower() in outsource else token.pos_.lower())
    if start_with: return '+'.join(sentence_structure).startswith(structure)
    elif end_with: return '+'.join(sentence_structure).endswith(structure)
    return structure in '+'.join(sentence_structure)

def has_nsubj(sent:str):
    print('has sub:', sent)
    doc = nlp(sent)
    for token in doc:
        if token.dep_ in ['nsubj', 'nsubjpass']:
            if token.lemma_ not in subor_conj: return token.text
    return False

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
        if i==0 and token.pos_ == "ADJ" and token.dep_ == 'ROOT':
            sent = "i am " + sent
        i+=1
    if "'d" in sent:
        doc=nlp(sent.capitalize())
        prev_tok=Fake_Token()
        for token in doc:
            if token.tag_ == 'VBN' and prev_tok.text=="'d": sent = sent.replace("'d", ' had')
            if token.tag_ == 'VB' and prev_tok.text=="'d": sent = sent.replace("'d", ' would')
            prev_tok=token
    if sent.startswith('long live') or sent.startswith('longlive'):
        sent='may ' + sent.replace('longlive ', '').replace('long live ', '').replace('longlive', '').replace('long live', '') + ' live long'
    return sent.lower()

def get_exact_sent(sent:str):
    doc = nlp(get_simple_sent(sent))
    root_verb=''
    for token in doc:
        if token.dep_ =='ROOT': root_verb=token.text
        if token.dep_ != 'ROOT' and token.dep_ != 'nsubj':
            sub_or_cls = ' '.join([t.text for t in list(token.subtree)])
            if sub_or_cls.split(' ')[0] in ['not'] and root_verb in ['need']:
                continue
            if not check_if_has_verb(sub_or_cls):
                continue
            if len(sub_or_cls.split(' '))<2:
                continue
            complex_sent=check_if_complex(sub_or_cls)
            print('Complex Sent:', complex_sent)
            if not complex_sent:
                print(f'Retuned text: "{sub_or_cls}"')
                return sub_or_cls, False
            # print('Removed:', sub_or_cls)
            return doc.text.replace(sub_or_cls, '').replace('  ', ' '), True
    return doc.text, False

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

def check_if_has_verb(sent:str) -> bool:
    doc = nlp(sent)
    for token in doc:
        if token.tag_ in ['VERB', 'VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']:
            return True
    return False

def check_if_complex(clause:str) -> bool:
    doc = nlp(clause)
    full_sub_text=''
    for token in doc:
        if token.dep_ in ['nsubj', 'nsubjpass']:
            full_sub_text = ' '.join([t.text for t in list(token.subtree)])
    print(f'clause: "{clause}"')
    print(f'full sub: "{full_sub_text}"')
    first_sub_word=full_sub_text.split(' ')[0]
    if match_pos('ADV',clause.split(' ')[0]):
        return False
    if check_if_has_verb(clause.split(' ')[0]):
        return False
    if clause.split(' ')[0] in subor_conj:
        return True
    if clause.split(' ')[0] != first_sub_word:
        return True
    return False

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
    doc = nlp(sent.capitalize())
    verbs=[]
    for token in doc:
        if token.dep_ == 'ROOT':
            if token.tag_ == 'VBP': verbs.append('do')
            if token.tag_ == 'VBD': verbs.append('did')
            if token.tag_ == 'VBN': verbs.append('did')
            if token.tag_ == 'VBZ': verbs.append('does')
        if token.dep_ == 'pobj' and token.tag_ == 'NNS': verbs.append('does')
    return verbs

def get_aux_verb_from_sent(sent:str) -> list:
    doc = nlp(sent)
    aux_verbs=[]
    i=0
    is_how_adj=False
    for token in doc:
        if token.pos_ == 'AUX' and token.text not in ['be']: aux_verbs.append(token.text)
        if token.dep_ == 'ROOT' and token.text.lower() in ['need'] and len(aux_verbs) == 0: aux_verbs.append(token.text)
        if sent.split(' ')[0].lower() == 'how' and i==1 and token.pos_ == 'ADJ': is_how_adj=True
        i+=1
    if is_how_adj: aux_verbs.append('is')
    print(aux_verbs)
    # They need not complete the work
    if 'need not' not in sent and 'need' in aux_verbs: aux_verbs.remove('need')
    return aux_verbs

def get_subject_from_sent(sent:str) -> list:
    doc = nlp(sent)
    verb=list(doc.sents)[0].root
    full_sub_text=''
    subject=Fake_Token()
    found_sub=False
    aux_verb=Fake_Token()
    found_aux=False
    for token in doc:
        if token.dep_ in ['nsubj', 'nsubjpass']:
            full_sub_text = ' '.join([t.text for t in list(token.subtree)])
        if token.dep_ in ['nsubj', 'nsubjpass', 'expl']:
            if not found_sub: subject = token; found_sub = True
        if token.dep_ in ['aux']:
            if not found_aux: aux_verb = token; found_aux = True
    # print(subject)
    if 'of us' in full_sub_text: return 'we'
    elif 'of them' in full_sub_text: return 'they'
    elif 'who' == full_sub_text: return 'they'
    elif 'this' == full_sub_text or 'that' == full_sub_text: return 'it'
    elif 'these' == full_sub_text or 'those' == full_sub_text: return 'they'
    elif subject.dep_ in ['nsubj'] and subject.pos_ == 'NOUN' and subject.tag_ == 'NN' and subject.text == 'none': return 'they'
    elif subject.pos_ == 'ADJ' and full_sub_text.lower().split(' ')[0] == 'the': return 'they'
    elif match_pos('the+NOUN+and+the+NOUN', full_sub_text, outsource=['the','and']): return 'they'
    elif subject.lemma_ in animals_list and subject.morph.get('Number') == ['Sing']: return 'it'
    elif subject.dep_ in ['expl', 'nsubj'] and subject.pos_ == 'PRON' and subject.tag_ == 'NN' and 'thing' in subject.text.lower(): return 'it'
    elif subject.dep_ in ['expl', 'nsubj'] and subject.pos_ == 'PRON' and subject.tag_ == 'NN' and 'one' in subject.text.lower(): return 'they'
    elif subject.dep_ in ['expl', 'nsubj'] and subject.pos_ == 'PRON' and subject.tag_ == 'NN' and 'body' in subject.text.lower(): return 'they'
    elif subject.dep_ in ['expl', 'nsubj'] and subject.pos_ == 'PRON': return 'they' if subject.text.lower() in ['all'] else subject.text.lower() if subject.text != 'i' else 'I'
    elif verb.morph.get('Person') == ['1'] and verb.morph.get('Number') == ['Sing']: return 'I'
    elif verb.morph.get('Person') == ['1'] and verb.morph.get('Number') == ['Plur']: return 'we'
    elif verb.morph.get('Person') == ['2'] and verb.morph.get('Number') == ['Sing']: return 'you'
    elif verb.morph.get('Person') == ['2'] and verb.morph.get('Number') == ['Plur']: return 'you'
    elif verb.morph.get('Person') == ['3'] and verb.morph.get('Number') == ['Sing']: return get_gendered_pronoun_from_subject(subject.lemma_)
    elif verb.morph.get('Person') == ['3'] and verb.morph.get('Number') == ['Plur']: return 'they'
    elif subject.morph.get('Person') == ['1'] and subject.morph.get('Number') == ['Sing']: return 'I'
    elif subject.morph.get('Person') == ['1'] and subject.morph.get('Number') == ['Plur']: return 'we'
    elif subject.morph.get('Person') == ['2'] and subject.morph.get('Number') == ['Sing']: return 'you'
    elif subject.morph.get('Person') == ['2'] and subject.morph.get('Number') == ['Plur']: return 'you'
    elif subject.morph.get('Person') == ['3'] and subject.morph.get('Number') == ['Sing']: return get_gendered_pronoun_from_subject(subject.lemma_)
    elif subject.morph.get('Person') == ['3'] and subject.morph.get('Number') == ['Plur']: return 'they'
    elif aux_verb.morph.get('Person') == ['1'] and aux_verb.morph.get('Number') == ['Sing']: return 'I'
    elif aux_verb.morph.get('Person') == ['1'] and aux_verb.morph.get('Number') == ['Plur']: return 'we'
    elif aux_verb.morph.get('Person') == ['2'] and aux_verb.morph.get('Number') == ['Sing']: return 'you'
    elif aux_verb.morph.get('Person') == ['2'] and aux_verb.morph.get('Number') == ['Plur']: return 'you'
    elif aux_verb.morph.get('Person') == ['3'] and aux_verb.morph.get('Number') == ['Sing']: return get_gendered_pronoun_from_subject(subject.lemma_)
    elif aux_verb.morph.get('Person') == ['3'] and aux_verb.morph.get('Number') == ['Plur']: return 'they'
    else:
        if subject.morph.get('Number') == ['Plur']: return 'they'
        elif subject.dep_ in ['nsubj'] and subject.pos_ == 'PROPN' and subject.tag_ == 'NNP': return get_gendered_pronoun_from_subject(subject.lemma_)
        else: return get_gendered_pronoun_from_subject(subject.lemma_)

def get_pronoun_from_subject(subject:str) -> str:
    doc = nlp(subject.lower())
    for token in doc:
        # print(list(token.subtree))
        if token.dep_ in ['nsubj', 'nsubjpass'] and token.pos_ == 'PRON': return subject
    return subject

def solve_tag_question(sent:str) -> str:
    # print_subtrees(sent)
    # print(get_explain(sent))
    org_simple_sent=get_simple_sent(sent)
    sentence, is_complex = get_exact_sent(sent)
    if sentence.startswith(' '): sentence=sentence[1:]
    print('given text:',sentence)
    if not has_nsubj(sentence) and check_if_has_verb(sentence.split(' ')[0]) and has_nsubj(org_simple_sent.replace(sentence, '')) and not is_complex:
        sentence=has_nsubj(org_simple_sent.replace(sentence, '')) + ' ' + sentence
    subject=get_subject_from_sent(sentence)
    # print(sentence)

    # loc={}
    # exec(open('practice.py','r').read(), globals(), loc)
    # subject=loc['get_subject_from_sent'](nlp, sentence)

    aux_verbs=get_aux_verb_from_sent(sentence)
    main_verbs=get_verb_from_sent(sentence)
    negative=get_if_negative_sent(sentence)
    print('Subject:', subject)
    print('Auxilary Verbs:', aux_verbs)
    print('Main Verbs:', main_verbs)
    print('Negative:', negative)
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
    str_in = "He visited the place and he was surprised"
    if str_in == 'exit': quit()
    # elif 'python -u' in str_in:continue
    print('Answer:', solve_tag_question(str_in))
