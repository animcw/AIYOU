import shutil

from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QWidget, QFileDialog
from qfluentwidgets import MessageBox, InfoBarIcon, FlyoutAnimationType

from app.common.config import cfg, mkdir
from app.resource.Pages.modManager import Ui_modWindow
from app.util.UI_general_method import *
from app.util.config_modify import update_json
from app.util.requests_general import *


class modManagerPageInterface(QWidget, Ui_modWindow):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)

        self.mod_description = load_description()
        self.config_path = os.path.join(os.getcwd(), 'AppData', 'config.json')
        self.mod_download_path = cfg.get(cfg.modDownloadFolder)
        game_path = cfg.get(cfg.gamePath)
        self.mod_path = os.path.join(game_path, '..', '..', '..', 'Content', 'Paks', '~mod')

        mkdir(self.mod_path)

        self.downloadFolder.setHeaderHidden(True)
        self.modFolder.setHeaderHidden(True)

        refresh_folder(self.downloadFolder, self.mod_download_path, '.pak')
        refresh_folder(self.modFolder, self.mod_path, '.pak')

        self.selectDownload.clicked.connect(self.download_folder_selector)
        self.openModFolder.clicked.connect(self.open_mod_folder)
        self.confirmButton.clicked.connect(self.copy_selected_mod)
        self.deleteButton.clicked.connect(self.delete_mods)
        self.refreshButton.clicked.connect(self.refresh_all)

        self.modFolder.itemSelectionChanged.connect(self.show_mod_description_mod_folder)
        self.downloadFolder.itemSelectionChanged.connect(self.show_mod_description_download_folder)

        self.modFolder.itemChanged.connect(self.update_delete_button_state)
        self.downloadFolder.itemChanged.connect(self.update_add_button_state)

        self.update_add_button_state()
        self.update_delete_button_state()

    def update_delete_button_state(self):
        update_button_state(self.modFolder, self.deleteButton)

    def update_add_button_state(self):
        update_button_state(self.downloadFolder, self.confirmButton)

    def refresh_all(self):
        try:
            refresh_folder(self.downloadFolder, self.mod_download_path, '.pak')
            refresh_folder(self.modFolder, self.mod_path, '.pak')
            self.update_add_button_state()
            self.update_delete_button_state()
            show_info_bar(self, 'success', self.tr('Refresh success!'), '')
        except Exception as e:
            print(e)

    def download_folder_selector(self):
        path = QFileDialog.getExistingDirectory(self, self.tr("Select Folder"), "")
        if path:
            cfg.modDownloadFolder = path
            self.mod_download_path = update_json(self.config_path, "Folders.modDownload", path)
            refresh_folder(self.downloadFolder, path, '.pak')

    def open_mod_folder(self):
        QDesktopServices.openUrl(QUrl.fromLocalFile(self.mod_path))

    def delete_mods(self):
        title = self.tr("Do you want to delete the selected mod?")
        content = self.tr(
            "Deleting some mods will make some functions unavailable, and even cause the game to not run normally.")
        w = MessageBox(title, content, self)
        if w.exec():
            try:
                self.delete_selected_mods()
            except Exception as e:
                print(str(e))

    def copy_selected_mod(self):
        selected_paths = []
        get_selected_item(self.downloadFolder.invisibleRootItem(), selected_paths)
        if selected_paths:
            if self.mod_path:
                for path in selected_paths:
                    try:
                        shutil.copy(path, self.mod_path)
                        show_info_bar(self, 'success', self.tr('Added successfully!'), '')
                    except shutil.Error as e:
                        if "same file" in str(e):
                            show_info_bar(self, 'error', self.tr('Add failed!'),
                                          self.tr('File with same name exists(；′⌒`)'))
                        else:
                            show_info_bar(self, 'error', self.tr('Add failed!'), self.tr(f"Unable to copy {path}: {e}"))
                    except Exception as e:
                        show_info_bar(self, 'error', self.tr('Add failed!'), self.tr(f"Unable to copy {path}: {e}"))

        refresh_folder(self.modFolder, self.mod_path, '.pak')
        self.update_add_button_state()

    def delete_selected_mods(self):
        selected_paths = []
        get_selected_item(self.modFolder.invisibleRootItem(), selected_paths)
        for path in selected_paths:
            try:
                os.remove(path)
                show_info_bar(self, 'success', self.tr('Deleted successfully!'), '')
            except Exception as e:
                show_info_bar(self, 'error', self.tr('Delete failed!'), self.tr(f"Unable to delete {path}: {e}"))
        refresh_folder(self.modFolder, self.mod_path, '.pak')
        self.update_delete_button_state()

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
