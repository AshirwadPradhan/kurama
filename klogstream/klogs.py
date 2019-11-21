from flask import Flask, Response, stream_with_context
import os
from pathlib import Path
import time

app = Flask(__name__)

HOME = str(Path.home())
LOGGING_FILE_PATH = os.path.join(HOME, '.klogs')
LOGGING_FILE = os.path.join(LOGGING_FILE_PATH, 'klog.logs')


@app.route('/stream', methods=['GET'])
def k_stream():
    def stream_context():
        with open(LOGGING_FILE, 'r') as f:
            while True:
                line = f.readline()
                if line:
                    yield line
                    time.sleep(0.08)
                else:
                    break
    return Response(stream_with_context(stream_context()))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)
