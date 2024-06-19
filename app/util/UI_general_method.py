from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon
from qfluentwidgets import InfoBar, InfoBarPosition, Flyout


def show_info_bar(window, info_type, title, info):
    if info_type == 'success':
        InfoBar.success(
            title=title,
            content=info,
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.BOTTOM,
            duration=2000,
            parent=window
        )
    elif info_type == 'warning':
        InfoBar.warning(
            title=title,
            content=info,
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.BOTTOM,
            duration=-1,  # 永不消失
            parent=window
        )
    else:
        InfoBar.error(
            title=title,
            content=info,
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.BOTTOM,
            duration=-1,
            parent=window
        )


def show_flyout(self, icon, title, content, target, aniType):
    Flyout.create(
        icon=icon,
        title=title,
        content=content,
        target=target,
        parent=self,
        isClosable=True,
        aniType=aniType
    )


def set_icon(button, icon, size):
    button.setIcon(QIcon(icon))
    button.setFixedSize(size, size)
    button.setIconSize(QSize(size, size))
