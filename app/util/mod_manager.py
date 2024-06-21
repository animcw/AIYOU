import requests


def load_description(path):
    try:
        proxies = {
            "http": None,
            "https": None,
        }
        x = requests.get(path, proxies=proxies)
        x.raise_for_status()
        json_result = x.json()
        return json_result
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None

