import os.path

from PyQt5.QtCore import QSize
from PyQt5.QtGui import QIcon, QColor
from PyQt5.QtWidgets import QApplication
from qfluentwidgets import FluentIcon as FIF
from qfluentwidgets import NavigationItemPosition, MSFluentWindow, SplashScreen

from app.common.config import cfg, fku_pyinstaller, restart_program
from app.common.signal_bus import signalBus
from app.util.config_modify import *
from app.view.gameSetting_interface import gameSettingInterface
from app.view.modManagerInterface import modManagerPageInterface
from app.view.setting_interface import SettingInterface
from app.view.TPFileManagerInterface import TPFileManagerPageInterface


class MainWindow(MSFluentWindow):

    def __init__(self):
        super().__init__()
        fku_pyinstaller()
        initialize_config(self)
        appdata = cfg.get(cfg.dataFolder)
        if not appdata:
            restart_program()
        self.initWindow()

        # TODO: create sub interface
        self.gameSettingInterface = gameSettingInterface(self)
        self.modManagerInterface = modManagerPageInterface(self)
        self.TPFileManagerInterface = TPFileManagerPageInterface(self)
        self.settingInterface = SettingInterface(self)

        self.connectSignalToSlot()

        # add items to navigation interface
        self.initNavigation()

    def connectSignalToSlot(self):
        signalBus.micaEnableChanged.connect(self.setMicaEffectEnabled)

    def initNavigation(self):
        # TODO: add navigation items
        self.addSubInterface(self.gameSettingInterface, FIF.GAME, self.tr('Game'))
        self.addSubInterface(self.modManagerInterface, FIF.DICTIONARY, self.tr('Mod'))
        self.addSubInterface(self.TPFileManagerInterface, FIF.TRAIN, self.tr('TP Files'))
        self.addSubInterface(self.settingInterface, FIF.SETTING, self.tr('Setting'),
                             position=NavigationItemPosition.BOTTOM)

        self.splashScreen.finish()

    def initWindow(self):
        icon = os.path.join(os.path.dirname(__file__), '..', 'resource', 'images', 'ikun-logo.png')
        self.resize(1000, 600)
        self.setMinimumWidth(1000)
        self.setWindowIcon(QIcon(icon))
        self.setWindowTitle('AIYOU')

        self.setCustomBackgroundColor(QColor(240, 244, 249), QColor(32, 32, 32))

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
