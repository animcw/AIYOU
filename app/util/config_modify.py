import configparser
import json
import os
import sys
import time

import win32api
import win32con
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QFileDialog
from qfluentwidgets import MessageBox

from app.common.config import VERSION, RELEASE_URL, json_data
from app.util.UI_general_method import show_info_bar
from app.util.requests_general import get_version_data


def initialize_config(self):
    """
    update json with program and game settings
    """

    app_data_folder = os.path.join(os.getcwd(), 'AppData')
    client_cache_folder = os.path.join(os.getcwd(), 'ServerCache')
    config_path = os.path.join(app_data_folder, "config.json")

    update_json(config_path, "Folders.AppData", app_data_folder)
    update_json(config_path, "Folders.Cache", client_cache_folder)

    path = read_config_json(config_path, "GameSetting.GamePath")

    def is_specific_file(file_path, directory, filename):
        return os.path.isfile(file_path) and file_path.endswith(filename) and directory in file_path

    while not is_specific_file(path, 'Client-Win64-Shipping', 'Client-Win64-Shipping.exe'):
        show_message_box('No Game Executable File Selected',
                         'Please Select Game Executable File：Client-Win64-Shipping.exe',
                         win32con.MB_ICONINFORMATION)
        game_path, _ = QFileDialog.getOpenFileName(self,
                                                   "Select Game Executable File：Client-Win64-Shipping.exe",
                                                   "",
                                                   "Executable Files (*.exe)")
        if game_path:
            update_json(os.path.join(app_data_folder, "config.json"), "GameSetting.GamePath", game_path)
            path = game_path  # 更新path以便循环条件能正确判断
        else:
            show_message_box('No Game Executable File Selected', 'Program Is About To Exit！', win32con.MB_ICONERROR)
            time.sleep(2)
            sys.exit(0)

    ini_path = os.path.join(path, '..', '..', '..', 'Saved', 'Config', 'WindowsNoEditor', 'GameUserSettings.ini')

    config = configparser.ConfigParser()
    config.read(ini_path)

    resolutionsizex = config.getint('/Script/Engine.GameUserSettings', 'resolutionsizex', fallback=None)
    resolutionsizey = config.getint('/Script/Engine.GameUserSettings', 'resolutionsizey', fallback=None)
    fullscreenmode = config.getint('/Script/Engine.GameUserSettings', 'fullscreenmode', fallback=None)
    account = json_data['last_login_cuid']

    if resolutionsizex is not None and resolutionsizey is not None:
        update_json(config_path,
                    "GameSetting.Resolution",
                    f"{resolutionsizex}x{resolutionsizey}")
    if fullscreenmode is not None:
        update_json(config_path, "GameSetting.FullScreenMode", fullscreenmode)
    if account != "":
        update_json(config_path, "GameSetting.lastLogin", int(account))
    else:
        update_json(config_path, "GameSetting.lastLogin", "")


def resource_path(relative_path):
    """ Get the absolute path to the resource, works for both dev and PyInstaller """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


def read_config_json(json_file, key_path):
    try:
        # 读取 JSON 文件
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 使用 key_path 来访问要修改的项
        keys = key_path.split('.')
        current = data
        for key in keys:
            current = current[key]

        return str(current)

    except FileNotFoundError:
        show_message_box('Error', f'Config file： {json_file} was not found', win32con.MB_ICONERROR)
    except json.JSONDecodeError:
        show_message_box('Error', f'Config Parsing error：{json_file}', win32con.MB_ICONERROR)
    except KeyError:
        show_message_box('Error', f'The key： {key_path} is invalid', win32con.MB_ICONERROR)


def update_json(json_file, key_path, new_value):
    try:
        # 读取 JSON 文件
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 使用 key_path 来访问要修改的项
        keys = key_path.split('.')
        current = data
        for key in keys[:-1]:
            current = current[key]

        # 更新指定的项
        current[keys[-1]] = new_value

        # 将更新后的内容写回 JSON 文件
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    except FileNotFoundError:
        show_message_box('Error', f'Config file： {json_file} was not found', win32con.MB_ICONERROR)
    except json.JSONDecodeError:
        show_message_box('Error', f'Config Parsing error：{json_file}', win32con.MB_ICONERROR)
    except KeyError:
        show_message_box('Error', f'The key： {key_path} is invalid', win32con.MB_ICONERROR)


def show_message_box(title, message, icon):
    win32api.MessageBox(0, message, title, icon)


def checkUpdate(self):
    version_json = get_version_data()
    online_version = version_json.get('version', '0.0.0')
    version_status = compare_versions(online_version, VERSION)
    if not version_status:
        show_info_bar(self, 'warning', '发现新版本', '请尽快前往更新')
        show_update_box(self)
    else:
        show_info_bar(self, 'success', '当前已是最新版本', '')


def show_update_box(self):
    w = MessageBox("发现新版本", "点击前往更新~~", self)
    if w.exec():
        QDesktopServices.openUrl(QUrl(RELEASE_URL))


def compare_versions(version1, version2):
    v1_parts = [int(part) for part in version1.split('.') if part.strip().isdigit()]
    v2_parts = [int(part) for part in version2.split('.') if part.strip().isdigit()]

    max_length = max(len(v1_parts), len(v2_parts))
    v1_parts.extend([0] * (max_length - len(v1_parts)))
    v2_parts.extend([0] * (max_length - len(v2_parts)))

    for v1, v2 in zip(v1_parts, v2_parts):
        if v1 > v2:
            return False
        elif v1 < v2:
            return True

    return True
