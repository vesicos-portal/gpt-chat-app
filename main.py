from flask import Flask, render_template, request, session, redirect, url_for, jsonify
import os
import openai
client = openai.OpenAI()

app = Flask(__name__)
app.secret_key = os.urandom(24)
openai.api_key = os.getenv("OPENAI_API_KEY")

user_chats = {}

@app.route('/')
def home():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('chat.html', username=session['user'])

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        session['user'] = email
        user_chats[email] = []
        return redirect(url_for('home'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/chat', methods=['POST'])
def chat():
    if 'user' not in session:
        return jsonify({"reply": "Please log in first."})

    email = session['user']
    message = request.form['message']
    user_chats[email].append({"role": "user", "content": message})

    try:
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=user_chats[email]
        )
        reply = response.choices[0].message.content
        user_chats[email].append({"role": "assistant", "content": reply})
        return jsonify({"reply": reply})

    except Exception as e:
        return jsonify({"reply": "Error: " + str(e)})

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
