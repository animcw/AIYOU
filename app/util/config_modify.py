import configparser
import os

from PyQt5.QtWidgets import QFileDialog


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


def create_ini(config_file, sections):

    config = configparser.ConfigParser()
    for section, options in sections.items():
        config[section] = options
    with open(config_file, 'w') as configfile:
        config.write(configfile)


def initialize_config():

    current_directory = os.getcwd()
    app_data_folder = os.path.join(current_directory, 'AppData')
    client_cache_folder = os.path.join(current_directory, 'ServerCache')

    if not os.path.exists(app_data_folder):
        os.makedirs(app_data_folder)
    if not os.path.exists(client_cache_folder):
        os.makedirs(client_cache_folder)

    config_file = os.path.join(app_data_folder, 'config.ini')

    if not os.path.exists(config_file):
        sections = {
            'gameSetting': {'game_path': '', 'client_version': '', 'is_load_mod': 0, 'full_screen_mode': '',
                            'windows_size_width': '',
                            'windows_size_height': ''},
            'programSetting': {'root_dir': '', 'data_dir': '', 'cache_dir': '', 'mod_download_dir': 'C:\\Users'}
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
                ini_path = os.path.join(game_path, '..', '..', '..', 'Saved', 'Config', 'WindowsNoEditor', 'GameUserSettings.ini')
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
