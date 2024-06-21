import configparser
import os
import sys

from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QFileDialog
from qfluentwidgets import MessageBox

from app.util.UI_general_method import show_info_bar
from app.util.requests_general import get_version_data


def resource_path(relative_path):
    """获取资源的绝对路径（处理 PyInstaller 打包后的路径问题）"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


class ConfigManager:
    _instance = None
    _config_file = None

    def __new__(cls, *args, **kwargs):

        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def init_config(self, config_file):
        if not self._initialized:
            self.config = configparser.ConfigParser()
            self.config_file = config_file
            self.read_config()
            self._initialized = True

    def read_config(self):
        if os.path.exists(self.config_file):
            self.config.read(self.config_file)
        else:
            raise FileNotFoundError(f"{self.config_file} does not exist.")

    def get(self, section, key):
        return self.config.get(section, key)

    def set(self, section, key, value):
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, key, value)
        with open(self.config_file, 'w', encoding='utf-8') as configfile:
            self.config.write(configfile)

    def get_all(self):

        return {section: dict(self.config.items(section)) for section in self.config.sections()}


def mkdir(path):
    folder = os.path.exists(path)
    if not folder:
        os.makedirs(path)


def create_ini(config_file, sections):
    config = configparser.ConfigParser()
    for section, options in sections.items():
        config[section] = options
    with open(config_file, 'w') as configfile:
        config.write(configfile)


def initialize_config():
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

    config_file = os.path.join(app_data_folder, 'config.ini')

    if not os.path.exists(config_file):
        sections = {
            'gameSetting': {'game_path': '', 'client_version': '', 'is_load_mod': 0, 'full_screen_mode': '',
                            'windows_size_width': '',
                            'windows_size_height': ''},
            'programSetting': {'root_dir': '', 'data_dir': '', 'cache_dir': '',
                               'mod_download_dir': 'C:\\Users',
                               'mod_description_dir': 'https://gitee.com/wxdxyyds/aiyou_-translate/raw/master/modDescription.json'}
        }
        create_ini(config_file, sections)

    config_manager = ConfigManager()
    config_manager.init_config(config_file)
    config_manager.set('programSetting', 'root_dir', current_directory)
    config_manager.set('programSetting', 'data_dir', app_data_folder)
    config_manager.set('programSetting', 'cache_dir', client_cache_folder)


config_manager = ConfigManager()


def check_path(self, section, key, is_game_path):
    path = config_manager.get(section, key)
    if is_game_path:
        if not os.path.isfile(path):
            game_path, _ = QFileDialog.getOpenFileName(self, "选择游戏可执行文件", "", "Executable Files (*.exe)")
            if game_path:
                config_manager.set(section, key, game_path)
                config = configparser.ConfigParser()
                ini_path = os.path.join(game_path, '..', '..', '..', 'Saved', 'Config', 'WindowsNoEditor',
                                        'GameUserSettings.ini')
                config.read(ini_path)

                resolutionsizex = config.getint('/Script/Engine.GameUserSettings', 'resolutionsizex', fallback=None)
                resolutionsizey = config.getint('/Script/Engine.GameUserSettings', 'resolutionsizey', fallback=None)
                fullscreenmode = config.getint('/Script/Engine.GameUserSettings', 'fullscreenmode', fallback=None)

                if resolutionsizex is not None:
                    config_manager.set(section, 'windows_size_width', str(resolutionsizex))
                if resolutionsizey is not None:
                    config_manager.set(section, 'windows_size_height', str(resolutionsizey))
                if fullscreenmode is not None:
                    config_manager.set(section, 'full_screen_mode', str(fullscreenmode))
    else:
        if not os.path.isdir(path):
            path = QFileDialog.getExistingDirectory(self, "选择文件夹", "")
            if path:
                config_manager.set(section, key, path)

    return config_manager.get(section, key)


# create_ini('../../AppData/config.ini', sections)

def check_update(self, is_button_clicked):
    file_path = resource_path('AppData/version')
    current_version = read_version_from_file(file_path)
    version_json = get_version_data()
    online_version = version_json.get('version', '0.0.0')
    version_status = compare_versions(online_version, current_version)
    if not version_status:
        if is_button_clicked:
            show_update_box(self)
        else:
            show_info_bar(self, 'warning', '发现新版本', '请尽快前往更新')
    else:
        show_info_bar(self, 'success', '当前已是最新版本', '')


def read_version_from_file(file_path):
    version = '0.0.0'
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                if line.startswith("version:"):
                    version = line.split(":")[1].strip()
                    break
    except FileNotFoundError:
        print(f"The file {file_path} does not exist.")
    except Exception as e:
        print(f"An error occurred: {e}")

    return version


def show_update_box(self):
    release_url = 'https://github.com/LittleBlackOfKUN/AIYOU/releases'
    w = MessageBox("发现新版本", "点击前往更新~~", self)
    if w.exec():
        QDesktopServices.openUrl(QUrl(release_url))


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
