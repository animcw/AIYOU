import requests


def load_description(path):
    x = requests.get(path)
    json_result = x.json()
    return json_result
