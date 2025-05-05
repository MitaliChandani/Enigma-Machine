from flask import Flask, render_template, request, send_file, redirect, url_for, session
import os

app = Flask(__name__)
app.secret_key = "your_secret_key"

UPLOAD_FOLDER = "uploads"
RESULT_FILE = os.path.join(UPLOAD_FOLDER, "result.txt")
USER_FILE = "users.txt"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def enigma_encrypt(message, rotor_shift, decrypt=False):
    encrypted = ""
    if decrypt:
        rotor_shift = -rotor_shift
    for char in message.upper():
        if char.isalpha():
            shifted = (ord(char) - ord('A') + rotor_shift) % 26
            encrypted += chr(shifted + ord('A'))
        else:
            encrypted += char
    return encrypted

def read_users():
    if not os.path.exists(USER_FILE):
        return {}
    with open(USER_FILE, "r") as f:
        lines = f.readlines()
    return {line.split(":")[0]: line.strip().split(":")[1] for line in lines}

def save_user(username, password):
    with open(USER_FILE, "a") as f:
        f.write(f"{username}:{password}\n")

@app.route("/", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        users = read_users()
        if username in users:
            return render_template("register.html", error="Username already exists.")
        save_user(username, password)
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        users = read_users()
        if username in users and users[username] == password:
            session["user"] = username
            return redirect(url_for("index"))
        else:
            return render_template("login.html", error="Invalid credentials.")
    return render_template("login.html")

@app.route("/home", methods=["GET", "POST"])
def index():
    if "user" not in session:
        return redirect(url_for("login"))

    result = ""
    if request.method == "POST":
        rotor = int(request.form.get("rotor", 1))
        action = request.form.get("action", "")
        message = request.form.get("message", "").strip()
        uploaded_file = request.files.get("file")

        if uploaded_file and uploaded_file.filename:
            message = uploaded_file.read().decode("utf-8").strip()

        if not message:
            result = "No input text or file content found."
        else:
            if action == "encrypt":
                result = enigma_encrypt(message, rotor, decrypt=False)
            elif action == "decrypt":
                result = enigma_encrypt(message, rotor, decrypt=True)

            with open(RESULT_FILE, "w", encoding="utf-8") as f:
                f.write(result)

    return render_template("index.html", result=result)

@app.route("/download")
def download():
    if "user" not in session:
        return redirect(url_for("login"))
    if not os.path.exists(RESULT_FILE):
        return "No result file to download.", 404
    return send_file(RESULT_FILE, as_attachment=True)

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
