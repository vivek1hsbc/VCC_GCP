#!/bin/bash
apt update
apt install -y python3-pip

pip3 install flask

cat <<EOF > /home/app.py
from flask import Flask
import os

app = Flask(__name__)

@app.route("/")
def home():
    return f"GCP Instance: {os.uname().nodename}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
EOF

python3 /home/app.py &
