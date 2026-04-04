from flask import Flask, render_template, request, redirect, session
import json
import os

app = Flask(__name__)
app.secret_key = "secret123"

# ------------------------------
# JSON Helpers
# ------------------------------
def load_users():
    if not os.path.exists("users.json"):
        # Create default admin if file missing
        with open("users.json", "w") as f:
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
            json.dump(default, f, indent=4)
    with open("users.json", "r") as f:
        return json.load(f)

def save_users(data):
    with open("users.json", "w") as f:
        json.dump(data, f, indent=4)

def load_events():
    if not os.path.exists("events.json"):
        with open("events.json", "w") as f:
            json.dump({"events": []}, f, indent=4)
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
        return redirect("/login")  # safety check

    events = load_events()
    return render_template("index.html", events=events["events"], user=current_user, role=current_user.get("role", "student"))

# ------------------------------
# Register
# ------------------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        users = load_users()
        new_user = {
            "username": request.form["username"],
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
        for u in users["users"]:
            if u["username"] == request.form["username"] and u["password"] == request.form["password"]:
                session["user"] = u["username"]
                session["role"] = u.get("role", "student")
                return redirect("/")
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
        "id": len(data["events"]) + 1,
        "name": request.form["name"],
        "date": request.form["date"],
        "time": request.form["time"],
        "location": request.form["location"],
        "description": request.form.get("description", ""),
        "image": request.form.get("image", ""),
        "likes": 0
    }
    data["events"].append(new_event)
    save_events(data)
    return redirect("/")

# ------------------------------
# Delete Event (Admin Only)
# ------------------------------
@app.route("/delete/<int:id>")
def delete(id):
    if session.get("role") != "admin":
        return "Access Denied"

    data = load_events()
    data["events"] = [e for e in data["events"] if e["id"] != id]
    save_events(data)
    return redirect("/")

# ------------------------------
# Profile Update
# ------------------------------
@app.route("/settings", methods=["GET", "POST"])
def settings():
    if "user" not in session:
        return redirect("/login")

    users = load_users()
    current_user = next((u for u in users["users"] if u["username"] == session["user"]), None)
    if not current_user:
        return redirect("/login")

    if request.method == "POST":
        current_user["name"] = request.form.get("name", current_user["name"])
        current_user["branch"] = request.form.get("branch", current_user["branch"])
        current_user["section"] = request.form.get("section", current_user["section"])
        current_user["photo"] = request.form.get("photo", current_user["photo"])
        current_user["password"] = request.form.get("password", current_user["password"])
        save_users(users)
        return redirect("/")

    return render_template("settings.html", user=current_user)

# ------------------------------
# Run App
# ------------------------------
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=10000)
