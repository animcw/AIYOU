import os.path

from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QWidget

from app.resource.Pages.about import Ui_aboutWindow
from app.util.UI_general_method import *


class aboutPageInterface(QWidget, Ui_aboutWindow):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)

        base_path = os.path.dirname(__file__)
        icon_path = os.path.join(base_path, '..', 'resource', 'images', 'icons')
        github_icon = os.path.join(icon_path, 'icons8-github-20.png')
        discord_icon = os.path.join(icon_path, 'icons8-discord-20.png')
        telegram_icon = os.path.join(icon_path, 'icons8-telegram-20.png')
        qq_icon = os.path.join(icon_path, 'icons8-qq-20.png')

        set_icon(self.github, github_icon, 20)
        set_icon(self.discord, discord_icon, 20)

        self.github.clicked.connect(self.open_github)
        self.discord.clicked.connect(self.open_discord)

    def open_github(self):

        QDesktopServices.openUrl(QUrl('https://github.com/Cey1anze'))

    def open_discord(self):

        QDesktopServices.openUrl(QUrl('https://discordapp.com/users/1018192564098191522'))

