from flask import Flask, request, jsonify, render_template
from tag_question import solve_tag_question, nlp
from urllib.parse import unquote_plus

app=Flask(__name__)
app.config['SECRET_KEY'] = 'ighirgiihigh4i3ig43itiheifuhewi'

@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('home.html')

@app.route('/solve-tag', methods=['GET', 'POST'])
def tag_solver():
    return render_template('tag_solve.html')

@app.route('/api/solve-tag', methods=['POST'])
def tag_solver_api():
    question=request.form.get('question')
    # print(question)
    try:
        answer=solve_tag_question(question)
    except:
        return jsonify({'success':False, 'question':question})
    return jsonify({'success':True, 'question':question, 'answer': answer})

@app.route('/debug/<sent>', methods=['GET', 'POST'])
def tag_debug(sent:str):
    sent=unquote_plus(sent)
    global text
    text=""
    def print(*args):
        global text
        text+=" ".join([str(arg) for arg in args])+"\n"
    # SUBTREE
    print('SUBTREE START')
    doc = nlp(sent)
    for token in doc:
        print(token.text + ',', ' '.join([t.text for t in list(token.subtree)]) + ',', token.morph)
    print('SUBTREE END')
    # EXPLAIN
    print("EXPLAIN START")
    doc = nlp(sent)
    data=[]
    for token in doc:
        data.append((token.text, token.dep_, token.pos_, token.tag_))
    print(data)
    print("EXPLAIN END")
    
    return text.replace("\n","<br>")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)

