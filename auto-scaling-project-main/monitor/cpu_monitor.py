import psutil
import time
import requests
import os
import subprocess
from datetime import datetime

THRESHOLD = 75
CHECK_INTERVAL = 5
HIGH_CPU_COUNT_REQUIRED = 3
LOW_CPU_COUNT_REQUIRED = 4

PROJECT_DIR = os.path.expanduser("~/autoscale-project")
MODE_FILE = os.path.join(PROJECT_DIR, "traffic_mode.txt")
LOG_FILE = os.path.join(PROJECT_DIR, "logs", "monitor.log")

LOCAL_BACKEND = "127.0.0.1:5000"
CLOUD_BACKEND = "136.110.230.137:80"

NGINX_BACKEND_FILE = "/etc/nginx/conf.d/autoscale_backend.conf"

high_count = 0
low_count = 0


def log(msg):
    line = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")


def write_mode(mode):
    with open(MODE_FILE, "w") as f:
        f.write(mode)


def read_mode():
    if not os.path.exists(MODE_FILE):
        write_mode("LOCAL")
        return "LOCAL"
    with open(MODE_FILE, "r") as f:
        return f.read().strip() or "LOCAL"


def write_nginx_backend(backend_host_port):
    content = f"""upstream autoscale_backend {{
    server {backend_host_port};
}}
"""
    cmd = f"cat <<'EOF' | sudo tee {NGINX_BACKEND_FILE} > /dev/null\n{content}EOF"
    subprocess.run(cmd, shell=True, check=True)


def reload_nginx():
    subprocess.run("sudo nginx -t", shell=True, check=True)
    subprocess.run("sudo systemctl reload nginx", shell=True, check=True)


def switch_to_local():
    write_nginx_backend(LOCAL_BACKEND)
    reload_nginx()
    write_mode("LOCAL")
    log("Switched Nginx routing to LOCAL backend")


def switch_to_cloud():
    write_nginx_backend(CLOUD_BACKEND)
    reload_nginx()
    write_mode("CLOUD")
    log("Switched Nginx routing to CLOUD backend")


def test_cloud():
    try:
        r = requests.get("http://136.110.230.137/health", timeout=5)
        return r.status_code == 200
    except Exception as e:
        log(f"Cloud health check failed: {e}")
        return False


log("CPU monitor started")

# ensure starting state matches mode file
current_mode = read_mode()
if current_mode == "CLOUD":
    try:
        switch_to_cloud()
    except Exception as e:
        log(f"Failed to initialize CLOUD route: {e}")
else:
    try:
        switch_to_local()
    except Exception as e:
        log(f"Failed to initialize LOCAL route: {e}")

while True:
    cpu = psutil.cpu_percent(interval=1)
    current_mode = read_mode()
    log(f"CPU={cpu}% | current_mode={current_mode}")

    if cpu >= THRESHOLD:
        high_count += 1
        low_count = 0
        log(f"High CPU detected count={high_count}")
    else:
        low_count += 1
        high_count = 0
        log(f"Low CPU detected count={low_count}")

    if high_count >= HIGH_CPU_COUNT_REQUIRED and current_mode != "CLOUD":
        log("Threshold crossed consistently. Trying to switch to CLOUD.")
        if test_cloud():
            try:
                switch_to_cloud()
            except Exception as e:
                log(f"Switch to CLOUD failed: {e}")
        else:
            log("Cloud not reachable. Staying on LOCAL.")
        high_count = 0

    if low_count >= LOW_CPU_COUNT_REQUIRED and current_mode != "LOCAL":
        log("CPU normal for long enough. Switching back to LOCAL.")
        try:
            switch_to_local()
        except Exception as e:
            log(f"Switch to LOCAL failed: {e}")
        low_count = 0

    time.sleep(CHECK_INTERVAL)
