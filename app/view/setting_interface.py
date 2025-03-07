# coding:utf-8
import os
import subprocess
import threading

import win32con
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QWidget
from qfluentwidgets import FluentIcon as FIF, MessageBox
from qfluentwidgets import (SettingCardGroup, OptionsSettingCard, PushSettingCard,
                            PrimaryPushSettingCard, ScrollArea,
                            ComboBoxSettingCard, ExpandLayout, Theme, InfoBar, CustomColorSettingCard,
                            setTheme, isDarkTheme)

from app.common.config import cfg, FEEDBACK_URL, AUTHOR, VERSION, YEAR, RELEASE_URL, AUTO_UPDATE_URL
from app.util.UI_general_method import show_info_bar
from app.util.config_modify import resource_path, compare_versions, generate_bat_file, show_message_box
from app.util.requests_general import get_version_data, download_file


class SettingInterface(ScrollArea):
    """ Setting interface """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.scrollWidget = QWidget()
        self.expandLayout = ExpandLayout(self.scrollWidget)
        self.setObjectName('settingWindow')

        # folders
        self.programFolderGroup = SettingCardGroup(
            self.tr("Program Folders"), self.scrollWidget)
        self.dataFolderCard = PushSettingCard(
            self.tr('Open folder'),
            FIF.DOWNLOAD,
            self.tr("AppData Directory"),
            cfg.get(cfg.dataFolder),
            self.programFolderGroup
        )
        self.cacheFolderCard = PushSettingCard(
            self.tr('Open folder'),
            FIF.DOWNLOAD,
            self.tr("Server Cache directory"),
            cfg.get(cfg.cacheFolder),
            self.programFolderGroup
        )

        # personalization
        self.personalGroup = SettingCardGroup(self.tr('Personalization'), self.scrollWidget)
        self.themeCard = OptionsSettingCard(
            cfg.themeMode,
            FIF.BRUSH,
            self.tr('Application theme'),
            self.tr("Change the appearance of your application"),
            texts=[
                self.tr('Light'), self.tr('Dark'),
                self.tr('Use system setting')
            ],
            parent=self.personalGroup
        )
        self.themeColorCard = CustomColorSettingCard(
            cfg.themeColor,
            FIF.PALETTE,
            self.tr('Theme color'),
            self.tr('Change the theme color of you application'),
            self.personalGroup
        )
        self.zoomCard = OptionsSettingCard(
            cfg.dpiScale,
            FIF.ZOOM,
            self.tr("Interface zoom"),
            self.tr("Change the size of widgets and fonts"),
            texts=[
                "100%", "125%", "150%", "175%", "200%",
                self.tr("Use system setting")
            ],
            parent=self.personalGroup
        )
        self.languageCard = ComboBoxSettingCard(
            cfg.language,
            FIF.LANGUAGE,
            self.tr('Language'),
            self.tr('Set your preferred language for UI'),
            texts=['简体中文', '繁體中文', 'English', self.tr('Use system setting')],
            parent=self.personalGroup
        )

        # application
        self.aboutGroup = SettingCardGroup(self.tr('About'), self.scrollWidget)
        self.feedbackCard = PrimaryPushSettingCard(
            self.tr('Provide feedback'),
            FIF.FEEDBACK,
            self.tr('Provide feedback'),
            self.tr('Help us improve AIYOU by providing feedback'),
            self.aboutGroup
        )
        self.aboutCard = PrimaryPushSettingCard(
            self.tr('Check update'),
            FIF.INFO,
            self.tr('About'),
            '© ' + self.tr('Copyright') + f" {YEAR}, {AUTHOR}. " +
            self.tr('Version') + f" {VERSION}",
            self.aboutGroup
        )

        self.__initWidget()

    def __initWidget(self):
        self.resize(800, 600)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setViewportMargins(0, 20, 0, 20)
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)

        # initialize style sheet
        self.__setQss()

        # initialize layout
        self.__initLayout()
        self.__connectSignalToSlot()

    def __initLayout(self):
        # add cards to group
        self.programFolderGroup.addSettingCard(self.dataFolderCard)
        self.programFolderGroup.addSettingCard(self.cacheFolderCard)

        self.personalGroup.addSettingCard(self.themeCard)
        self.personalGroup.addSettingCard(self.themeColorCard)
        self.personalGroup.addSettingCard(self.zoomCard)
        self.personalGroup.addSettingCard(self.languageCard)

        self.aboutGroup.addSettingCard(self.feedbackCard)
        self.aboutGroup.addSettingCard(self.aboutCard)

        # add setting card group to layout
        self.expandLayout.setSpacing(28)
        self.expandLayout.setContentsMargins(60, 10, 60, 0)
        self.expandLayout.addWidget(self.programFolderGroup)
        self.expandLayout.addWidget(self.personalGroup)
        self.expandLayout.addWidget(self.aboutGroup)

    def __setQss(self):
        """ set style sheet """
        self.scrollWidget.setObjectName('scrollWidget')

        theme = 'dark' if isDarkTheme() else 'light'
        with open(resource_path(f'app/resource/qss/{theme}/setting_interface.qss'), encoding='utf-8') as f:
            self.setStyleSheet(f.read())

    def __showRestartTooltip(self):
        """ show restart tooltip """
        InfoBar.warning(
            '',
            self.tr('Configuration takes effect after restart'),
            parent=self.window()
        )

    def __onThemeChanged(self, theme: Theme):
        """ theme changed slot """
        # change the theme
        setTheme(theme)

        # chang the theme of setting interface
        self.__setQss()

    def __connectSignalToSlot(self):
        """ connect signal to slot """
        cfg.appRestartSig.connect(self.__showRestartTooltip)
        cfg.themeChanged.connect(self.__onThemeChanged)

        # folder
        self.dataFolderCard.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl.fromLocalFile(cfg.get(cfg.dataFolder))))
        self.cacheFolderCard.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl.fromLocalFile(cfg.get(cfg.cacheFolder))))

        # about
        self.aboutCard.clicked.connect(self.checkUpdate)
        self.feedbackCard.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl(FEEDBACK_URL)))

    def checkUpdate(self):
        version_json = get_version_data()
        online_version = version_json.get('version', '0.0.0')
        version_status = compare_versions(online_version, VERSION)
        if not version_status:
            show_info_bar(self, 'warning', self.tr('Found new version'), self.tr('Please update ASAP.'))
            self.show_update_box()
        else:
            show_info_bar(self, 'success', self.tr("It is already the latest version"), "")

    def show_update_box(self):
        w = MessageBox(self.tr("Found new version"), self.tr("Click to update ~~"), self)
        if w.exec():
            show_info_bar(self, 'info', self.tr('Trying to auto update'), self.tr('Downloading,please hold on...'))

            def run_update():
                self.run_bat_update(AUTO_UPDATE_URL)

            thread = threading.Thread(target=run_update)
            thread.start()

    def run_bat_update(self, url):
        download_path = 'AIYOU.zip'
        download_file(url, download_path)
        if os.path.exists(download_path):
            generate_bat_file()
            subprocess.Popen(["cmd.exe", "/c", "start", "update.bat"])
        else:
            show_message_box('Error', 'Download Failed', win32con.MB_ICONERROR)
            QDesktopServices.openUrl(QUrl(RELEASE_URL))
