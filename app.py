from flask import Flask, render_template, request, redirect, session
import json

app = Flask(__name__)
app.secret_key = "secret123"

# ------------------- Helper functions ------------------- #
def load_events():
    try:
        with open("events.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"events": []}

def save_events(data):
    with open("events.json", "w") as f:
        json.dump(data, f, indent=4)

def load_users():
    try:
        with open("users.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"users": []}

def save_users(data):
    with open("users.json", "w") as f:
        json.dump(data, f, indent=4)

# ------------------- Home / Dashboard ------------------- #
@app.route("/")
def home():
    if "user" not in session:
        return redirect("/login")
    data = load_events()
    users_data = load_users()
    current_user = next((u for u in users_data["users"] if u["username"] == session["user"]), {})
    return render_template("index.html", events=data["events"], user=current_user, role=session.get("role"))

# ------------------- Register ------------------- #
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        users = load_users()
        # Add new student
        users["users"].append({
            "username": request.form["username"],
            "password": request.form["password"],
            "role": "student",
            "name": request.form.get("name", request.form["username"]),
            "branch": request.form.get("branch", ""),
            "section": request.form.get("section", ""),
            "photo": request.form.get("photo", "https://cdn-icons-png.flaticon.com/512/149/149071.png")
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
    return render_template("login.html")

# ------------------- Logout ------------------- #
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# ------------------- Add Event (Admin) ------------------- #
@app.route("/add", methods=["POST"])
def add():
    if session.get("role") != "admin":
        return "Access Denied"

    data = load_events()
    events = data.get("events", [])
    new_event = {
        "id": (max([e["id"] for e in events]) + 1) if events else 1,
        "name": request.form["name"],
        "date": request.form["date"],
        "time": request.form["time"],
        "location": request.form["location"],
        "image": request.form["image"],
        "description": request.form["description"],
        "likes": 0
    }
    events.append(new_event)
    data["events"] = events
    save_events(data)
    return redirect("/")

# ------------------- Like Event (All users) ------------------- #
@app.route("/like/<int:id>")
def like(id):
    data = load_events()
    for e in data.get("events", []):
        if e["id"] == id:
            e["likes"] += 1
    save_events(data)
    return redirect("/")

# ------------------- Delete Event (Admin) ------------------- #
@app.route("/delete/<int:id>")
def delete(id):
    if session.get("role") != "admin":
        return "Access Denied"

    data = load_events()
    data["events"] = [e for e in data.get("events", []) if e["id"] != id]
    save_events(data)
    return redirect("/")

# ------------------- Profile ------------------- #
@app.route("/profile", methods=["GET", "POST"])
def profile():
    if "user" not in session:
        return redirect("/login")

    users_data = load_users()
    current_user = next((u for u in users_data["users"] if u["username"] == session["user"]), None)

    if request.method == "POST":
        current_user["name"] = request.form.get("name", current_user.get("name",""))
        current_user["branch"] = request.form.get("branch", current_user.get("branch",""))
        current_user["section"] = request.form.get("section", current_user.get("section",""))
        current_user["photo"] = request.form.get("photo", current_user.get("photo",""))
        save_users(users_data)
        return redirect("/profile")

    return render_template("profile.html", user=current_user)

# ------------------- Settings ------------------- #
@app.route("/settings", methods=["GET", "POST"])
def settings():
    if "user" not in session:
        return redirect("/login")

    users_data = load_users()
    current_user = next((u for u in users_data["users"] if u["username"] == session["user"]), None)

    if request.method == "POST":
        current_user["name"] = request.form.get("name", current_user.get("name",""))
        current_user["branch"] = request.form.get("branch", current_user.get("branch",""))
        current_user["section"] = request.form.get("section", current_user.get("section",""))
        current_user["photo"] = request.form.get("photo", current_user.get("photo",""))

        # Change password
        new_password = request.form.get("password", "")
        if new_password.strip():
            current_user["password"] = new_password

        save_users(users_data)
        return redirect("/settings")

    return render_template("settings.html", user=current_user)

# ------------------- Run App ------------------- #
if __name__ == "__main__":
    app.run(debug=True)
