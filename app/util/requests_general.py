import requests

proxies = {
    "http": None,
    "https": None,
}


def load_description(path):
    try:
        x = requests.get(path, proxies=proxies)
        x.raise_for_status()
        json_result = x.json()
        return json_result
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None


def get_version_data():
    version_txt_url = 'https://gitee.com/wxdxyyds/aiyou/raw/master/version'
    try:
        response = requests.get(version_txt_url, proxies=proxies)

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
        return None
