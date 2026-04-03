from flask import Flask, render_template, request, redirect, session
import json, os

app = Flask(__name__)
app.secret_key = 'secret123'

EVENT_FILE = 'events.json'
USER_FILE = 'users.json'

# Create files if not exist
for file, default in [(EVENT_FILE, {"events": []}), (USER_FILE, {"users": []})]:
    if not os.path.exists(file):
        with open(file, 'w') as f:
            json.dump(default, f)

def load(file):
    with open(file, 'r') as f:
        return json.load(f)

def save(file, data):
    with open(file, 'w') as f:
        json.dump(data, f, indent=4)

# Home page
@app.route('/')
def home():
    if 'user' not in session:
        return redirect('/login')
    data = load(EVENT_FILE)
    return render_template('index.html', events=data['events'], user=session['user'])

# Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        users = load(USER_FILE)
        users['users'].append({
            "username": request.form['username'],
            "password": request.form['password']
        })
        save(USER_FILE, users)
        return redirect('/login')
    return render_template('register.html')

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        users = load(USER_FILE)
        username = request.form['username']
        password = request.form['password']

        for user in users['users']:
            if user['username'] == username and user['password'] == password:
                session['user'] = username
                return redirect('/')
    return render_template('login.html')

# Logout
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')

# Add Event
@app.route('/add', methods=['POST'])
def add_event():
    data = load(EVENT_FILE)
    event = {
        "id": len(data['events']) + 1,
        "name": request.form['name'],
        "date": request.form['date'],
        "time": request.form['time'],
        "location": request.form['location'],
        "image": request.form['image'],
        "likes": 0
    }
    data['events'].append(event)
    save(EVENT_FILE, data)
    return redirect('/')

# Delete Event
@app.route('/delete/<int:id>')
def delete_event(id):
    data = load(EVENT_FILE)
    data['events'] = [e for e in data['events'] if e['id'] != id]
    save(EVENT_FILE, data)
    return redirect('/')

# Like Event
@app.route('/like/<int:id>')
def like_event(id):
    data = load(EVENT_FILE)
    for e in data['events']:
        if e['id'] == id:
            e['likes'] += 1
    save(EVENT_FILE, data)
    return redirect('/')

# Search Event
@app.route('/search', methods=['POST'])
def search():
    query = request.form['query'].lower()
    data = load(EVENT_FILE)
    filtered = [e for e in data['events'] if query in e['name'].lower()]
    return render_template('index.html', events=filtered, user=session['user'])

# Run app
if __name__ == "__main__":
    app.run()
