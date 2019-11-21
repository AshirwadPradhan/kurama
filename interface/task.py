import requests


def background_task(service):
    if service is not None:
        req = requests.get(service)
        if req.status_code == 200:
            return 'Stream Ended'
