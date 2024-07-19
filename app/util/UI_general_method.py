import json
import os
import shutil
import sys

from PIL import Image, ImageDraw, ImageFont
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QTreeWidgetItem
from qfluentwidgets import InfoBar, InfoBarPosition, Flyout, SubtitleLabel, LineEdit, MessageBoxBase


class CustomMessageBox(MessageBoxBase):
    """ Custom message box """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.titleLabel = SubtitleLabel('')
        self.urlLineEdit = LineEdit()

        self.urlLineEdit.setPlaceholderText('')
        self.urlLineEdit.setClearButtonEnabled(True)

        # 将组件添加到布局中
        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.urlLineEdit)

        # 设置对话框的最小宽度
        self.widget.setMinimumWidth(350)


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
    elif info_type == 'info':
        InfoBar.info(
            title=title,
            content=info,
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.BOTTOM,
            duration=5000,
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


def resource_path(relative_path):
    """ Get the absolute path to the resource, works for both dev and PyInstaller """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


def generate_images(records, cardPoolType):
    font_path = resource_path('app/resource/font/H7GBK-Heavy.ttf')
    list_path = resource_path('app/resource/FiveStarList.json')

    with open(list_path, 'r', encoding='utf-8') as file:
        list = json.load(file)

    for cardType in cardPoolType:
        base_image_path = os.path.join(os.getcwd(), 'AppData', 'gachaImage')
        output_directory = os.path.join(base_image_path, cardPoolType[cardType])
        if os.path.exists(output_directory):
            shutil.rmtree(output_directory)
        os.makedirs(output_directory, exist_ok=True)

        search_paths = [resource_path("app/resource/images/Characters"),
                        resource_path("app/resource/images/Weapons")]

        for interval, name, qualityLevel in records[cardType]["four_star_intervals"] + records[cardType][
            "five_star_intervals"]:
            image_found = False
            for search_path in search_paths:
                image_path = os.path.join(search_path, f"{name}.png")
                # print(f"Checking image path: {image_path}")
                if os.path.exists(image_path):
                    image = Image.open(image_path)

                    image = image.resize((240, 320), Image.LANCZOS)

                    new_size = (image.width // 2, image.height // 2)
                    resized_image = image.resize(new_size, Image.LANCZOS)

                    # 设置背景颜色
                    if (interval, name, qualityLevel) in records[cardType]["four_star_intervals"]:
                        background_color = (126, 87, 194, 255)  # 紫色
                    elif (interval, name, qualityLevel) in records[cardType]["five_star_intervals"]:
                        background_color = (255, 204, 77, 255)  # 金色

                    # 背景颜色部分的高度设置为图像高度的20%
                    background_color_height = int(new_size[1] * 0.2)
                    background_size = (new_size[0], new_size[1] + background_color_height)
                    background = Image.new('RGBA', background_size, (0, 0, 0, 0))
                    background.paste(resized_image, (0, 0))

                    draw = ImageDraw.Draw(background)
                    font_size = 30
                    font = ImageFont.truetype(font_path, font_size)
                    text = f"{interval}"

                    text_bbox = draw.textbbox((0, 0), text, font=font)
                    text_width = text_bbox[2] - text_bbox[0]
                    text_height = text_bbox[3] - text_bbox[1]
                    text_position = ((background_size[0] - text_width) // 2, new_size[1])

                    # 绘制背景颜色部分
                    draw.rectangle([(0, new_size[1]), (background_size[0], background_size[1])], fill=background_color)

                    if cardType == 1 and name in list['characters'] and name not in list['UP']:
                        losePity_font = ImageFont.truetype(font_path, 20)
                        losePity_text = "Lost 50/50"
                        losePity_bbox = draw.textbbox((0, 0), losePity_text, font=losePity_font)
                        losePity_text_width = losePity_bbox[2] - losePity_bbox[0]
                        losePity_text_height = losePity_bbox[3] - losePity_bbox[1]
                        losePity_position = (
                            background_size[0] - losePity_text_width - 10,  # 右边距10像素
                            10  # 上边距10像素
                        )
                        draw.rectangle([(0, new_size[1]), (background_size[0], background_size[1])],
                                       fill='#ba5b49')
                        draw.text(losePity_position, losePity_text, font=losePity_font, fill='#ba5b49')

                    draw.text(text_position, text, font=font, fill='#FFFFFF')

                    output_image_path = os.path.join(output_directory, f"{name}_{interval}.png")
                    background.save(output_image_path)
                    image_found = True
                    break  # 找到图片后停止搜索
            #if not image_found:
                #print(f"Image not found for {name}")
