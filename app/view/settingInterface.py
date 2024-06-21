import shutil

from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QWidget
from qfluentwidgets import MessageBox

from app.resource.Pages.setting import Ui_settingWindow
from app.util.UI_general_method import *
from app.util.config_modify import check_update, resource_path, read_version_from_file
from app.util.get_path import get_data_path, get_cache_path


class settingPageInterface(QWidget, Ui_settingWindow):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)

        self.dataFolder = get_data_path()
        self.cacheFolder = get_cache_path()
        file_path = resource_path('AppData/version')
        self.version = read_version_from_file(file_path)

        self.programFolderInfo.setText(self.dataFolder)
        self.cacheFolderInfo.setText(self.cacheFolder)
        self.aboutInfo.setText(self.version)

        self.openFolderButton.clicked.connect(self.open_data_folder)
        self.opencacheFolderButton.clicked.connect(self.open_cache_folder)
        self.cleancacheFolderButton.clicked.connect(self.clean_cache_flyout)

        self.pushIssuesButton.clicked.connect(self.open_github_issues)
        self.checkUpdateButton.clicked.connect(self.check_update)

    def check_update(self):
        check_update(self, True)

    def open_github_issues(self):
        github_issues_url = 'https://github.com/LittleBlackOfKUN/AIYOU/issues'
        QDesktopServices.openUrl(QUrl(github_issues_url))

    def open_data_folder(self):
        QDesktopServices.openUrl(QUrl.fromLocalFile(self.dataFolder))

    def open_cache_folder(self):
        QDesktopServices.openUrl(QUrl.fromLocalFile(self.cacheFolder))

    def clean_cache_flyout(self):
        title = '你想好要删除缓存了吗？'
        content = """删除缓存后下次转换需要重新下载游戏客户端文件。"""
        w = MessageBox(title, content, self)
        if w.exec():
            self.clean_cache(self.cacheFolder)

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
