from flask import Flask, jsonify
import socket
import os
import time
import math

app = Flask(__name__)

MODE_FILE = os.path.expanduser("~/autoscale-project/traffic_mode.txt")
DEFAULT_MODE = "LOCAL"


def get_mode():
    if not os.path.exists(MODE_FILE):
        with open(MODE_FILE, "w") as f:
            f.write(DEFAULT_MODE)
        return DEFAULT_MODE
    with open(MODE_FILE, "r") as f:
        return f.read().strip() or DEFAULT_MODE


@app.route("/")
def home():
    mode = get_mode()
    hostname = socket.gethostname()

    if mode == "CLOUD":
        return jsonify({
            "message": "Local VM detected high CPU. Use GCP Load Balancer now.",
            "current_mode": mode,
            "local_vm_hostname": hostname
        })
    else:
        return jsonify({
            "message": "Application is running on LOCAL Debian VM",
            "current_mode": mode,
            "local_vm_hostname": hostname
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
    return jsonify({"status": "local cpu burn completed", "value": x})


@app.route("/mode")
def mode():
    return jsonify({"current_mode": get_mode()})


@app.route("/set-mode/<mode>")
def set_mode(mode):
    mode = mode.upper()
    if mode not in ["LOCAL", "CLOUD"]:
        return jsonify({"error": "mode must be LOCAL or CLOUD"}), 400
    with open(MODE_FILE, "w") as f:
        f.write(mode)
    return jsonify({"status": "updated", "new_mode": mode})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
