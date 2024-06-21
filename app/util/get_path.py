import os

from app.util.config_modify import config_manager


def get_game_path():
    game_path = config_manager.get('gameSetting', 'game_path')
    return game_path


def get_client_version():
    client_version = config_manager.get('gameSetting', 'client_version')
    return client_version


def set_client_version(version):
    client_version = config_manager.set('gameSetting', 'client_version', version)
    return client_version


def get_load_mod():
    is_load_mod = config_manager.get('gameSetting', 'is_load_mod')
    return is_load_mod


def set_load_mod(is_load):
    is_load_mod = config_manager.set('gameSetting', 'is_load_mod', is_load)
    return is_load_mod


def get_full_screen_mode():
    full_screen_mode = config_manager.get('gameSetting', 'full_screen_mode')
    return full_screen_mode


def set_full_screen_mode(is_full):
    full_screen_mode = config_manager.set('gameSetting', 'full_screen_mode', is_full)
    return full_screen_mode


def get_windows_size_width():
    windows_size_width = config_manager.get('gameSetting', 'windows_size_width')
    return windows_size_width


def set_windows_size_width(width):
    windows_size_width = config_manager.set('gameSetting', 'windows_size_width', width)
    return windows_size_width


def get_windows_size_height():
    windows_size_height = config_manager.get('gameSetting', 'windows_size_height')
    return windows_size_height


def set_windows_size_height(height):
    windows_size_height = config_manager.set('gameSetting', 'windows_size_height', height)
    return windows_size_height


def get_root_path():
    root_path = config_manager.get('programSetting', 'root_dir')
    return root_path


def set_root_path(root):
    root_path = config_manager.set('programSetting', 'root_dir', root)
    return root_path


def get_data_path():
    data_path = os.path.join(get_root_path(), 'AppData')
    return data_path


def set_data_path():
    data_path = config_manager.set('programSetting', 'data_dir', get_data_path())
    return data_path


def get_cache_path():
    cache_path = os.path.join(get_root_path(), 'ServerCache')
    return cache_path


def set_cache_path(cache):
    cache_path = config_manager.set('programSetting', 'data_dir', get_cache_path())
    return cache_path


def get_mod_download_path():
    download_path = config_manager.get('programSetting', 'mod_download_dir')
    return download_path


def set_mod_download_path(download):
    download_path = config_manager.set('programSetting', 'mod_download_dir', download)
    return download_path


def get_description_path():
    description_path = config_manager.get('programSetting', 'mod_description_dir')
    return description_path


def set_description_path(description):
    description_path = config_manager.set('programSetting', 'mod_description_dir', description)
    return description_path
