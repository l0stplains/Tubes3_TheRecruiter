import src.app.resources.resources_rc
import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget
from PyQt5.QtCore import Qt

from src.app.main_menu import MainMenuPage
from src.app.search_page import SearchPage
from src.app.cv_summary_page import CVSummaryPage
from src.app.upload_page import UploadPage
from src.app.cv_viewer_page import CVViewerPage
from PyQt5.QtGui import QIcon, QPixmap


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("The Recruiter")
        self.setWindowIcon(QIcon(":/images/app_icon.png"))
        self.setGeometry(100, 100, 800, 600)
        
        # Create stacked widget for navigation
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        # Initialize pages
        self.main_menu = MainMenuPage()
        self.search_page = SearchPage()
        self.cv_summary_page = CVSummaryPage()
        self.cv_viewer_page = CVViewerPage()
        self.add_data_page = UploadPage()
        
        # Add pages to stacked widget
        self.stacked_widget.addWidget(self.main_menu)
        self.stacked_widget.addWidget(self.search_page)
        self.stacked_widget.addWidget(self.cv_summary_page)
        self.stacked_widget.addWidget(self.add_data_page)
        self.stacked_widget.addWidget(self.cv_viewer_page)
        
        # Connect navigation signals
        self.setup_navigation()
        
        # Show main menu initially
        self.stacked_widget.setCurrentWidget(self.main_menu)
    
    def setup_navigation(self):
        # Main menu navigation
        self.main_menu.search_btn.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.search_page))
        self.main_menu.add_data_btn.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.add_data_page))
        self.main_menu.exit_btn.clicked.connect(lambda: exit(0))

        # Search page navigation
        self.search_page.back_btn.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.main_menu))
        self.search_page.result_selected.connect(lambda applicationID: (self.stacked_widget.setCurrentWidget(self.cv_summary_page), self.cv_summary_page.populateContent(applicationID)))
        self.search_page.cv_selected.connect(lambda applicationID: (self.stacked_widget.setCurrentWidget(self.cv_viewer_page), self.cv_viewer_page.loadPDF(applicationID)))
        
        # Result detail navigation
        self.cv_summary_page.back_btn.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.search_page))
        self.cv_viewer_page.back_btn.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.search_page))
        
        # Add data navigatio
        self.add_data_page.back_btn.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.main_menu))



def window():
    
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())