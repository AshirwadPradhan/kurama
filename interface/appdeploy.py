from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from pathlib import Path
import os
import redis
from rq import Queue
from task import background_task
import subprocess
import yaml
import datetime

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
            with open('job.sh', 'w') as pp:
                pp.write(f'#!/usr/bin/env bash\npython3 {py_file}')
            # runjob()
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


def calculate_hours(start_time):
    delta_hours = 0
    if start_time != 'None':
        start_time = start_time.split('.')[0]
        tdelta = datetime.datetime.now() - datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
        delta_hours = int(tdelta.total_seconds() / 3600)
    return delta_hours


def calculate_pricing(hours, unit_price):
    return hours * unit_price


def get_instances():   
    servicelist  = ['msdb', 'msdash', 'msalert', 'msjson']
    result = {}
    services = None
    overall_cost = 0
    pricing = {
        'msdb': 0.3,
        'msdash': 0.25,
        'msalert': 0.2,
        'msjson': 0.15,
    }
    with open("servicelist.yaml", 'r') as stream:
        try:
            services = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
    for service, instances in services.items():
        totalhours = 0
        tmp_time = {}
        if service in servicelist:
            instance_count = 0
            for instance in instances:
                # if(str(type(instance))) == "<class 'dict'>":
                instance_count = instance_count + 1
                for key, time in instance.items():
                    hours = calculate_hours(time)
                    totalhours = totalhours + hours
                    tmp_time[key] = hours
            tmp_time['instance_count'] = instance_count
            tmp_time['total_hours'] = totalhours
            tmp_time['unit_price'] = pricing[service]
            cost = calculate_pricing(totalhours, pricing[service])
            tmp_time['total_price'] = cost
            result[service] = tmp_time
            overall_cost = overall_cost + cost
    result['Total'] = dict({'net_total': overall_cost})
    return result
        
        
@app.route('/pricing')
def pricing():    
    service_stats = get_instances()
    print(service_stats)
    return render_template('pricing.html', service_stats=service_stats)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
