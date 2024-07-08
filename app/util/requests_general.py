import re
from urllib.parse import parse_qs

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


def find_record(log_file_path):
    # 定义要匹配的模式
    pattern = re.compile(
        r'OpenWebView \[sdkJson: \{"title":"","url":"(https://.*?)","transparent":true,"titlebar":true,"innerbrowser":true,"webAccelerated":true}]')

    with open(log_file_path, 'r', encoding='utf-8') as file:
        for line in file:
            match = pattern.search(line)
            if match:
                return match.group(1)

    return None


def extract_fragment_params(url):
    # 分割URL，提取fragment部分
    fragment = url.split('#')[-1]
    # 解析fragment部分的查询参数
    params = parse_qs(fragment.split('?')[-1])
    # 将参数的值从列表中取出
    extracted_params = {k: v[0] for k, v in params.items()}
    return extracted_params


def fetch_gacha_records(playerId, cardPoolId, cardPoolType, serverId, recordId):
    url = "https://gmserver-api.aki-game2.net/gacha/record/query"
    records = {}

    for cardType in cardPoolType:
        payload = {
            "playerId": playerId,
            "cardPoolId": cardPoolId,
            "cardPoolType": cardType,
            "serverId": serverId,
            "languageCode": "zh-Hans",
            "recordId": recordId
        }

        response = requests.post(url, json=payload, proxies=proxies)
        data = response.json()

        # 反转抽奖记录
        draws = data['data'][::-1]

        # 初始化计数器
        draw_count = 0
        next_four_star_countdown = 10
        next_five_star_countdown = 80
        last_four_star_draw_count = 0
        last_five_star_draw_count = 0

        # 统计数据
        three_star_count = 0
        four_star_count = 0
        five_star_count = 0

        four_star_intervals = []
        five_star_intervals = []
        four_star_names = []
        five_star_names = []

        total_five_star_interval = 0

        # 遍历每一次抽奖记录
        for draw in draws:
            draw_count += 1
            next_four_star_countdown -= 1
            next_five_star_countdown -= 1

            if draw['qualityLevel'] == 3:
                three_star_count += 1

            if draw['qualityLevel'] == 4:
                interval_since_last_four_star = draw_count - last_four_star_draw_count
                four_star_intervals.append((interval_since_last_four_star, draw['name'], draw['qualityLevel']))
                four_star_names.append(draw['name'])
                last_four_star_draw_count = draw_count
                next_four_star_countdown = 10  # 重置四星倒计时
                four_star_count += 1

            if draw['qualityLevel'] == 5:
                interval_since_last_five_star = draw_count - last_five_star_draw_count
                five_star_intervals.append((interval_since_last_five_star, draw['name'], draw['qualityLevel']))
                five_star_names.append(draw['name'])
                last_five_star_draw_count = draw_count
                next_five_star_countdown = 80  # 重置五星倒计时
                five_star_count += 1
                total_five_star_interval += interval_since_last_five_star

        if five_star_count > 0:
            average_five_star_interval = total_five_star_interval / five_star_count
        else:
            average_five_star_interval = 0

        records[cardType] = {
            "three_star_count": three_star_count,
            "four_star_count": four_star_count,
            "five_star_count": five_star_count,
            "four_star_intervals": four_star_intervals,
            "five_star_intervals": five_star_intervals,
            "next_four_star_countdown": next_four_star_countdown,
            "next_five_star_countdown": next_five_star_countdown,
            "average_five_star_interval": average_five_star_interval
        }
    #print(records)
    return records
