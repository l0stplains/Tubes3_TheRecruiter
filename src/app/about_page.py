from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QFrame, QFileDialog)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5 import uic
import os

class AboutPage(QWidget):
    def __init__(self):
        super().__init__()
        self.data_count = 0
        self.load_ui()
    
    def load_ui(self):
        # Load the UI file
        ui_file = os.path.join(os.path.dirname(__file__), 'pages', 'about_page.ui')
        if os.path.exists(ui_file):
            uic.loadUi(ui_file, self)
        else:
            raise Exception("failed to load ui")
   
    @property
    def back_btn(self):
        return self.backBtn