from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QScrollArea, QFrame)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5 import uic
import os

class CVSummaryPage(QWidget):
    def __init__(self):
        super().__init__()
        self.load_ui()
    
    def load_ui(self):
        # Load the UI file
        ui_file = os.path.join(os.path.dirname(__file__), 'pages', 'cv_summary_page.ui')
        if os.path.exists(ui_file):
            uic.loadUi(ui_file, self)
        else:
            # Fallback: create UI programmatically if .ui file doesn't exist
            self.create_ui_programmatically()

    def populateContent():
        pass

    @property
    def back_btn(self):
        return self.backBtn