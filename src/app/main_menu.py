from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import QPixmap
from PyQt5 import uic
import os

class MainMenuPage(QWidget):
    def __init__(self):
        super().__init__()
        self.load_ui()
    
    def load_ui(self):
        # Load the UI file
        ui_file = os.path.join(os.path.dirname(__file__), 'pages', 'main_menu_page.ui')
        if os.path.exists(ui_file):
            uic.loadUi(ui_file, self)
        else:
            raise Exception("failed to load ui")
    

    @property
    def search_btn(self):
        return self.searchBtn
    
    @property
    def add_data_btn(self):
        return self.addBtn
    
    @property
    def exit_btn(self):
        return self.exitBtn
