import json
import os
import shutil

import pythoncom
import win32com.client

from app.common.config import cfg


def send_game_setting():
    """
    选择启动方式
    launchByOther > isLoadMod
    """
    game_path = cfg.get(cfg.gamePath)
    otherLauncher_path = cfg.get(cfg.otherLauncherPath)
    shortcut_path = os.path.join(os.path.dirname(game_path), 'shortcut.lnk')

    launchByOther = cfg.get(cfg.launchByOther)
    is_load_mod = cfg.get(cfg.isLoadMod)

    def checkOtherLauncher():
        if launchByOther and os.path.isfile(otherLauncher_path):
            return os.path.dirname(otherLauncher_path), otherLauncher_path
        return None, None

    # 创建快捷方式
    if os.path.exists(game_path) and not os.path.exists(shortcut_path):
        create_shortcut(game_path)

    # 其他启动器启动且路径正确
    launcher_dir, launcher_path = checkOtherLauncher()
    if launcher_dir and launcher_path:
        edit_d3dx_ini(otherLauncher_path, shortcut_path, game_path)
        return launcher_dir, launcher_path

    # 其他情况
    if launchByOther:
        if is_load_mod:
            return os.path.dirname(shortcut_path), shortcut_path
        else:
            return os.path.dirname(game_path), game_path
    else:
        if is_load_mod:
            return os.path.dirname(shortcut_path), shortcut_path
        else:
            return os.path.dirname(game_path), game_path


def modify_last_login_cuid(new_cuid):
    """
    切换账号
    :param new_cuid: 切换的账号
    """
    username = os.getlogin()
    os_account_path = fr"C:\Users\{username}\AppData\Roaming\KR_G153"
    if os.path.exists(os_account_path):
        for root, dirs, files in os.walk(os_account_path):
            if 'KRSDKUserCache.json' in files:
                path = os.path.join(root, 'KRSDKUserCache.json')
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                if 'last_login_cuid' in data:
                    data['last_login_cuid'] = new_cuid

                with open(path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)


def create_shortcut(target_path):
    """
    创建游戏快捷方式
    :param target_path: 游戏本体路径（cfg.gamePath）
    """
    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut_path = os.path.join(os.path.dirname(target_path), 'shortcut.lnk')
    shortcut = shell.CreateShortcut(shortcut_path)
    shortcut.TargetPath = target_path
    shortcut.Arguments = "-fileopenlog"
    shortcut.WorkingDirectory = os.path.dirname(target_path)
    shortcut.save()


def parse_shortcut(shortcut_path):
    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortcut(shortcut_path)
    target_path = shortcut.TargetPath
    arguments = shortcut.Arguments
    return target_path, arguments


def backup_ini_file(ini_path):
    """
    备份ini
    :param ini_path: ini路径
    """
    backup_path = ini_path + '.bak'
    if not os.path.exists(backup_path):
        shutil.copy(ini_path, backup_path)


def edit_d3dx_ini(otherLauncherPath, shortcut_path, game_path):
    """
    修改WWMI的配置文件
    :param otherLauncherPath: WWMI的路径
    :param shortcut_path: 快捷方式路径
    :param game_path: 游戏路径
    """
    # 只有WWMI才改
    if os.path.basename(otherLauncherPath) == 'WWMI Loader.exe':
        ini_path = os.path.join(os.path.dirname(otherLauncherPath), 'd3dx.ini')
        if os.path.exists(ini_path):
            backup_ini_file(ini_path)

            with open(ini_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()

            in_loader_section = False
            for i, line in enumerate(lines):
                if line.strip().lower() == '[loader]':
                    in_loader_section = True
                elif line.startswith('[') and in_loader_section:
                    in_loader_section = False

                if in_loader_section:
                    if line.startswith('launch'):
                        lines[i] = f'launch = {shortcut_path}\n'
                    elif line.startswith('target'):
                        lines[i] = f'target = {os.path.basename(game_path)}\n'

            with open(ini_path, 'w', encoding='utf-8') as file:
                file.writelines(lines)
