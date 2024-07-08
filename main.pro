SOURCES += app/view/main_window.py \
        app/view/setting_interface.py \
        app/view/gameSetting_interface.py \
        app/view/modManagerInterface.py \
        app/view/TPFileManagerInterface.py \
        app/view/gachaHistoryInterface.py \
        app/util/config_modify.py

FORMS += app/resource/Pages/modManager.ui \
        app/resource/Pages/TPFileManager.ui \
        app/resource/Pages/gachaHistory.ui

TRANSLATIONS = app/resource/i18n/app.zh_CN.ts \
                app/resource/i18n/app.zh_HK.ts
