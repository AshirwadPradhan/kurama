import psycopg2
import requests
from flask import Flask
import time

app = Flask(__name__)

pg_conn = psycopg2.connect(dbname='test_kurama', user='postgres', password='postgres')
curr = pg_conn.cursor()

query = "INSERT INTO klogging (stamp, log_level, req_type, req_url, status_code, uuid, cpu, disk, swap, " \
        "virtual) VALUES (%s, %s,  %s,  %s, %s, %s, %s, %s, %s, %s) "


@app.route('/kpostdb', methods=['GET'])
def post_db():
    with requests.get('http://localhost:5002/stream', stream=True) as req:
        buffer = ''
        for chunk in req.iter_content(chunk_size=1):
            time.sleep(0.8)
            if chunk.endswith(b'\n'):
                try:
                    t = str(buffer)
                    print(t)
                    column_val = (t.split(' :: '))
                    # print(column_val)
                    # print(column_val[6])
                    if column_val is not None:
                        curr.execute(query, (
                            column_val[0], column_val[1], column_val[2], column_val[3], column_val[4], column_val[5],
                            column_val[6], column_val[7], column_val[8], column_val[9]))
                        pg_conn.commit()
                    buffer = ''
                except IndexError:
                    continue

            else:
                buffer += chunk.decode()

    return 'Stream Ended: Refresh to get more data', 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5003)
