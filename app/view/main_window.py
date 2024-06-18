# coding: utf-8
import os.path

from PyQt5.QtCore import QSize
from PyQt5.QtGui import QIcon, QColor
from PyQt5.QtWidgets import QApplication
from qfluentwidgets import FluentIcon as FIF
from qfluentwidgets import NavigationItemPosition, MSFluentWindow, SplashScreen

from app.common.config import cfg
from app.common.signal_bus import signalBus
from app.util.config_modify import check_path
from app.view.aboutInterface import aboutPageInterface
from app.view.clientSwitchInterface import clientSwitchPageInterface
from app.view.modManagerInterface import modManagerPageInterface
from app.view.settingInterface import settingPageInterface


class MainWindow(MSFluentWindow):

    def __init__(self):
        super().__init__()
        self.initWindow()
        check_path(self, 'gameSetting', 'game_path', True)

        # TODO: create sub interface
        # self.homeInterface = HomeInterface(self)
        self.clientSwitchInterface = clientSwitchPageInterface(self)
        self.aboutInterface = aboutPageInterface(self)
        self.modManagerInterface = modManagerPageInterface(self)
        self.settingInterface = settingPageInterface(self)

        self.connectSignalToSlot()

        # add items to navigation interface
        self.initNavigation()

    def connectSignalToSlot(self):
        signalBus.micaEnableChanged.connect(self.setMicaEffectEnabled)

    def initNavigation(self):
        # self.navigationInterface.setAcrylicEnabled(True)

        # TODO: add navigation items
        # self.addSubInterface(self.homeInterface, FIF.HOME, self.tr('Home'))
        self.addSubInterface(self.clientSwitchInterface, FIF.GAME, self.tr('启动设置'))
        self.addSubInterface(self.modManagerInterface, FIF.DICTIONARY, self.tr('Mod管理'))
        self.addSubInterface(self.aboutInterface, FIF.INFO, self.tr('关于'), position=NavigationItemPosition.BOTTOM)

        # add custom widget to bottom
        self.addSubInterface(self.settingInterface, FIF.SETTING, self.tr('设置'), position=NavigationItemPosition.BOTTOM)

        self.splashScreen.finish()

    def initWindow(self):
        icon = os.path.join(os.path.dirname(__file__), '..', 'resource', 'images', 'ikun-logo.png')
        self.resize(900, 600)
        self.setMinimumWidth(900)
        self.setWindowIcon(QIcon(icon))
        self.setWindowTitle('AIYOU')

        self.setCustomBackgroundColor(QColor(240, 244, 249), QColor(32, 32, 32))
        self.setMicaEffectEnabled(cfg.get(cfg.micaEnabled))

        # create splash screen
        self.splashScreen = SplashScreen(self.windowIcon(), self)
        self.splashScreen.setIconSize(QSize(106, 106))
        self.splashScreen.raise_()

        desktop = QApplication.primaryScreen().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)
        self.show()
        QApplication.processEvents()

    def resizeEvent(self, e):
        super().resizeEvent(e)
        if hasattr(self, 'splashScreen'):
            self.splashScreen.resize(self.size())
