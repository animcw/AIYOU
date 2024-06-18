import os
import shutil

from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QWidget
from qfluentwidgets import MessageBox

from app.resource.Pages.setting import Ui_settingWindow
from app.util.UI_general_method import *
from app.util.config_modify import config_manager


def clean_cache(self, path):

    for filename in os.listdir(path):
        file_path = os.path.join(path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
            show_info_bar(self, 'success', '删除成功！', '＼(＾O＾)／')
        except Exception as e:
            show_info_bar(self, 'error', f'删除 {file_path} 失败！', f'{e}')


class settingPageInterface(QWidget, Ui_settingWindow):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)

        self.dataFolder = config_manager.get('programSetting', 'data_dir')
        self.cacheFolder = config_manager.get('programSetting', 'cache_dir')
        self.programFolderInfo.setText(self.dataFolder)
        self.cacheFolderInfo.setText(self.cacheFolder)

        self.openFolderButton.clicked.connect(self.open_data_folder)
        self.opencacheFolderButton.clicked.connect(self.open_cache_folder)
        self.cleancacheFolderButton.clicked.connect(self.clean_cache_flyout)

        self.pushIssuesButton.clicked.connect(self.in_build_info)
        self.checkUpdateButton.clicked.connect(self.in_build_info)

    def in_build_info(self):

        show_info_bar(self, 'warning', '正在建设！', '(；・∀・)')

    def open_data_folder(self):

        QDesktopServices.openUrl(QUrl.fromLocalFile(self.dataFolder))

    def open_cache_folder(self):

        QDesktopServices.openUrl(QUrl.fromLocalFile(self.cacheFolder))

    def clean_cache_flyout(self):

        title = '你想好要删除缓存了吗？'
        content = """删除缓存后下次转换需要重新下载游戏客户端文件。"""
        w = MessageBox(title, content, self)
        if w.exec():
            clean_cache(self, self.cacheFolder)
