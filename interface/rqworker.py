import subprocess
import time

while True:
    for _ in range(0, 3):
        p = subprocess.Popen('rq worker', shell=True)

    time.sleep(30)
