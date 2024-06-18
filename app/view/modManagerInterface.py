import os
import shutil

from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QWidget, QTreeWidgetItem, QFileDialog, QTreeWidget
from qfluentwidgets import MessageBox, InfoBar, InfoBarPosition

from app.resource.Pages.modManager import Ui_modWindow
from app.util.config_modify import config_manager
from app.util.UI_general_method import *


class modManagerPageInterface(QWidget, Ui_modWindow):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)

        game_path = config_manager.get('gameSetting', 'game_path')
        self.mod_download_path = config_manager.get('programSetting', 'mod_download_dir')
        self.mod_path = os.path.join(game_path, '..', '..', '..', 'Content', 'Paks', '~mod')

        self.downloadFolder.setHeaderHidden(True)
        self.modFolder.setHeaderHidden(True)

        self.refresh_folder(self.downloadFolder, self.mod_download_path)
        self.refresh_folder(self.modFolder, self.mod_path)

        self.selectDownload.clicked.connect(self.download_folder_selector)
        self.openModFolder.clicked.connect(self.open_mod_folder)
        self.confirmButton.clicked.connect(self.copy_selected_mod)
        self.refreshButton.clicked.connect(self.refresh_all)
        self.deleteButton.clicked.connect(self.delete_mods)

        self.modFolder.itemChanged.connect(self.update_delete_button_state)

        self.update_delete_button_state()

    def download_folder_selector(self):

        path = QFileDialog.getExistingDirectory(self, "选择文件夹", "")
        if path:
            config_manager.set('programSetting', 'mod_download_dir', path)
            self.refresh_folder(self.downloadFolder, path)

    def open_mod_folder(self):

        QDesktopServices.openUrl(QUrl.fromLocalFile(self.mod_path))

    def refresh_all(self):

        self.mod_download_path = config_manager.get('programSetting', 'mod_download_dir')
        self.refresh_folder(self.downloadFolder, self.mod_download_path)
        self.refresh_folder(self.modFolder, self.mod_path)
        show_info_bar(self, 'success', '刷新成功！', '＼(＾O＾)／')

    def select_download_folder(self, path):

        config_manager.set('programSetting', 'mod_download_dir', path)
        self.refresh_folder(self.downloadFolder, self.mod_download_path)

    def delete_mods(self):

        title = '你想好要删除选中的mod了吗？'
        content = """删除某些mod会导致部分功能无法使用，甚至导致游戏无法正常运行。"""
        w = MessageBox(title, content, self)
        if w.exec():
            self.delete_selected_mods()

    def add_tree_items(self, parent, directory):

        parent.clear()
        root_item = QTreeWidgetItem([os.path.basename(directory)])
        root_item.setFlags(root_item.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsTristate)
        root_item.setCheckState(0, Qt.Unchecked)
        root_item.setData(0, Qt.UserRole, directory)
        parent.addTopLevelItem(root_item)
        self.add_subtree_items(root_item, directory)

    def add_subtree_items(self, parent_item, path):

        try:
            items = os.listdir(path)
            items.sort()
            for item in items:
                item_path = os.path.join(path, item)
                if os.path.isfile(item_path) and item.endswith('.pak'):
                    child_item = QTreeWidgetItem([item])
                    child_item.setFlags(child_item.flags() | Qt.ItemIsUserCheckable)
                    child_item.setCheckState(0, Qt.Unchecked)
                    child_item.setData(0, Qt.UserRole, item_path)
                    parent_item.addChild(child_item)
        except PermissionError:
            pass

    def copy_selected_mod(self):

        selected_paths = []
        self.get_selected_mods(self.downloadFolder.invisibleRootItem(), selected_paths)
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

        self.refresh_folder(self.modFolder, self.mod_path)

    def get_selected_mods(self, item, selected_paths):

        for i in range(item.childCount()):
            child = item.child(i)
            if child.checkState(0) in (Qt.Checked, Qt.PartiallyChecked):
                path = child.data(0, Qt.UserRole)
                if path and not os.path.isdir(path):
                    selected_paths.append(path)
            self.get_selected_mods(child, selected_paths)

    def refresh_folder(self, folder, path):

        folder.clear()
        self.add_tree_items(folder, path)
        folder.expandAll()
        self.update_delete_button_state()

    def delete_selected_mods(self):

        selected_paths = []
        self.get_selected_mods(self.modFolder.invisibleRootItem(), selected_paths)
        for path in selected_paths:
            try:
                os.remove(path)
                show_info_bar(self, 'success', '删除成功！', '哎呦，你干嘛Σ(°ロ°)')
            except Exception as e:
                show_info_bar(self, 'error', '删除失败！', f"无法删除 {path}: {e}")
        self.refresh_folder(self.modFolder, self.mod_path)

    def update_delete_button_state(self):

        selected_paths = []
        self.get_selected_mods(self.modFolder.invisibleRootItem(), selected_paths)
        self.deleteButton.setEnabled(bool(selected_paths))
