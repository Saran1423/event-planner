from flask import Flask, render_template, request, redirect, session
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = "secret123"

# -------------------------
# Load & Save Data Functions
# -------------------------
def load_events():
    with open("events.json", "r") as f:
        return json.load(f)

def save_events(data):
    with open("events.json", "w") as f:
        json.dump(data, f, indent=4)

def load_users():
    with open("users.json", "r") as f:
        return json.load(f)

def save_users(data):
    with open("users.json", "w") as f:
        json.dump(data, f, indent=4)

# -------------------------
# Context Processor for Today's Events
# -------------------------
@app.context_processor
def inject_today_events():
    data = load_events()
    today_str = datetime.today().strftime("%Y-%m-%d")
    today_events = [e for e in data["events"] if e["date"] == today_str]
    return dict(today_events=today_events, today_date=today_str)

# -------------------------
# Routes
# -------------------------
@app.route("/")
def home():
    if "user" not in session:
        return redirect("/login")
    data = load_events()
    return render_template("index.html", events=data["events"], user=session["user"], role=session.get("role"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        users = load_users()
        users["users"].append({
            "username": request.form["username"],
            "password": request.form["password"],
            "role": "student"
        })
        save_users(users)
        return redirect("/login")
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        users = load_users()
        for u in users["users"]:
            if u["username"] == request.form["username"] and u["password"] == request.form["password"]:
                session["user"] = u["username"]
                session["role"] = u.get("role", "student")
                return redirect("/")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# Add Event/Seminar (Admin only)
@app.route("/add", methods=["POST"])
def add():
    if session.get("role") != "admin":
        return "Access Denied"

    data = load_events()
    new_event = {
        "id": len(data["events"]) + 1,
        "name": request.form["name"],
        "date": request.form["date"],
        "time": request.form["time"],
        "location": request.form["location"],
        "description": request.form["description"],
        "image": request.form["image"],
        "likes": 0,
        "type": request.form["type"]
    }
    data["events"].append(new_event)
    save_events(data)
    return redirect("/")

@app.route("/like/<int:id>")
def like(id):
    data = load_events()
    for e in data["events"]:
        if e["id"] == id:
            e["likes"] += 1
    save_events(data)
    return redirect("/")

@app.route("/delete/<int:id>")
def delete(id):
    if session.get("role") != "admin":
        return "Access Denied"
    data = load_events()
    data["events"] = [e for e in data["events"] if e["id"] != id]
    save_events(data)
    return redirect("/")

@app.route("/search", methods=["POST"])
def search():
    data = load_events()
    query = request.form["query"].lower()
    filtered = [e for e in data["events"] if query in e["name"].lower()]
    return render_template("index.html", events=filtered, user=session["user"], role=session.get("role"))

# Profile Settings Page
@app.route("/settings", methods=["GET", "POST"])
def settings():
    if "user" not in session:
        return redirect("/login")
    users = load_users()
    user = next((u for u in users["users"] if u["username"] == session["user"]), None)
    if request.method == "POST":
        user["password"] = request.form["password"]
        save_users(users)
        return redirect("/")
    return render_template("settings.html", user=user)

# Run the app
if __name__ == "__main__":
    app.run(debug=True)
