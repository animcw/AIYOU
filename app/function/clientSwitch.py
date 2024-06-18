import configparser
import os
import subprocess

from app.util.config_modify import config_manager

section = '/Script/Engine.GameUserSettings'


def get_ini_path(base_path):

    new_path = os.path.join(base_path, '..', '..', '..', 'Saved', 'Config', 'WindowsNoEditor', 'GameUserSettings.ini')
    game_ini_path = os.path.normpath(new_path)

    return game_ini_path


def run_game():

    command = send_game_setting()
    subprocess.run(command, check=True)


def change_game_ini(option, value):

    base_path = config_manager.get('gameSetting', 'game_path')
    ini_path = get_ini_path(base_path)
    config = configparser.ConfigParser()
    config.read(ini_path)

    if section in config:
        config.set(section, option, value)

        with open(ini_path, 'w', encoding='utf-8') as configfile:
            config.write(configfile)


def send_game_setting():

    game_path = config_manager.get('gameSetting', 'game_path')
    is_load_mod = int(config_manager.get('gameSetting', 'is_load_mod'))
    args = " -fileopenlog"

    command = game_path + args

    if is_load_mod:
        return command
    else:
        return game_path
