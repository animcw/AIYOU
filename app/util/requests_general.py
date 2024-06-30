import requests

from app.common.config import VERSION_CHECK_CHECK, MOD_DESCRIPTION_URL

proxies = {
    "http": None,
    "https": None,
}


def load_description():
    try:
        x = requests.get(MOD_DESCRIPTION_URL, proxies=proxies)
        x.raise_for_status()
        json_result = x.json()
        return json_result
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None


def get_version_data():
    try:
        response = requests.get(VERSION_CHECK_CHECK, proxies=proxies)

        response.raise_for_status()
        file_content = response.text
        lines = file_content.split('\n')

        data = {}
        for line in lines:
            if line.strip():
                key, value = line.split(':', 1)
                data[key.strip()] = value.strip()

        return data
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return '0.0.0'
