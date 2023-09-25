from flask import session
from flask import Flask, url_for, request, redirect, session, render_template, jsonify

import openai  # for OpenAI API calls
import time
import os
app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")
print(openai.api_key)
# Set the secret key to some random bytes. Keep this really secret!
app.secret_key = os.urandom(12)
print(app.secret_key)

userData = {}
dialogs = {}

@app.route('/')
def index():
    if 'username' in session:
        return render_template('index.html', name=session["username"])
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        userData[request.form['username']] = request.form['password']
        session['username'] = request.form['username']
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] in userData:
            if request.form['password'] == userData[request.form['username']]:
                session['username'] = request.form['username']
            else:
                return "비밀번호가 틀렸습니다."
        else :
            return "회원가입 해주세욥"
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/chat', methods=['POST'])
def chat():
    if not ('username' in session):
        return render_template('login.html')
    
    jsonData = chat(request.form['content']).json

    return render_template('index.html', name=session["username"], dialogs=dialogs[session["username"]], time=jsonData["time"])

def chat(content: str):
    # send a ChatCompletion request to count to 100
    start_time = time.time()
    if session["username"] in dialogs:
        messages = dialogs[session["username"]] + [{'role': 'user', 'content': f"{content}"}]
    else:
        messages = [{'role': 'user', 'content': f"{content}"}]

    response = openai.ChatCompletion.create(
        model='gpt-4',
        messages = messages,
        temperature= 0.7,
    )
    # print the time delay and text received
    print(f"Full response received:\n{response}")

    messages.append(response.choices[0]["message"].to_dict())
    dialogs[session["username"]] = messages

    print(dialogs)
    jsonData = {
        "content" : response.choices[0]["message"]["content"],
        "time" : time.time() - start_time
    }
    return jsonify(jsonData)
    
if __name__ == '__main__':
    app.run(debug=True)