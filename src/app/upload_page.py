from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QFrame, QFileDialog)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5 import uic
import os

class UploadPage(QWidget):
    def __init__(self):
        super().__init__()
        self.data_count = 0
        self.load_ui()
        self.setup_functionality()
    
    def load_ui(self):
        # Load the UI file
        ui_file = os.path.join(os.path.dirname(__file__), 'pages', 'upload_page.ui')
        if os.path.exists(ui_file):
            uic.loadUi(ui_file, self)
        else:
            raise Exception("failed to load ui")
   
    def setup_functionality(self):
        # Connect button signals
        self.addPdfBtn.clicked.connect(self.add_pdf)
        self.addFolderBtn.clicked.connect(self.add_folder)
    
    def add_pdf(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select PDF", "", "PDF Files (*.pdf)")
        if file_path:
            self.data_count += 1
            self.update_data_summary()
    
    def add_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder_path:
            # Count PDF files in folder
            try:
                pdf_count = len([f for f in os.listdir(folder_path) if f.lower().endswith('.pdf')])
                self.data_count += pdf_count
                self.update_data_summary()
            except OSError:
                # Handle case where folder can't be read
                pass
    
    def update_data_summary(self):
        self.dataInfo.setText(f"Total documents: {self.data_count}\nLast updated: Just now\nStorage used: {self.data_count * 2.5:.1f} MB")
    
    @property
    def back_btn(self):
        return self.backBtn