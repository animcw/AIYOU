# coding:utf-8
import json
import os
import sys
import time
from enum import Enum

from PyQt5.QtCore import QLocale
from pyjsparser.parser import false
from qfluentwidgets import (qconfig, QConfig, ConfigItem, OptionsConfigItem, BoolValidator,
                            OptionsValidator, ConfigSerializer, EnumSerializer)

username = os.getlogin()
os_client_user_cache = fr"C:\Users\{username}\AppData\Roaming\KR_G153"
account_cuid = []
account_email = []

account_json_path = None
json_data = None

config_path = os.path.join(os.getcwd(), 'AppData', 'config.json')


def restart_program():
    """重启当前的程序"""
    try:
        # 获取当前运行的脚本路径
        python = sys.executable
        # 获取当前的脚本名称和参数
        script = os.path.abspath(sys.argv[0])
        args = sys.argv[1:]

        # 延时几秒以确保程序能顺利重启
        time.sleep(2)

        # 重新启动程序
        os.execv(python, [python] + [script] + args)

    except Exception as e:
        print(f"重启程序时出错: {e}")


def mkdir(path):
    folder = os.path.exists(path)
    if not folder:
        os.makedirs(path)


def fku_pyinstaller():
    data = {
        "Folders": {
            "Cache": "",
            "AppData": "",
            "modDownload": "C:\\Users"
        },
        "GameSetting": {
            "ClientVersion": 1,
            "GamePath": "",
            "FullScreenMode": "",
            "isLoadMod": false,
            "lastLogin": "",
            "Resolution": ""
        },
        "MainWindow": {
            "DpiScale": "Auto",
            "Language": "Auto"
        },
        "QFluentWidgets": {
            "ThemeColor": "#ff009faa",
            "ThemeMode": "Light"
        }
    }

    current_directory = os.getcwd()
    app_data_folder = os.path.join(current_directory, 'AppData')
    tool_folder = os.path.join(app_data_folder, 'Tools')
    client_cache_folder = os.path.join(current_directory, 'ServerCache')
    unpaked_TP_file_folder = os.path.join(app_data_folder, 'custom_TP_file')
    single_tp_file_cache_folder = os.path.join(unpaked_TP_file_folder, 'Single_TP_file_cache')
    saved_TP_file_folder = os.path.join(unpaked_TP_file_folder, 'saved_custom_TP_file')

    mkdir(app_data_folder)
    mkdir(client_cache_folder)
    mkdir(tool_folder)
    mkdir(unpaked_TP_file_folder)
    mkdir(single_tp_file_cache_folder)
    mkdir(saved_TP_file_folder)

    config_path = os.path.join(os.getcwd(), 'AppData', 'config.json')

    if not os.path.exists(config_path):
        with open(config_path, "w", encoding="utf-8") as config:
            json.dump(data, config, indent=4)


def read_user_cache_json(folder_path):
    global account_json_path
    global json_data
    account_cuid.clear()
    account_email.clear()
    for root, dirs, files in os.walk(folder_path):
        if 'KRSDKUserCache.json' in files:
            json_path = os.path.join(root, 'KRSDKUserCache.json')
            account_json_path = json_path
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                json_data = data

            account_list = data.get("account_list", [])
            last_login = data.get("last_login_cuid")
            if last_login == "":
                account_cuid.append("")
                account_email.append("")
            for account in account_list:
                cuid = account.get("cuid")
                account_cuid.append(int(cuid))
                loginType = account.get("loginType")
                if str(loginType) == "9":
                    apple_account_num = 0
                    account_email.append(f"Apple-{cuid}")
                    apple_account_num += 1
                elif str(loginType) == "18":
                    google_account_num = 0
                    account_email.append(f"Google-{cuid}")
                    google_account_num += 1
                else:
                    email = account.get("email")
                    account_email.append(email)

            return account_cuid, account_email


def read_config_json(json_file, key_path):
    # 读取 JSON 文件
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 使用 key_path 来访问要修改的项
    keys = key_path.split('.')
    current = data
    for key in keys:
        current = current[key]

    return str(current)


class Language(Enum):
    """ Language enumeration """

    CHINESE_SIMPLIFIED = QLocale(QLocale.Chinese, QLocale.China)
    CHINESE_TRADITIONAL = QLocale(QLocale.Chinese, QLocale.HongKong)
    ENGLISH = QLocale(QLocale.English)
    AUTO = QLocale()


class LanguageSerializer(ConfigSerializer):
    """ Language serializer """

    def serialize(self, language):
        return language.value.name() if language != Language.AUTO else "Auto"

    def deserialize(self, value: str):
        return Language(QLocale(value)) if value != "Auto" else Language.AUTO


class GamePath(Enum):
    if not os.path.exists(config_path):
        fku_pyinstaller()
    game_path = read_config_json(config_path, "GameSetting.GamePath")

    @staticmethod
    def values():
        return [q.value for q in GamePath]


class Resolution(Enum):
    """ Resolution enumeration class """

    Biggest = "1920x1080"
    Bigger = "1600x900"
    Normal = "1440x900"
    Smaller = "1366x768"
    Smallest = "1280x720"

    @staticmethod
    def values():
        return [q.value for q in Resolution]


class Config(QConfig):
    """ Config of application """
    # game
    gamePath = OptionsConfigItem("GameSetting", "GamePath", GamePath, OptionsValidator(GamePath),
                                 EnumSerializer(GamePath))
    clientVersion = OptionsConfigItem("GameSetting", "ClientVersion", 1, OptionsValidator([1, 2]))
    lastLogin = OptionsConfigItem("GameSetting", "lastLogin", "",
                                  OptionsValidator(read_user_cache_json(os_client_user_cache)[0]))
    isLoadMod = ConfigItem("GameSetting", "isLoadMod", False, BoolValidator())
    isFull = OptionsConfigItem("GameSetting", "FullScreenMode", 1, OptionsValidator([1, 2]))
    resolution = OptionsConfigItem("GameSetting", "Resolution", Resolution.Normal, OptionsValidator(Resolution),
                                   EnumSerializer(Resolution))

    # folders
    dataFolder = ConfigItem(
        "Folders", "AppData", "C:\\Users")
    cacheFolder = ConfigItem(
        "Folders", "Cache", "C:\\Users")
    modDownloadFolder = ConfigItem(
        "Folders", "modDownload", "C:\\Users")

    # main window
    dpiScale = OptionsConfigItem(
        "MainWindow", "DpiScale", "Auto", OptionsValidator([1, 1.25, 1.5, 1.75, 2, "Auto"]), restart=True)
    language = OptionsConfigItem(
        "MainWindow", "Language", Language.AUTO, OptionsValidator(Language), LanguageSerializer(), restart=True)


YEAR = 2024
AUTHOR = "RoosterBrother"
VERSION = "0.1.3"
VERSION_CHECK_CHECK = "https://gitee.com/wxdxyyds/aiyou/raw/master/version"
MOD_DESCRIPTION_URL = "https://gitee.com/wxdxyyds/aiyou_-translate/raw/master/modDescription.json"
FEEDBACK_URL = "https://github.com/RoosterBrother/AIYOU"
RELEASE_URL = "https://github.com/RoosterBrother/AIYOU/releases"

cfg = Config()
qconfig.load(os.path.join(os.getcwd(), 'AppData', 'config.json'), cfg)
