import shutil

from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QWidget, QFileDialog
from qfluentwidgets import MessageBox, InfoBarIcon, FlyoutAnimationType

from app.resource.Pages.modManager import Ui_modWindow
from app.util.UI_general_method import *
from app.util.get_path import *
from app.util.mod_manager import *


class modManagerPageInterface(QWidget, Ui_modWindow):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)

        mod_description_path = get_description_path()
        self.mod_description = load_description(mod_description_path)
        self.mod_download_path = get_mod_download_path()
        game_path = get_game_path()
        self.mod_path = os.path.join(game_path, '..', '..', '..', 'Content', 'Paks', '~mod')

        self.downloadFolder.setHeaderHidden(True)
        self.modFolder.setHeaderHidden(True)

        refresh_folder(self.downloadFolder, self.mod_download_path, self.deleteButton, '.pak')
        refresh_folder(self.modFolder, self.mod_path, self.deleteButton, '.pak')

        self.selectDownload.clicked.connect(self.download_folder_selector)
        self.openModFolder.clicked.connect(self.open_mod_folder)
        self.confirmButton.clicked.connect(self.copy_selected_mod)
        self.refreshButton.clicked.connect(self.refresh_all)
        self.deleteButton.clicked.connect(self.delete_mods)

        self.modFolder.itemSelectionChanged.connect(self.show_mod_description_mod_folder)
        self.downloadFolder.itemSelectionChanged.connect(self.show_mod_description_download_folder)

        self.modFolder.itemChanged.connect(self.update_delete_button_state)

        self.update_delete_button_state()

    def update_delete_button_state(self):
        update_button_state(self.modFolder, self.deleteButton)

    def download_folder_selector(self):
        path = QFileDialog.getExistingDirectory(self, "选择文件夹", "")
        if path:
            set_mod_download_path(path)
            refresh_folder(self.downloadFolder, path, self.deleteButton, '.pak')

    def open_mod_folder(self):
        QDesktopServices.openUrl(QUrl.fromLocalFile(self.mod_path))

    def refresh_all(self):
        self.mod_download_path = get_mod_download_path()
        refresh_folder(self.downloadFolder, self.mod_download_path, self.deleteButton, '.pak')
        refresh_folder(self.modFolder, self.mod_path, self.deleteButton, '.pak')
        show_info_bar(self, 'success', '刷新成功！', '＼(＾O＾)／')

    def delete_mods(self):
        title = '你想好要删除选中的mod了吗？'
        content = """删除某些mod会导致部分功能无法使用，甚至导致游戏无法正常运行。"""
        w = MessageBox(title, content, self)
        if w.exec():
            self.delete_selected_mods()

    def copy_selected_mod(self):
        selected_paths = []
        get_selected_item(self.downloadFolder.invisibleRootItem(), selected_paths)
        if selected_paths:
            if self.mod_path:
                for path in selected_paths:
                    try:
                        shutil.copy(path, self.mod_path)
                        show_info_bar(self, 'success', '添加成功！', '快启动游戏看看吧~~')
                    except shutil.Error as e:
                        if "same file" in str(e):
                            show_info_bar(self, 'error', '添加失败！', '存在同名文件(；′⌒`)')
                        else:
                            show_info_bar(self, 'error', '添加失败！', f"无法复制 {path}: {e}")
                    except Exception as e:
                        show_info_bar(self, 'error', '添加失败！', f"无法复制 {path}: {e}")

        refresh_folder(self.modFolder, self.mod_path, self.deleteButton, '.pak')

    def delete_selected_mods(self):
        selected_paths = []
        get_selected_item(self.modFolder.invisibleRootItem(), selected_paths)
        for path in selected_paths:
            try:
                os.remove(path)
                show_info_bar(self, 'success', '删除成功！', '哎呦，你干嘛Σ(°ロ°)')
            except Exception as e:
                show_info_bar(self, 'error', '删除失败！', f"无法删除 {path}: {e}")
        refresh_folder(self.modFolder, self.mod_path, self.deleteButton, '.pak')

    def show_mod_description_mod_folder(self):
        selected_items = self.modFolder.selectedItems()
        if selected_items[0].text(0) in self.mod_description:
            show_flyout(self, InfoBarIcon.INFORMATION, selected_items[0].text(0),
                        self.mod_description[selected_items[0].text(0)], self.modFolder, FlyoutAnimationType.PULL_UP)

    def show_mod_description_download_folder(self):
        selected_items = self.downloadFolder.selectedItems()
        if selected_items[0].text(0) in self.mod_description:
            show_flyout(self, InfoBarIcon.INFORMATION, selected_items[0].text(0),
                        self.mod_description[selected_items[0].text(0)], self.downloadFolder,
                        FlyoutAnimationType.PULL_UP)
