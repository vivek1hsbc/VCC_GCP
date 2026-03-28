#!/bin/bash

apt-get update
apt-get install -y python3 python3-pip

pip3 install flask

mkdir -p /opt/cloudapp

cat <<EOF > /opt/cloudapp/app.py
from flask import Flask, jsonify
import socket
import time
import math

app = Flask(__name__)

@app.route("/")
def home():
    return jsonify({
        "message": "Application is running on GCP cloud instance",
        "cloud_instance_hostname": socket.gethostname()
    })

@app.route("/health")
def health():
    return "OK", 200

@app.route("/cpu-burn")
def cpu_burn():
    start = time.time()
    x = 0.0
    while time.time() - start < 20:
        for i in range(1, 200000):
            x += math.sqrt(i) * math.sin(i)
    return jsonify({"status": "cloud cpu burn completed", "value": x})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
EOF

nohup python3 /opt/cloudapp/app.py > /var/log/cloudapp.log 2>&1 &
