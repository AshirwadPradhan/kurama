import requests
import random
import time

base_api = 'http://localhost:10000/user/'
http_req_list = ['GET', 'POST', 'PUT', 'DEL']
user_names_get = ['Trouble', 'Hell', 'Bobber']
user_names_p = ['Tim', 'Bim', 'Shim']
user_names_del = ['Rim', 'Bim']

while True:
    http_req_type = random.choice(http_req_list)
    if http_req_type == 'GET':
        response = requests.get(base_api + random.choice(user_names_get))
        if response.status_code == 200:
            print('Successful GET')
        else:
            print('Unsuccessful GET')

    if http_req_type == 'POST':
        response = requests.post(base_api + random.choice(user_names_p), data={'age': 40, 'occupation': 'GupChup'})
        if response.status_code == 200:
            print('Successful POST')
        else:
            print('Unsuccessful POST')

    if http_req_type == 'PUT':
        response = requests.put(base_api + random.choice(user_names_p), data={'age': 40, 'occupation': 'GupChup'})
        if response.status_code == 200:
            print('Successful PUT')
        else:
            print('Unsuccessful PUT')

    if http_req_type == 'DEL':
        response = requests.delete(base_api + random.choice(user_names_del))
        if response.status_code == 200:
            print('Successful DELETE')
        else:
            print('Unsuccessful DELETE')

    time.sleep(0.1)
