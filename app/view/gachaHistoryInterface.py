import json
import os
import threading

from PyQt5.QtCore import QEasingCurve
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from qfluentwidgets import FlowLayout, ImageLabel, InfoBarIcon, FlyoutAnimationType

from app.common.config import cfg
from app.resource.Pages.gachaHistory import Ui_gachaHistoryWindow
from app.util.UI_general_method import generate_images, show_info_bar, resource_path, show_flyout
from app.util.requests_general import fetch_gacha_records, find_record, extract_fragment_params

cardPoolType = {
    1: "Character Event Wish-角色UP",
    2: "Weapon Event Wish-武器UP",
    3: "Character Standard Wish-角色常驻",
    4: "Weapon Standard Wish-武器常驻",
}


class Demo(QWidget):

    def __init__(self):
        super().__init__()

        self.layout = FlowLayout(self, needAni=True)
        self.layout.setAnimation(250, QEasingCurve.OutQuad)
        self.layout.setContentsMargins(30, 30, 30, 30)
        self.layout.setVerticalSpacing(20)
        self.layout.setHorizontalSpacing(10)

    def prepare_gacha_image(self, cardPool_type, records, only_five_star=False):
        self.layout.takeAllWidgets()

        base_path = os.path.join(os.getcwd(), 'AppData', 'gachaImage')
        input_directory = os.path.join(base_path, cardPool_type)

        if only_five_star and records:
            five_star_intervals = records['five_star_intervals']
            five_star_names = [interval[1] for interval in five_star_intervals]
        else:
            five_star_names = None

        for filename in os.listdir(input_directory):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                if only_five_star and five_star_names:
                    if not any(name in filename for name in five_star_names):
                        continue
                image = ImageLabel(os.path.join(input_directory, filename))
                # 按比例缩放到指定高度
                image.scaledToHeight(150)
                image.setBorderRadius(8, 8, 8, 8)

                self.layout.addWidget(image)


class gachaHistoryPageInterface(QWidget, Ui_gachaHistoryWindow):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)

        self.records = None
        self.only_show_five_star = False

        self.image_folder_path = os.path.join(os.getcwd(), 'AppData', 'gachaImage')
        os.makedirs(self.image_folder_path, exist_ok=True)

        self.placeholder_widget = self.findChild(QWidget, 'showHistory')
        self.demo_widget = Demo()
        layout = QVBoxLayout(self.placeholder_widget)
        layout.addWidget(self.demo_widget)

        self.ComboBox.setCurrentIndex(-1)
        self.ComboBox.setEnabled(False)

        self.ComboBox.currentIndexChanged.connect(self.refresh_gachaHistory)
        self.urlButton.clicked.connect(self.fetch_gacha_history)
        self.show5starButton.checkedChanged.connect(self.set_show_stats)
        self.usageButton.clicked.connect(self.show_usage)

        self.folder_mapping = {
            'Character Event Wish-角色UP': 1,
            'Weapon Event Wish-武器UP': 2,
            'Character Standard Wish-角色常驻': 3,
            'Weapon Standard Wish-武器常驻': 4
        }

    def show_usage(self):
        show_flyout(self, InfoBarIcon.INFORMATION, self.tr('How To Use'),
                    self.tr('1.Open gacha history in game,and ensure that history can be loaded properly\n'
                            '2.Click "Get Gacha History"\n'
                            '3.Wait for generate'), self.usageButton, FlyoutAnimationType.DROP_DOWN)

    def fetch_gacha_history(self):
        log_path = os.path.join(cfg.get(cfg.gamePath.value), '..', '..', '..', 'Saved', 'Logs',
                                'Client.log')
        url = find_record(log_path)

        def run():
            try:
                params = extract_fragment_params(url)
                player_id = params['player_id']
                cardPoolId = params['resources_id']
                serverId = params['svr_id']
                recordId = params['record_id']

                records = fetch_gacha_records(player_id, cardPoolId, cardPoolType, serverId, recordId)
                if records is None:
                    show_info_bar(self, 'error', 'History URL Found,But records Get Failed', self.tr(''))
                    return
                self.records = records
                generate_images(records, cardPoolType)

                self.ComboBox.clear()
                for name in os.listdir(self.image_folder_path):
                    if name in self.folder_mapping:
                        self.ComboBox.addItem(name)
                self.ComboBox.setCurrentIndex(0)
                self.ComboBox.setEnabled(True)
            except Exception as e:
                show_info_bar(self, 'error', self.tr('Error'), self.tr(f'{e}'))
        if url:
            show_info_bar(self, 'info', self.tr('Generating gacha records'), self.tr('Please wait patiently'))
            thread = threading.Thread(target=run)
            thread.start()
        else:
            show_info_bar(self, 'error', self.tr('Gacha History URL not Found'),
                          self.tr('Please open gacha history in game and try again'))

    def calculate_up_probability(self, index, five_star_intervals):
        list_json = resource_path('app/resource/FiveStarList.json')
        with open(list_json, 'r', encoding='utf-8') as list:
            data = json.load(list)
        up_count = sum(1 for interval in five_star_intervals if interval[1] in data['UP'])
        total_five_star_count = len(five_star_intervals)
        if total_five_star_count > 0 and index == 1:
            up_probability = int((up_count / total_five_star_count) * 100)
        else:
            up_probability = 100
        return up_probability

    def set_ring(self, index):
        three_star_count = self.records[index]['three_star_count']
        four_star_count = self.records[index]['four_star_count']
        five_star_count = self.records[index]['five_star_count']
        countdown = self.records[index]['next_five_star_countdown']
        average_five_star_interval = int(self.records[index]['average_five_star_interval'])
        total_count = int(three_star_count) + int(four_star_count) + int(five_star_count)
        up_probability = self.calculate_up_probability(index, self.records[index]['five_star_intervals'])

        self.threeStarRing.setTextVisible(True)
        self.fourStarRing.setTextVisible(True)
        self.fiveStarRing.setTextVisible(True)
        self.winPityRing.setTextVisible(True)

        self.BodyLabel.setText(self.tr('Total number of pulls: {total_count}\n'
                                       '⭐️⭐️⭐️ counts: {three_star_count}\n'
                                       '⭐️⭐️⭐️⭐️ counts: {four_star_count}\n'
                                       '⭐️⭐️⭐️⭐️⭐️ counts: {five_star_count}\n'
                                       'Pulls left until next pity: {countdown}\n'
                                       'Average Pity: {average_five_star_interval}\n')
                               .format(total_count=total_count,
                                       three_star_count=three_star_count,
                                       four_star_count=four_star_count,
                                       five_star_count=five_star_count,
                                       countdown=countdown,
                                       average_five_star_interval=average_five_star_interval))

        if total_count != 0:
            self.threeStarRing.setValue(int((int(three_star_count) / total_count) * 100))
            self.fourStarRing.setValue(int((int(four_star_count) / total_count) * 100))
            self.fiveStarRing.setValue(int((int(five_star_count) / total_count) * 100))
            self.winPityRing.setValue(up_probability)
        else:
            self.threeStarRing.setValue(0)
            self.fourStarRing.setValue(0)
            self.fiveStarRing.setValue(0)
            self.winPityRing.setValue(up_probability)

    def refresh_gachaHistory(self):
        cardPool_Type = self.ComboBox.currentText()
        if cardPool_Type in self.folder_mapping:
            cardPool_Index = self.folder_mapping[cardPool_Type]
            self.demo_widget.prepare_gacha_image(cardPool_Type, self.records[cardPool_Index], self.only_show_five_star)
            self.set_ring(cardPool_Index)

    def set_show_stats(self):
        if self.show5starButton.isChecked():
            self.only_show_five_star = True
            self.refresh_gachaHistory()
        else:
            self.only_show_five_star = False
            self.refresh_gachaHistory()
