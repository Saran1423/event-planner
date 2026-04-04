from flask import Flask, render_template, request, redirect, session, url_for
import json
import os
import logging

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = "secret123"

# ------------------------------
# JSON Helpers
# ------------------------------
def load_users():
    if not os.path.exists("users.json"):
        default = {
            "users": [
                {
                    "username": "admin",
                    "password": "admin123",
                    "role": "admin",
                    "name": "Admin",
                    "branch": "CSE",
                    "section": "A",
                    "photo": "https://cdn-icons-png.flaticon.com/512/149/149071.png"
                }
            ]
        }
        save_users(default)
    with open("users.json", "r") as f:
        return json.load(f)

def save_users(data):
    with open("users.json", "w") as f:
        json.dump(data, f, indent=4)

def load_events():
    if not os.path.exists("events.json"):
        save_events({"events": []})
    with open("events.json", "r") as f:
        return json.load(f)

def save_events(data):
    with open("events.json", "w") as f:
        json.dump(data, f, indent=4)

# ------------------------------
# Home Dashboard
# ------------------------------
@app.route("/")
def home():
    if "user" not in session:
        return redirect("/login")

    users = load_users()
    current_user = next((u for u in users["users"] if u["username"] == session["user"]), None)
    if not current_user:
        session.clear()
        return redirect("/login")

    events_data = load_events()
    events_list = events_data.get("events", [])
    return render_template("index.html",
                           events=events_list,
                           users=current_user,
                           role=current_user.get("role", "student"))

# ------------------------------
# Register
# ------------------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        users = load_users()
        username = request.form["username"]

        # Check if username exists
        if any(u["username"] == username for u in users["users"]):
            return "Username already exists. Please choose another."

        new_user = {
            "username": username,
            "password": request.form["password"],
            "role": "student",
            "name": request.form.get("name", ""),
            "branch": request.form.get("branch", ""),
            "section": request.form.get("section", ""),
            "photo": request.form.get("photo", "https://cdn-icons-png.flaticon.com/512/149/149071.png")
        }
        users["users"].append(new_user)
        save_users(users)
        return redirect("/login")
    return render_template("register.html")

# ------------------------------
# Login
# ------------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        users = load_users()
        username = request.form["username"]
        password = request.form["password"]

        for u in users["users"]:
            if u["username"] == username and u["password"] == password:
                session["user"] = u["username"]
                session["role"] = u.get("role", "student")
                return redirect("/")
        return "Invalid username or password"
    return render_template("login.html")

# ------------------------------
# Logout
# ------------------------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# ------------------------------
# Add Event (Admin Only)
# ------------------------------
@app.route("/add", methods=["POST"])
def add():
    if session.get("role") != "admin":
        return "Access Denied"

    data = load_events()
    new_event = {
        "id": len(data.get("events", [])) + 1,
        "name": request.form.get("name", "Untitled Event"),
        "date": request.form.get("date", ""),
        "time": request.form.get("time", ""),
        "location": request.form.get("location", ""),
        "description": request.form.get("description", ""),
        "image": request.form.get("image", ""),
        "likes": 0
    }
    data.setdefault("events", []).append(new_event)
    save_events(data)
    return redirect("/")

# ------------------------------
# Delete Event (Admin Only)
# ------------------------------
@app.route("/delete/<int:event_id>")
def delete(event_id):
    if session.get("role") != "admin":
        return "Access Denied"

    data = load_events()
    events = data.get("events", [])
    data["events"] = [e for e in events if e.get("id") != event_id]
    save_events(data)
    return redirect("/")

# ------------------------------
# Profile Settings
# ------------------------------
@app.route("/settings", methods=["GET", "POST"])
def settings():
    if "user" not in session:
        return redirect("/login")

    users = load_users()
    current_user = next((u for u in users["users"] if u["username"] == session["user"]), None)
    if not current_user:
        session.clear()
        return redirect("/login")

    if request.method == "POST":
        current_user["name"] = request.form.get("name", current_user.get("name", ""))
        current_user["branch"] = request.form.get("branch", current_user.get("branch", ""))
        current_user["section"] = request.form.get("section", current_user.get("section", ""))
        current_user["photo"] = request.form.get("photo", current_user.get("photo", "https://cdn-icons-png.flaticon.com/512/149/149071.png"))
        current_user["password"] = request.form.get("password", current_user.get("password", ""))
        save_users(users)
        return redirect("/")

    return render_template("settings.html", user=current_user)

# ------------------------------
# Like Event
# ------------------------------
@app.route("/like/<int:event_id>")
def like(event_id):
    data = load_events()
    for e in data.get("events", []):
        if e.get("id") == event_id:
            e["likes"] += 1
            break
    save_events(data)
    return redirect("/")

# ------------------------------
# Run App
# ------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(debug=True, host="0.0.0.0", port=port)