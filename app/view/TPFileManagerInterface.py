import os.path
import shutil
import subprocess

from PyQt5.QtWidgets import QWidget, QFileDialog
from qfluentwidgets import InfoBarIcon, FlyoutAnimationType

from app.common.config import cfg, mkdir
from app.resource.Pages.TPFileManager import Ui_TPfileWindow
from app.util.TP_manager import *
from app.util.UI_general_method import *
from app.util.config_modify import resource_path, update_json, read_config_json


class TPFileManagerPageInterface(QWidget, Ui_TPfileWindow):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)

        game_path = cfg.get(cfg.gamePath)
        app_data_path = cfg.get(cfg.dataFolder)
        self.mod_download_path = cfg.get(cfg.modDownloadFolder)
        self.config_path = os.path.join(os.getcwd(), 'AppData', 'config.json')
        self.mod_path = os.path.join(game_path, '..', '..', '..', 'Content', 'Paks', '~mod')

        # 解析的js路径
        self.unpaked_TP_file_path = os.path.join(app_data_path, 'custom_TP_file')
        # 解析的单列表路径
        self.single_tp_file_cache_path = os.path.join(self.unpaked_TP_file_path, 'Single_TP_file_cache')
        # 生成的自定义js路径
        self.saved_TP_file_path = os.path.join(self.unpaked_TP_file_path, 'saved_custom_TP_file', 'ModTpFile.js')

        # 工具路径
        self.tool_path = os.path.join(app_data_path, 'Tools')
        self.unpack_exe_path = os.path.join(self.tool_path, 'UnrealPakTool', 'UnrealPak.exe')
        self.repak_exe_path = os.path.join(self.tool_path, 'rePak', 'repak.exe')

        repak_zip_path = resource_path('AppData/Tools/repak.zip')
        if not os.path.exists(os.path.join(self.tool_path, 'rePak')):
            unzip_file(repak_zip_path, self.tool_path)
        unpak_zip_path = resource_path('AppData/Tools/unPak.zip')
        if not os.path.exists(os.path.join(self.tool_path, 'UnrealPakTool')):
            unzip_file(unpak_zip_path, self.tool_path)

        self.downloadFolder.setHeaderHidden(True)
        self.customTPFolder.setHeaderHidden(True)

        refresh_folder(self.downloadFolder, self.mod_download_path, '.pak')
        refresh_folder(self.customTPFolder, self.single_tp_file_cache_path, '.json')

        self.downloadFolder.itemChanged.connect(self.update_analysis_button_state)
        self.customTPFolder.itemChanged.connect(self.update_confirm_button_state)

        self.selectFolderButton.clicked.connect(self.download_folder_selector)
        self.analysisButton.clicked.connect(self.unpack)
        self.confirmButton.clicked.connect(self.repak)

        self.usageButton.clicked.connect(self.show_how_to_use)

        self.update_confirm_button_state()
        self.update_analysis_button_state()

    def show_how_to_use(self):
        show_flyout(self, InfoBarIcon.INFORMATION, self.tr('Usage'), self.tr('1.Select the folder where the tp file is located\n2.Select the TP file and click "Analysis TP File"\n3.Select the TP content you want to combine\n4.Click Generate Custom TP File, the program will automatically generate a custom TP file in the mod directory（saved_custom_TP_file.pak）'), self.usageButton, FlyoutAnimationType.PULL_UP)

    def update_confirm_button_state(self):
        update_button_state(self.customTPFolder, self.confirmButton)

    def update_analysis_button_state(self):
        update_button_state(self.downloadFolder, self.analysisButton)

    def download_folder_selector(self):
        path = QFileDialog.getExistingDirectory(self, self.tr("Select Folder"), "")
        if path:
            cfg.modDownloadFolder = path
            self.mod_download_path = update_json(self.config_path, "Folders.modDownload", path)
            refresh_folder(self.downloadFolder, path, '.pak')
            self.update_analysis_button_state()

    def unpack(self):
        selected_paths = []
        get_selected_item(self.downloadFolder.invisibleRootItem(), selected_paths)
        if len(selected_paths) == 1:
            for path in selected_paths:
                command = [self.unpack_exe_path, path, "-extract", self.unpaked_TP_file_path]
                result = subprocess.run(command, creationflags=subprocess.CREATE_NO_WINDOW)
                if result.returncode == 0:
                    TP_file = os.path.join(self.unpaked_TP_file_path, 'ModTpFile.js')
                    # It is specially used to handle js files with wrong format.
                    # Please standardize the format of nested dictionaries in the list,
                    # otherwise I have to write special methods to handle them.：<
                    handle_TP_lists(TP_file, self.single_tp_file_cache_path)
                    refresh_folder(self.customTPFolder, self.single_tp_file_cache_path, '.json')
                    self.update_confirm_button_state()
                else:
                    show_info_bar(self, 'error', self.tr('Unpack TP file failed'), '')
        else:
            show_info_bar(self, 'error', self.tr('Something is wrong'), self.tr('Only one TP file can be selected!'))

    def repak(self):
        # repak路径要求
        pack_path = os.path.join(self.unpaked_TP_file_path, 'saved_custom_TP_file', 'Client', 'Content', 'Aki',
                                 'JavaScript', 'Game', 'Manager', 'ModFuncs')
        mkdir(pack_path)
        mkdir(self.single_tp_file_cache_path)
        selected_paths = []
        get_selected_item(self.customTPFolder.invisibleRootItem(), selected_paths)
        json_files = load_json_files(self.single_tp_file_cache_path)
        combine_to_js(json_files, selected_paths, self.saved_TP_file_path)
        try:
            # repak执行路径
            repak_path = os.path.join(self.unpaked_TP_file_path, 'saved_custom_TP_file')
            # 删除的js路径
            need_to_del = os.path.join(repak_path, 'ModTpFile.js')
            # 复制到规定路径
            shutil.copy(self.saved_TP_file_path, pack_path)
            os.remove(need_to_del)
            command = [self.repak_exe_path, 'pack', repak_path]
            result = subprocess.run(command, creationflags=subprocess.CREATE_NO_WINDOW)
            if result.returncode == 0:
                show_info_bar(self, 'success', self.tr('successfully Generated'), '')
                repaked = os.path.join(self.unpaked_TP_file_path, 'saved_custom_TP_file.pak')
                shutil.copy(repaked, self.mod_path)
                shutil.rmtree(self.unpaked_TP_file_path)
        except Exception as e:
            show_info_bar(self, 'error', self.tr('Something is wrong'), f'{e}')
