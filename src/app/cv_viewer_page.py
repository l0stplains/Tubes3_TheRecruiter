from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QScrollArea, QFrame)
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QFont
from PyQt5 import uic
from PyQt5.QtWebEngineWidgets import QWebEngineView
import os

class CVViewerPage(QWidget):
    def __init__(self):
        super().__init__()
        self.load_ui()

    def load_ui(self):
        # Load the UI file
        ui_file = os.path.join(os.path.dirname(__file__), 'pages', 'cv_viewer_page.ui')
        if os.path.exists(ui_file):
            uic.loadUi(ui_file, self)
            
        else:
            raise Exception("failed to load ui")

    def loadPDF(self, applicationID):
        # fetch pdf path here

        
        pdf_path = "C:/Users/Lenovo/Downloads/Kompilasi UAS Stima.pdf"

        if not hasattr(self, 'pdf_view') or self.pdf_view is None:
            self.pdf_view = QWebEngineView()
            settings = self.pdf_view.settings()
            settings.setAttribute(settings.PluginsEnabled, True)
            settings.setAttribute(settings.PdfViewerEnabled, True)

        self.pdf_view.load(QUrl.fromLocalFile(pdf_path))

        if self.pdfWidget.layout() is None:
            layout = QVBoxLayout()
            layout.addWidget(self.pdf_view)
            self.pdfWidget.setLayout(layout)
        else:
            layout = self.pdfWidget.layout()
            if self.pdf_view.parent() != self.pdfWidget:
                layout.addWidget(self.pdf_view)



    @property
    def back_btn(self):
        return self.backBtn

