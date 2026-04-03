from flask import Flask, render_template, request, redirect, session
import json
from datetime import date

app = Flask(__name__)
app.secret_key = "secret123"

# ------------------- Load & Save Events ------------------- #
def load_events():
    try:
        with open("events.json", "r") as f:
            return json.load(f)
    except:
        return {"events": []}

def save_events(data):
    with open("events.json", "w") as f:
        json.dump(data, f, indent=4)

# ------------------- Load & Save Users ------------------- #
def load_users():
    try:
        with open("users.json", "r") as f:
            return json.load(f)
    except:
        return {"users": []}

def save_users(data):
    with open("users.json", "w") as f:
        json.dump(data, f, indent=4)

# ------------------- Home / Dashboard ------------------- #
@app.route("/")
def home():
    if "user" not in session:
        return redirect("/login")

    all_events = load_events()["events"]
    users_list = load_users()["users"]
    current_user = next((u for u in users_list if u["username"] == session["user"]), None)

    today_str = date.today().strftime("%Y-%m-%d")
    today_events = [e for e in all_events if e["date"] == today_str]

    return render_template(
        "index.html",
        events=all_events,
        user=current_user,
        role=session.get("role"),
        today_date=today_str,
        today_events=today_events
    )

# ------------------- Profile Edit ------------------- #
@app.route("/profile", methods=["GET", "POST"])
def profile():
    if "user" not in session:
        return redirect("/login")

    users_data = load_users()
    current_user = next((u for u in users_data["users"] if u["username"] == session["user"]), None)

    if request.method == "POST":
        current_user["name"] = request.form.get("name", current_user.get("name", ""))
        current_user["branch"] = request.form.get("branch", current_user.get("branch", ""))
        current_user["section"] = request.form.get("section", current_user.get("section", ""))
        current_user["photo"] = request.form.get("photo", current_user.get("photo", "https://i.pravatar.cc/150"))
        save_users(users_data)
        return redirect("/")

    return render_template("profile.html", user=current_user)

# ------------------- Register ------------------- #
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        users_data = load_users()
        users_data["users"].append({
            "username": request.form["username"],
            "password": request.form["password"],
            "role": "student",
            "name": request.form.get("name", ""),
            "branch": request.form.get("branch", ""),
            "section": request.form.get("section", ""),
            "photo": request.form.get("photo", "https://i.pravatar.cc/150")
        })
        save_users(users_data)
        return redirect("/login")
    return render_template("register.html")

# ------------------- Login ------------------- #
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        users_data = load_users()
        for u in users_data["users"]:
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
        "name": request.form.get("name", ""),
        "date": request.form.get("date", ""),
        "time": request.form.get("time", ""),
        "location": request.form.get("location", ""),
        "image": request.form.get("image", "https://via.placeholder.com/300x180"),
        "description": request.form.get("description", ""),
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
