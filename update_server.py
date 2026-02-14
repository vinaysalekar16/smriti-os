from flask import Flask
import subprocess

app = Flask(__name__)

@app.route("/update")
def update():
    subprocess.Popen(["/home/vinay/smriti-os/update.sh"])
    return "Updating..."

app.run(host="0.0.0.0", port=5000)
