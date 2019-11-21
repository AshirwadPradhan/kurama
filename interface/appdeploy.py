from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from pathlib import Path
import os
import subprocess
import redis
from rq import Queue
from task import background_task
import asyncio
import subprocess

app = Flask(__name__)
app.secret_key = b'KURAMA\n\xec]/'
r = redis.Redis()
q = Queue(connection=r)

HOME = str(Path.home())
APP_UPLOAD_FOLDER = os.path.join(HOME, '.kappc')
SERVICES_REQUIRED = []

if not os.path.exists(APP_UPLOAD_FOLDER):
    try:
        cp = subprocess.run('mkdir ' + APP_UPLOAD_FOLDER, shell=True, check=True)
        if cp.returncode == 0:
            print(f'{APP_UPLOAD_FOLDER} App Upload Folder Created')
    except subprocess.CalledProcessError as e:
        print(e.stderr)

app.config['APP_UPLOAD_FOLDER'] = APP_UPLOAD_FOLDER


@app.route('/')
def hello_world():
    return '<h1> Hello Kurama! </h1>'


@app.route('/appupload', methods=['GET'])
def app_upload():
    return render_template('appgzupload.html')


ALLOWED_EXTENSIONS = {'gz'}


def allowed_file(filename):
    # print(filename.rsplit('.', 1)[1].lower())
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/success', methods=['POST'])
def upload_success():
    if request.method == 'POST':

        if 'file' not in request.files:
            flash('No File Part in the request')
            return redirect(url_for('app_upload'))

        file = request.files['file']

        if file.filename == '':
            flash('No App uploaded')
            return redirect(url_for('app_upload'))

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            full_path = os.path.join(app.config['APP_UPLOAD_FOLDER'], filename)
            file.save(full_path)
            # print('APP Successfully saved')

            try:
                # p = subprocess.run(f'mkdir {full_path[:-7]}', shell=True)
                p = subprocess.run(f'tar -C {full_path[:-7]} -xvf {full_path}', shell=True)

            except Exception:
                print('Error while extracting')
                return redirect(url_for('app_upload'))

            full_f = full_path[:-7]
            proc_file = os.path.join(full_f, 'Procfile')
            with open(proc_file, 'r') as p:
                tmp = p.readline()
                p_file = tmp[6:-1]
                print(p_file)
            print(f'Reading python file name {p_file}')
            py_file = os.path.join(full_path[:-7], p_file)
            print(f'Running the {py_file}')
            p = subprocess.Popen(f'python3 {py_file}', shell=True)
            flash(f'App {file.filename} successfully uploaded')
            return redirect(url_for('app_upload'))

    return redirect(url_for('app_upload'))


@app.route('/kcreatepipeline', methods=['GET'])
def create_pipeline():
    return render_template('pipeline.html')


@app.route('/initpipeline', methods=['POST'])
def init_pipeline():
    if request.method == 'POST':
        dbval = request.form.get('db', None)
        jsonval = request.form.get('json', None)
        dashval = request.form.get('dash', None)
        alertval = request.form.get('alert', None)
        if dbval is not None:
            SERVICES_REQUIRED.append(dbval)
        if jsonval is not None:
            SERVICES_REQUIRED.append(jsonval)
        if dashval is not None:
            SERVICES_REQUIRED.append(dashval)
        if alertval is not None:
            SERVICES_REQUIRED.append(alertval)
        # print(dbval, alertval, jsonval, dashval)

    return redirect(url_for('app_upload'))


@app.route('/kstartpipeline', methods=['GET'])
def start_pipeline():
    global SERVICES_REQUIRED
    if len(SERVICES_REQUIRED) == 0:
        return '<h1> Error: Pipeline is not Initialiazed </h1>'
    else:
        jobs = []
        for service in SERVICES_REQUIRED:
            if service == 'dash':
                job = q.enqueue(background_task, 'http://localhost:5001/dashboard')
                jobs.append(job)
            if service == 'json':
                job = q.enqueue(background_task, 'http://localhost:5004/kjson')
                jobs.append(job)
            if service == 'db':
                job = q.enqueue(background_task, 'http://localhost:5003/kpostdb')
                jobs.append(job)
            if service == 'alert':
                job = q.enqueue(background_task, 'http://localhost:5005/kalert')
                jobs.append(job)

        SERVICES_REQUIRED = []
        return '<h1> Pipeline Services has started </h1>'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
