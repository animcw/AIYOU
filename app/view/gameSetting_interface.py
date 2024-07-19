# coding:utf-8
import os
import subprocess
import threading

import win32con
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QFileDialog
from qfluentwidgets import FluentIcon as FIF, FluentIcon, PrimaryPushSettingCard, InfoBarIcon, \
    FlyoutAnimationType, RangeSettingCard, PushSettingCard
from qfluentwidgets import (SettingCardGroup, SwitchSettingCard, ScrollArea,
                            ComboBoxSettingCard, ExpandLayout, isDarkTheme)

from app.common.config import cfg, check_client_version, restart_program
from app.util.UI_general_method import show_flyout
from app.util.config_modify import resource_path, show_message_box, update_json
from app.util.localstorage import update_all_localstorage
from app.util.startUP_method import send_game_setting, modify_last_login_cuid, parse_shortcut


class gameSettingInterface(ScrollArea):
    """ Setting interface """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.scrollWidget = QWidget()
        self.expandLayout = ExpandLayout(self.scrollWidget)
        self.setObjectName('gameSettingWindow')

        # game startup
        self.startUPGroup = SettingCardGroup(
            self.tr("Start Game"), self.scrollWidget)
        self.startUPCard = PrimaryPushSettingCard(
            text=self.tr("Start Game"),
            icon=FluentIcon.GAME,
            title=self.tr("Start Game"),
            content=self.tr("Let's have some fun!")
        )

        # client version setting
        self.clientSettingGroup = SettingCardGroup(
            self.tr("Client Settings"), self.scrollWidget)
        self.clientVersionCard = ComboBoxSettingCard(
            cfg.clientVersion,
            FIF.GLOBE,
            self.tr('Client Version Switch'),
            self.tr('Set your preferred client version'),
            texts=[self.tr('CN'), self.tr('OS')],
            parent=self.clientSettingGroup
        )
        self.accountSwitchCard = ComboBoxSettingCard(
            cfg.lastLogin,
            FIF.PEOPLE,
            self.tr('Account Switch'),
            self.tr('Choose your preferred account(CN is not supported)'),
            texts=check_client_version()[1],
            parent=self.clientSettingGroup
        )

        self.launcherSettingGroup = SettingCardGroup(self.tr('Startup Settings'), self.scrollWidget)
        self.launcherSelectorCard = PushSettingCard(
            self.tr('Select launcher'),
            FIF.COMMAND_PROMPT,
            self.tr('Launcher Selector'),
            cfg.get(cfg.otherLauncherPath)
        )
        self.launchByOtherCard = SwitchSettingCard(
            FIF.EMBED,
            self.tr('Launch game by other launcher'),
            self.tr(
                "Choose a different launcher to start game,other launcher's setting will override the setting of [Load mods]"),
            configItem=cfg.launchByOther,
            parent=self.launcherSettingGroup
        )
        self.loadModCard = SwitchSettingCard(
            FIF.APPLICATION,
            self.tr('Load mods'),
            self.tr('Using -fileopenlog Commands to load mods'),
            configItem=cfg.isLoadMod,
            parent=self.launcherSettingGroup
        )

        # game-start setting
        self.displaySettingGroup = SettingCardGroup(self.tr('Display Settings'), self.scrollWidget)
        self.unlock120Card = SwitchSettingCard(
            FIF.MARKET,
            self.tr('Unlock 120 FPS'),
            self.tr('Set the frame rate to 120'),
            configItem=cfg.isUnlock120,
            parent=self.displaySettingGroup
        )
        self.screenModeCard = ComboBoxSettingCard(
            cfg.isFull,
            FIF.FIT_PAGE,
            self.tr('Display Mode'),
            self.tr('Set your preferred display mode'),
            texts=[self.tr('Full Screen'), self.tr('Windows')],
            parent=self.displaySettingGroup
        )
        self.resolutionCard = ComboBoxSettingCard(
            cfg.resolution,
            FIF.LAYOUT,
            self.tr('Windowed Resolution'),
            self.tr('Set your preferred Resolution'),
            texts=["1920x1080", "1600x900", "1440x900", "1366x768", "1280x720"],
            parent=self.displaySettingGroup
        )
        self.isCustomResolutionCard = SwitchSettingCard(
            FIF.ZOOM,
            self.tr('Enable custom resolution'),
            self.tr('Choose whether to use a custom resolution'),
            configItem=cfg.isCustomResolution,
            parent=self.displaySettingGroup
        )
        self.customWidthCard = RangeSettingCard(
            cfg.customWidth,
            FIF.MINIMIZE,
            title=self.tr("Custom Width"),
            content=self.tr("Minimum is 200 and maximum is the current screen width")
        )
        self.customHeightCard = RangeSettingCard(
            cfg.customHeight,
            FIF.MINIMIZE,
            title=self.tr("Custom Height"),
            content=self.tr("Minimum is 200 and maximum is the current screen height")
        )
        self.__initWidget()

    def otherLauncherSelector(self):
        app_data_folder = cfg.get(cfg.dataFolder)
        show_message_box(self.tr('No Other Launcher Executable File Selected'),
                         self.tr('Please Select Executable File'),
                         win32con.MB_ICONINFORMATION)
        otherLauncher_path, _ = QFileDialog.getOpenFileName(self,
                                                            self.tr("Select Other Launcher Executable File"),
                                                            "",
                                                            self.tr("Executable Files (*.exe)"))
        if otherLauncher_path:
            update_json(os.path.join(app_data_folder, "config.json"), "GameSetting.otherLauncherPath",
                        otherLauncher_path)
            show_message_box(self.tr('Launcher Set'),
                             self.tr('Need restart AIYOU to apply changes\nClick confirm or close this to restart'),
                             win32con.MB_ICONINFORMATION)
            restart_program()
        else:
            show_message_box('No game executable file selected', 'Program is about to exit', win32con.MB_ICONERROR)

    def run_game(self):
        try:
            command_dir, command = send_game_setting()
            if command_dir and command:
                os.chdir(command_dir)
                if command.endswith('.lnk'):
                    target_path, arguments = parse_shortcut(command)
                    subprocess.run([target_path] + arguments.split())
                else:
                    subprocess.run(command)
            else:
                show_message_box(self.tr("Start Failed"),
                                 self.tr("Read start-up setting failed,Received None type"),
                                 win32con.MB_ICONERROR)
        except Exception as e:
            show_message_box('Error', f'{e}', win32con.MB_ICONERROR)

    def run_launcherSelector(self):
        thread = threading.Thread(target=self.otherLauncherSelector)
        thread.start()

    def launch_game(self):
        show_flyout(self, InfoBarIcon.INFORMATION, self.tr("Starting"), self.tr("It's playtime"),
                    self.startUPCard,
                    FlyoutAnimationType.PULL_UP)
        thread = threading.Thread(target=self.run_game)
        thread.start()

    def apply_clientSwitch(self):
        self.__initAccountVisual()

    def apply_account(self):
        account = str(cfg.get(cfg.lastLogin))
        modify_last_login_cuid(account)

    def apply_120hz(self):
        if cfg.get(cfg.isUnlock120):
            update_all_localstorage(120, 'KeyCustomFrameRate')
        else:
            update_all_localstorage(60, 'KeyCustomFrameRate')

    def apply_screenMode(self):
        screenMode = str(cfg.get(cfg.isFull))
        self.__initEnableCustomResolutionVisual()
        self.__initResolutionVisual()
        self.__initPresetResolutionVisual()
        self.__initCustomResolutionVisual()
        update_all_localstorage(int(screenMode), 'KeyPcWindowMode')
        # change_game_ini('fullscreenmode', screenMode)

    def apply_resolution(self):
        if not cfg.get(cfg.isCustomResolution):
            width = cfg.get(cfg.resolution.value).split("x")[0]
            height = cfg.get(cfg.resolution.value).split("x")[1]
        else:
            width = cfg.get(cfg.customWidth)
            height = cfg.get(cfg.customHeight)
        update_all_localstorage(int(width), 'KeyPcResolutionWidth')
        update_all_localstorage(int(height), 'KeyPcResolutionHeight')
        # change_game_ini('resolutionsizex', width)
        # change_game_ini('resolutionsizey', height)

    def __initResolutionVisual(self):
        screenMode = cfg.get(cfg.isFull)
        if screenMode == 1:
            self.resolutionCard.setEnabled(False)
        else:
            self.resolutionCard.setEnabled(True)

    def __initAccountVisual(self):
        client_version = cfg.get(cfg.clientVersion)
        if client_version == 1:
            self.accountSwitchCard.setEnabled(False)
        else:
            self.accountSwitchCard.setEnabled(True)

    def __initEnableCustomResolutionVisual(self):
        if cfg.get(cfg.isFull) == 1:
            self.isCustomResolutionCard.setEnabled(False)
        else:
            self.isCustomResolutionCard.setEnabled(True)

    def __initPresetResolutionVisual(self):
        if not cfg.get(cfg.isCustomResolution):
            self.resolutionCard.setEnabled(True)
        else:
            self.resolutionCard.setEnabled(False)

    def __initCustomResolutionVisual(self):
        if cfg.get(cfg.isCustomResolution) and not cfg.get(cfg.isFull) == 1:
            self.customWidthCard.setEnabled(True)
            self.customHeightCard.setEnabled(True)
        else:
            self.customWidthCard.setEnabled(False)
            self.customHeightCard.setEnabled(False)

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
        self.__initAccountVisual()
        self.__initResolutionVisual()
        self.__initEnableCustomResolutionVisual()
        self.__initCustomResolutionVisual()

    def __initLayout(self):
        # add cards to group
        self.startUPGroup.addSettingCard(self.startUPCard)

        self.clientSettingGroup.addSettingCard(self.clientVersionCard)
        self.clientSettingGroup.addSettingCard(self.accountSwitchCard)

        self.launcherSettingGroup.addSettingCard(self.launcherSelectorCard)
        self.launcherSettingGroup.addSettingCard(self.launchByOtherCard)
        self.launcherSettingGroup.addSettingCard(self.loadModCard)

        self.displaySettingGroup.addSettingCard(self.unlock120Card)
        self.displaySettingGroup.addSettingCard(self.screenModeCard)
        self.displaySettingGroup.addSettingCard(self.isCustomResolutionCard)
        self.displaySettingGroup.addSettingCard(self.resolutionCard)
        self.displaySettingGroup.addSettingCard(self.customWidthCard)
        self.displaySettingGroup.addSettingCard(self.customHeightCard)

        # add setting card group to layout
        self.expandLayout.setSpacing(28)
        self.expandLayout.setContentsMargins(60, 10, 60, 0)
        self.expandLayout.addWidget(self.startUPGroup)
        self.expandLayout.addWidget(self.clientSettingGroup)
        self.expandLayout.addWidget(self.launcherSettingGroup)
        self.expandLayout.addWidget(self.displaySettingGroup)

    def __setQss(self):
        """ set style sheet """
        self.scrollWidget.setObjectName('scrollWidget')

        theme = 'dark' if isDarkTheme() else 'light'
        with open(resource_path(f'app/resource/qss/{theme}/setting_interface.qss'), encoding='utf-8') as f:
            self.setStyleSheet(f.read())

    def __connectSignalToSlot(self):
        self.startUPCard.clicked.connect(self.launch_game)
        self.launcherSelectorCard.clicked.connect(self.run_launcherSelector)
        cfg.clientVersion.valueChanged.connect(self.apply_clientSwitch)
        cfg.isUnlock120.valueChanged.connect(self.apply_120hz)
        cfg.lastLogin.valueChanged.connect(self.apply_account)
        cfg.isFull.valueChanged.connect(self.apply_screenMode)
        cfg.resolution.valueChanged.connect(self.apply_resolution)
        cfg.isCustomResolution.valueChanged.connect(self.__initCustomResolutionVisual)
        cfg.isCustomResolution.valueChanged.connect(self.__initPresetResolutionVisual)
        cfg.customWidth.valueChanged.connect(self.apply_resolution)
        cfg.customHeight.valueChanged.connect(self.apply_resolution)
