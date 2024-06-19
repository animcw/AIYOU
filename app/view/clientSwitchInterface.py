import threading

from PyQt5.QtWidgets import QWidget
from qfluentwidgets import InfoBarIcon, FlyoutAnimationType

from app.function.clientSwitch import *
from app.resource.Pages.clientSwitch import Ui_clientSwitchWindow
from app.util.UI_general_method import *
from app.util.config_modify import config_manager


class clientSwitchPageInterface(QWidget, Ui_clientSwitchWindow):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)

        # 设置下拉菜单
        clientItems = ['国服', '国际服']
        isFull = ['全屏', '窗口化']
        windowSize = ['1920x1080', '1600x900', '1440x900', '1366x768', '1280x720']

        self.clientSelect.setPlaceholderText("选择服务器版本")
        self.clientSelect.addItems(clientItems)
        self.clientSelect.setCurrentIndex(-1)

        self.fullScreenSelect.setPlaceholderText("选择显示模式")
        self.fullScreenSelect.addItems(isFull)
        self.fullScreenSelect.setCurrentIndex(-1)

        self.windowSizeSelect.setPlaceholderText("选择窗口大小")
        self.windowSizeSelect.addItems(windowSize)
        self.windowSizeSelect.setCurrentIndex(-1)

        self.gameStartButton.clicked.connect(self.launch_game)
        self.loadSwitchButton.checkedChanged.connect(self.switchLoad)
        self.clientSelect.currentIndexChanged.connect(self.client_version_changed)
        self.fullScreenSelect.currentIndexChanged.connect(self.full_screen_changed)
        self.windowSizeSelect.currentIndexChanged.connect(self.window_size_changed)

        self.load_initial_settings()

    # 初始化界面选项
    def load_initial_settings(self):

        client_version = config_manager.get('gameSetting', 'client_version')
        full_screen_mod = config_manager.get('gameSetting', 'full_screen_mode')
        is_load_mod = config_manager.get('gameSetting', 'is_load_mod')
        windows_size_width = config_manager.get('gameSetting', 'windows_size_width')
        windows_size_height = config_manager.get('gameSetting', 'windows_size_height')

        # 设置下拉菜单的初始状态
        client_version_index = {'cn': 0, 'os': 1}.get(client_version, -1)
        self.clientSelect.setCurrentIndex(client_version_index)

        full_screen_index = int(full_screen_mod)
        self.fullScreenSelect.setCurrentIndex(full_screen_index)

        window_size_text = f"{windows_size_width}x{windows_size_height}"
        window_size_index = self.windowSizeSelect.findText(window_size_text)
        if window_size_index != -1:
            self.windowSizeSelect.setCurrentIndex(window_size_index)

        self.loadSwitchButton.setChecked(is_load_mod == '1')

    def launch_game(self):

        show_flyout(self, InfoBarIcon.SUCCESS, '正在启动', '开始新的一天吧！', self.gameStartButton, FlyoutAnimationType.PULL_UP)
        thread = threading.Thread(target=run_game)
        thread.start()

    def switchLoad(self, isChecked: bool):

        if isChecked:
            config_manager.set('gameSetting', 'is_load_mod', '1')
        else:
            config_manager.set('gameSetting', 'is_load_mod', '0')

    def client_version_changed(self, index):

        version_map = {0: 'cn', 1: 'os'}
        client_version = version_map.get(index)
        config_manager.set('gameSetting', 'client_version', client_version)

    def full_screen_changed(self, index):

        full_screen_mode = str(index)
        config_manager.set('gameSetting', 'full_screen_mode', full_screen_mode)
        if full_screen_mode == '0':
            self.windowSizeSelect.setEnabled(0)
            change_game_ini('FullscreenMode', '1')
        else:
            self.windowSizeSelect.setEnabled(1)
            change_game_ini('FullscreenMode', '2')

    def window_size_changed(self, index):

        window_size = self.windowSizeSelect.itemText(index)
        width, height = window_size.split('x')
        config_manager.set('gameSetting', 'windows_size_width', width)
        config_manager.set('gameSetting', 'windows_size_height', height)
        change_game_ini('resolutionsizex', width)
        change_game_ini('resolutionsizey', height)
