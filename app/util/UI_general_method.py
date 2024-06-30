import os

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QTreeWidgetItem
from qfluentwidgets import InfoBar, InfoBarPosition, Flyout


def show_info_bar(window, info_type, title, info):
    """
    :param window: 窗口
    :param info_type: success,warning,error
    :param title: 标题
    :param info: 内容
    """
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
    """
    :param self: 窗口
    :param icon: 显示的图标（InfoBarIcon）
    :param title: 标题
    :param content: 内容
    :param target: 弹窗绑定显示的组件
    :param aniType: 弹窗位置（FlyoutAnimationType）
    """
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


def add_tree_items(parent, directory, file_type):
    parent.clear()
    root_item = QTreeWidgetItem([os.path.basename(directory)])
    root_item.setFlags(root_item.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsTristate)
    root_item.setCheckState(0, Qt.Unchecked)
    root_item.setData(0, Qt.UserRole, directory)
    parent.addTopLevelItem(root_item)
    add_subtree_items(root_item, directory, file_type)


def add_subtree_items(parent_item, path, file_type):
    try:
        items = os.listdir(path)
        items.sort()
        for item in items:
            item_path = os.path.join(path, item)
            if os.path.isfile(item_path) and item.endswith(file_type):
                child_item = QTreeWidgetItem([item])
                child_item.setFlags(child_item.flags() | Qt.ItemIsUserCheckable)
                child_item.setCheckState(0, Qt.Unchecked)
                child_item.setData(0, Qt.UserRole, item_path)
                parent_item.addChild(child_item)
    except PermissionError:
        pass


def refresh_folder(folder, path, file_type):
    folder.clear()
    add_tree_items(folder, path, file_type)
    folder.expandAll()


def update_button_state(folder, button):
    selected_paths = []
    get_selected_item(folder.invisibleRootItem(), selected_paths)
    button.setEnabled(bool(selected_paths))


def get_selected_item(item, selected_paths):
    for i in range(item.childCount()):
        child = item.child(i)
        if child.checkState(0) in (Qt.Checked, Qt.PartiallyChecked):
            path = child.data(0, Qt.UserRole)
            if path and not os.path.isdir(path):
                selected_paths.append(path)
        get_selected_item(child, selected_paths)
