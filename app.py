from flask import Flask, request, jsonify, render_template
from tag_question import solve_tag_question

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)