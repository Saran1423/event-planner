from flask import Flask, render_template, request, redirect, session
import json, os, time
from datetime import datetime
from werkzeug.utils import secure_filename
from functools import wraps
from PIL import Image

app = Flask(__name__)
app.secret_key = "secret123"

USERS_FILE = "users.json"
EVENTS_FILE = "events.json"

UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ------------------ HELPERS ------------------

def load_users():
    if not os.path.exists(USERS_FILE):
        save_users({"users": []})
    return json.load(open(USERS_FILE))

def save_users(data):
    json.dump(data, open(USERS_FILE, "w"), indent=4)

def load_events():
    if not os.path.exists(EVENTS_FILE):
        save_events({"events": []})
    return json.load(open(EVENTS_FILE))

def save_events(data):
    json.dump(data, open(EVENTS_FILE, "w"), indent=4)

def to_12hr(time_str):
    if not time_str:
        return ""
    return datetime.strptime(time_str, "%H:%M").strftime("%I:%M %p")

# ------------------ SECURITY DECORATOR ------------------

def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if session.get("role") != "admin":
            return "Access Denied", 403
        return f(*args, **kwargs)
    return wrapper

# ------------------ HOME ------------------

@app.route("/")
def home():
    if "user" not in session:
        return redirect("/login")

    data = load_events()
    users = load_users()["users"]

    current_user = next(
        (u for u in users if u["username"] == session["user"]),
        None
    )

    if not current_user:
        return redirect("/login")

    today = datetime.now().date().isoformat()

    return render_template(
        "index.html",
        events=data["events"],
        user=current_user,
        role=session.get("role"),
        today=today,
        active_page="dashboard"
    )

# ------------------ AUTH ------------------

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        users = load_users()

        if any(u["username"] == request.form["username"] for u in users["users"]):
            return "Username already exists"

        new_user = {
            "username": request.form["username"],
            "password": request.form["password"],
            "role": "student",
            "name": request.form.get("name", ""),
            "branch": request.form.get("branch", ""),
            "section": request.form.get("section", ""),
            "photo": request.form.get("photo", "")
        }

        users["users"].append(new_user)
        save_users(users)

        return redirect("/login")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        users = load_users()["users"]

        # ADMIN LOGIN
        if request.form["username"] == "admin" and request.form["password"] == "admin123":
            session["user"] = "admin"
            session["role"] = "admin"
            return redirect("/")

        # NORMAL USERS
        for u in users:
            if u["username"] == request.form["username"] and \
               u["password"] == request.form["password"]:

                session["user"] = u["username"]
                session["role"] = "student"
                return redirect("/")

        return "Invalid credentials"

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# ------------------ SETTINGS ------------------

@app.route("/settings", methods=["GET", "POST"])
def settings():
    if "user" not in session:
        return redirect("/login")

    users = load_users()
    current_user = next(
        (u for u in users["users"] if u["username"] == session["user"]),
        None
    )

    if not current_user:
        return redirect("/login")

    if request.method == "POST":
        current_user["name"] = request.form.get("name", "")
        current_user["branch"] = request.form.get("branch", "")
        current_user["section"] = request.form.get("section", "")
        current_user["photo"] = request.form.get("photo", "")

        if request.form.get("password"):
            current_user["password"] = request.form["password"]

        save_users(users)
        return redirect("/")

    return render_template("settings.html", user=current_user, active_page="profile")

# ------------------ EVENTS ------------------

@app.route("/add", methods=["POST"])
@admin_required
def add():
    data = load_events()

    new_id = max([e["id"] for e in data["events"]], default=0) + 1

    time_12 = to_12hr(request.form.get("time"))

    file = request.files.get("image")
    image_path = ""

    if file and file.filename:
        filename = str(int(time.time())) + "_" + secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)

        file.save(filepath)

        img = Image.open(filepath)
        img = img.convert("RGB")
        img.thumbnail((800, 800))
        img.save(filepath, optimize=True, quality=85)

        image_path = "/static/uploads/" + filename

    new_event = {
        "id": new_id,
        "name": request.form["name"],
        "date": request.form["date"],
        "time": time_12,
        "location": request.form.get("location", ""),
        "description": request.form.get("description", ""),
        "image": image_path
    }

    data["events"].append(new_event)
    save_events(data)

    return redirect("/")


@app.route("/delete/<int:id>")
@admin_required
def delete(id):
    data = load_events()
    data["events"] = [e for e in data["events"] if e["id"] != id]
    save_events(data)
    return redirect("/")


@app.route("/edit/<int:id>", methods=["POST"])
@admin_required
def edit(id):
    data = load_events()

    for e in data["events"]:
        if e["id"] == id:

            e["name"] = request.form["name"]
            e["date"] = request.form["date"]
            e["time"] = to_12hr(request.form.get("time"))
            e["location"] = request.form.get("location", "")
            e["description"] = request.form.get("description", "")

            file = request.files.get("image")
            if file and file.filename:
                filename = str(int(time.time())) + "_" + secure_filename(file.filename)
                filepath = os.path.join(UPLOAD_FOLDER, filename)

                file.save(filepath)

                img = Image.open(filepath)
                img = img.convert("RGB")
                img.thumbnail((800, 800))
                img.save(filepath, optimize=True, quality=85)

                e["image"] = "/static/uploads/" + filename

    save_events(data)
    return redirect("/")

# ------------------ RUN ------------------

if __name__ == "__main__":
    app.run(debug=True)