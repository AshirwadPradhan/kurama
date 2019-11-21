import json
import requests
from flask import Flask
from pathlib import Path
import os
import subprocess
import time

app = Flask(__name__)

HOME = str(Path.home())
JSON_FILE_PATH = os.path.join(HOME, '.klogsjson')
if not os.path.exists(JSON_FILE_PATH):
    try:
        cp = subprocess.run('mkdir ' + JSON_FILE_PATH, shell=True, check=True)
        if cp.returncode == 0:
            print(f'{JSON_FILE_PATH} Folder Created')
    except subprocess.CalledProcessError as e:
        print(e.stderr)


@app.route('/kjson', methods=['GET'])
def get_json():
    while True:
        with requests.get('http://localhost:5002/stream', stream=True) as req:
            buffer = ''
            for chunk in req.iter_content(chunk_size=1):
                if chunk.endswith(b'\n'):
                    try:
                        t = str(buffer)
                        print(t)
                        json_path = os.path.join(JSON_FILE_PATH, 'klogs.json')
                        with open(json_path, 'a') as handle:
                            json.dump(t + '\n', handle)
                        buffer = ''
                    except IndexError:
                        continue
                else:
                    buffer += chunk.decode()
        time.sleep(0.2)
        # return 'Stream Ended: Refresh to get more data', 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5004)
