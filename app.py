from flask import Flask, render_template, request, redirect, session
import json
from datetime import date

app = Flask(__name__)
app.secret_key = "secret123"

# ------------------- Load & Save Events ------------------- #
def load_events():
    with open("events.json", "r") as f:
        return json.load(f)

def save_events(data):
    with open("events.json", "w") as f:
        json.dump(data, f, indent=4)

# ------------------- Load & Save Users ------------------- #
def load_users():
    with open("users.json", "r") as f:
        return json.load(f)

def save_users(data):
    with open("users.json", "w") as f:
        json.dump(data, f, indent=4)

# ------------------- Home / Dashboard ------------------- #
@app.route("/")
def home():
    if "user" not in session:
        return redirect("/login")
    
    all_events = load_events()["events"]
    today_str = date.today().strftime("%Y-%m-%d")
    today_events = [e for e in all_events if e["date"] == today_str]

    return render_template(
        "index.html",
        events=all_events,
        user=session["user"],
        role=session.get("role"),
        today_date=today_str,
        today_events=today_events
    )

# ------------------- Profile Edit ------------------- #
@app.route("/profile", methods=["GET", "POST"])
def profile():
    if "user" not in session:
        return redirect("/login")
    users = load_users()
    current_user = next(u for u in users["users"] if u["username"] == session["user"])
    
    if request.method == "POST":
        current_user["name"] = request.form["name"]
        current_user["branch"] = request.form["branch"]
        current_user["section"] = request.form["section"]
        current_user["photo"] = request.form["photo"]
        save_users(users)
        return redirect("/")
    return render_template("profile.html", user=current_user)

# ------------------- Register ------------------- #
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        users = load_users()
        users["users"].append({
            "username": request.form["username"],
            "password": request.form["password"],
            "role": "student",
            "name": request.form.get("name", ""),
            "branch": request.form.get("branch", ""),
            "section": request.form.get("section", ""),
            "photo": request.form.get("photo", "https://i.pravatar.cc/150?img=3")
        })
        save_users(users)
        return redirect("/login")
    return render_template("register.html")

# ------------------- Login ------------------- #
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        users = load_users()
        for u in users["users"]:
            if u["username"] == request.form["username"] and u["password"] == request.form["password"]:
                session["user"] = u["username"]
                session["role"] = u.get("role", "student")
                return redirect("/")
        return "Invalid credentials"
    return render_template("login.html")

# ------------------- Logout ------------------- #
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# ------------------- Add Event (Admin Only) ------------------- #
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
        "image": request.form["image"],
        "description": request.form["description"],
        "type": request.form.get("type", "event"),
        "likes": 0
    }
    data["events"].append(new_event)
    save_events(data)
    return redirect("/")

# ------------------- Delete Event (Admin Only) ------------------- #
@app.route("/delete/<int:id>")
def delete(id):
    if session.get("role") != "admin":
        return "Access Denied"
    data = load_events()
    data["events"] = [e for e in data["events"] if e["id"] != id]
    save_events(data)
    return redirect("/")

# ------------------- Like Event (All Users) ------------------- #
@app.route("/like/<int:id>")
def like(id):
    data = load_events()
    for e in data["events"]:
        if e["id"] == id:
            e["likes"] += 1
    save_events(data)
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
