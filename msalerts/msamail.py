import json
import requests
from flask import Flask
from flask_mail import Mail, Message
import time
import os

app = Flask(__name__)

mail_settings = {
    "MAIL_SERVER": 'smtp.gmail.com',
    "MAIL_PORT": 465,
    "MAIL_USE_TLS": False,
    "MAIL_USE_SSL": True,
    "MAIL_USERNAME": os.environ['SENDER_EMAIL'],
    "MAIL_PASSWORD": os.environ['SENDER_PASS']
}

app.config.update(mail_settings)
mail = Mail(app)

@app.route('/kalert', methods=['GET'])
def send_alert():
    while True:
        with requests.get('http://localhost:5002/stream', stream=True) as req:
            buffer = ''
            list_cpu = list()
            for chunk in req.iter_content(chunk_size=1):
                if chunk.endswith(b'\n'):
                    try:
                        t = str(buffer)
                        print(t)
                        column_val = (t.split(' :: '))
                        if column_val is not None:
                            list_cpu.append(float(column_val[6]))
                            if len(list_cpu) == 50:
                                avg_cpu_usage = (sum(list_cpu) / 50)
                                if avg_cpu_usage > 10:
                                    send_alert(f'High CPU Usage: {avg_cpu_usage}')
                        buffer = ''
                    except IndexError:
                        continue
                else:
                    buffer += chunk.decode()
        time.sleep(1)
        # return 'Stream Ended: Refresh to get more data', 200

def send_alert(msg):
    print(msg)
    with app.app_context():
        kmsg = Message(subject='Alerts from Kurama',
                sender=app.config.get('MAIL_USERNAME'),
                recipients=['ash120895@gmail.com', 'h20190043@pilani.bits-pilani.ac.in'],
                body=msg)
    mail.send(kmsg)
    print('Mail sent!!!')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5005)
