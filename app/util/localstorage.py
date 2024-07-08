import os.path
import sqlite3
import json

from app.common.config import cfg

game_path = cfg.get(cfg.gamePath.value)
localstorage_path = os.path.join(game_path, '..', '..', '..', 'Saved', 'LocalStorage')


def update_all_localstorage(option, key):
    for filename in os.listdir(localstorage_path):
        if filename.startswith("LocalStorage") and filename.endswith(".db"):
            db_file_path = os.path.join(localstorage_path, filename)
            update_game_quality_setting(db_file_path, option, key)


def update_game_quality_setting(file_path, option, key):
    """
    KeyCustomFrameRate
    KeyPcResolutionWidth
    KeyPcResolutionHeight
    """
    conn = sqlite3.connect(file_path)
    cursor = conn.cursor()

    # 查询当前的GameQualitySetting值
    cursor.execute("SELECT value FROM LocalStorage WHERE key='GameQualitySetting'")
    result = cursor.fetchone()

    if result:
        game_quality_setting = json.loads(result[0])

        game_quality_setting[key] = option

        updated_value = json.dumps(game_quality_setting)

        # 更新数据库中的值
        cursor.execute("UPDATE LocalStorage SET value=? WHERE key='GameQualitySetting'", (updated_value,))
        conn.commit()

    conn.close()
