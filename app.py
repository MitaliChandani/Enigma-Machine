from flask import Flask, render_template, request

app = Flask(__name__)

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

@app.route("/", methods=["GET", "POST"])
def index():
    result = ""
    if request.method == "POST":
        message = request.form.get("message", "")
        rotor = int(request.form.get("rotor", 1))
        action = request.form.get("action", "encrypt")

        if action == "encrypt":
            result = enigma_encrypt(message, rotor, decrypt=False)
        elif action == "decrypt":
            result = enigma_encrypt(message, rotor, decrypt=True)

    return render_template("index.html", result=result)

if __name__ == "__main__":
    app.run(debug=True)
