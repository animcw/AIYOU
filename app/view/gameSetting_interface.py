# coding:utf-8
import configparser
import json
import os.path
import subprocess
import threading

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget
from qfluentwidgets import FluentIcon as FIF, FluentIcon, PrimaryPushSettingCard, InfoBarIcon, \
    FlyoutAnimationType, RangeSettingCard
from qfluentwidgets import (SettingCardGroup, SwitchSettingCard, ScrollArea,
                            ComboBoxSettingCard, ExpandLayout, isDarkTheme)

from app.common.config import cfg, check_client_version
from app.util.UI_general_method import show_flyout
from app.util.config_modify import resource_path
from app.util.localstorage import update_all_localstorage


def send_game_setting():
    game_path = cfg.get(cfg.gamePath.value)
    is_load_mod = cfg.get(cfg.isLoadMod)
    args = " -fileopenlog"

    command = game_path + args

    if is_load_mod:
        return command
    else:
        return game_path


def change_game_ini(option, value):
    section = '/Script/Engine.GameUserSettings'
    game_path = cfg.get(cfg.gamePath.value)
    ini_path = os.path.join(game_path, '..', '..', '..', 'Saved', 'Config', 'WindowsNoEditor',
                            'GameUserSettings.ini')
    config = configparser.ConfigParser()
    config.read(ini_path)

    if section in config:
        config.set(section, option, value)

        with open(ini_path, 'w', encoding='utf-8') as configfile:
            config.write(configfile)


def modify_last_login_cuid(new_cuid):
    username = os.getlogin()
    os_account_path = fr"C:\Users\{username}\AppData\Roaming\KR_G153"
    if os.path.exists(os_account_path):
        for root, dirs, files in os.walk(os_account_path):
            if 'KRSDKUserCache.json' in files:
                path = os.path.join(root, 'KRSDKUserCache.json')
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                if 'last_login_cuid' in data:
                    data['last_login_cuid'] = new_cuid

                with open(path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)


def run_game():
    command = send_game_setting()
    subprocess.run(command)


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

        # game-start setting
        self.startupSettingGroup = SettingCardGroup(self.tr('Startup Settings'), self.scrollWidget)
        self.loadModCard = SwitchSettingCard(
            FIF.APPLICATION,
            self.tr('Load mods when the game starts'),
            self.tr('Using -fileopenlog Commands to load mods'),
            configItem=cfg.isLoadMod,
            parent=self.startupSettingGroup
        )
        self.unlock120Card = SwitchSettingCard(
            FIF.MARKET,
            self.tr('Unlock 120 FPS'),
            self.tr('Set the frame rate to 120'),
            configItem=cfg.isUnlock120,
            parent=self.startupSettingGroup
        )
        self.screenModeCard = ComboBoxSettingCard(
            cfg.isFull,
            FIF.FIT_PAGE,
            self.tr('Display Mode'),
            self.tr('Set your preferred display mode'),
            texts=[self.tr('Full Screen'), self.tr('Windows')],
            parent=self.startupSettingGroup
        )
        self.resolutionCard = ComboBoxSettingCard(
            cfg.resolution,
            FIF.LAYOUT,
            self.tr('Windowed Resolution'),
            self.tr('Set your preferred Resolution'),
            texts=["1920x1080", "1600x900", "1440x900", "1366x768", "1280x720"],
            parent=self.startupSettingGroup
        )
        self.isCustomResolutionCard = SwitchSettingCard(
            FIF.ZOOM,
            self.tr('Enable custom resolution'),
            self.tr('Choose whether to use a custom resolution'),
            configItem=cfg.isCustomResolution,
            parent=self.startupSettingGroup
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

    def launch_game(self):
        show_flyout(self, InfoBarIcon.SUCCESS, self.tr("Start Successful!"), self.tr("It's playtime"), self.startUPCard,
                    FlyoutAnimationType.PULL_UP)
        thread = threading.Thread(target=run_game)
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

        self.startupSettingGroup.addSettingCard(self.loadModCard)
        self.startupSettingGroup.addSettingCard(self.unlock120Card)
        self.startupSettingGroup.addSettingCard(self.screenModeCard)
        self.startupSettingGroup.addSettingCard(self.isCustomResolutionCard)
        self.startupSettingGroup.addSettingCard(self.resolutionCard)
        self.startupSettingGroup.addSettingCard(self.customWidthCard)
        self.startupSettingGroup.addSettingCard(self.customHeightCard)

        # add setting card group to layout
        self.expandLayout.setSpacing(28)
        self.expandLayout.setContentsMargins(60, 10, 60, 0)
        self.expandLayout.addWidget(self.startUPGroup)
        self.expandLayout.addWidget(self.clientSettingGroup)
        self.expandLayout.addWidget(self.startupSettingGroup)

    def __setQss(self):
        """ set style sheet """
        self.scrollWidget.setObjectName('scrollWidget')

        theme = 'dark' if isDarkTheme() else 'light'
        with open(resource_path(f'app/resource/qss/{theme}/setting_interface.qss'), encoding='utf-8') as f:
            self.setStyleSheet(f.read())

    def __connectSignalToSlot(self):
        self.startUPCard.clicked.connect(self.launch_game)
        cfg.clientVersion.valueChanged.connect(self.apply_clientSwitch)
        cfg.isUnlock120.valueChanged.connect(self.apply_120hz)
        cfg.lastLogin.valueChanged.connect(self.apply_account)
        cfg.isFull.valueChanged.connect(self.apply_screenMode)
        cfg.resolution.valueChanged.connect(self.apply_resolution)
        cfg.isCustomResolution.valueChanged.connect(self.__initCustomResolutionVisual)
        cfg.isCustomResolution.valueChanged.connect(self.__initPresetResolutionVisual)
        cfg.customWidth.valueChanged.connect(self.apply_resolution)
        cfg.customHeight.valueChanged.connect(self.apply_resolution)

