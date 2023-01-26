from flask import Flask, request, jsonify, render_template

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
    return 'Hello World'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)