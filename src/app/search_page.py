from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QGridLayout, QFrame)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from PyQt5 import uic
import os
import math

class SearchPage(QWidget):
    result_selected = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.load_ui()
        self.setup_search_functionality()
    
    def load_ui(self):
        # Load the UI file
        ui_file = os.path.join(os.path.dirname(__file__), 'pages', 'search_page.ui')
        if os.path.exists(ui_file):
            uic.loadUi(ui_file, self)
        else:
            raise Exception("failed to load ui")

    def setup_search_functionality(self):
        # Connect search button
        self.searchBtn.clicked.connect(self.perform_search)
        
        # Setup results widget if using UI file
        if hasattr(self, 'scrollArea'):
            self.results_layout = QVBoxLayout(self.searchResult)
            self.results_layout.setContentsMargins(10, 10, 10, 10)
            
            # Initially hide search summary
            self.searchSummary.hide()
    
    def perform_search(self):
        # Simulate search
        query = self.searchBar.text()
        if not query:
            return
        
        # Show search summary
        self.summaryTime.setText(f"Search completed in 0.23s | Algorithm: {self.algoDropdown.currentText()} | Results: {len(query)}")
        self.searchSummary.show()
        
        # Clear previous results
        for i in reversed(range(self.results_layout.count())):
            child = self.results_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        # Add sample results
        sample_results = [
            ("Document Analysis Report", "Comprehensive analysis\n of document processing techniques..."),
            ("Search Algorithm Comparison", "Detailed comparison of \ndifferent search algorithms..."),
            ("Data Mining Techniques", "Overview of modern data mining \nand extraction methods..."),
            ("Information Retrieval Systems", "Study of information \nretrieval and ranking systems..."),
        ]
        
        cards = []
        for title, desc in sample_results:
            card = self.create_result_card(title, desc, "1")
            card.setMinimumWidth(100)
            card.setMaximumWidth(250)
            cards.append(card)
        
        cols = 3
        rows = math.ceil(len(cards) / cols)

        for row in range(rows):
            row_layout = QHBoxLayout()
            row_layout.setSpacing(10)
            
            # Add cards to this row
            for col in range(cols):
                card_index = row * cols + col
                if card_index < len(cards):
                    row_layout.addWidget(cards[card_index])
                else:
                    break
            
            # Add stretch to push cards to the left if row is not full
            row_layout.setAlignment(Qt.AlignHCenter)
            
            # Create a widget to hold the row layout
            row_widget = QWidget()
            row_widget.setLayout(row_layout)
            self.results_layout.addWidget(row_widget)
        
        # Add stretch at the bottom
        self.results_layout.addStretch()
    
    def create_result_card(self, title, description, matches):
        card = QFrame()
        card.setFrameStyle(QFrame.Box)
        card.setStyleSheet("""
            QFrame { 
                border: 1px solid rgba(150, 150, 150, 0.5); 
                border-radius: 8px; 
                padding: 10px; 
                margin: 5px; 
                background-color: rgba(50, 50, 50, 0.8);
            }
            QFrame:hover {
                border: 1px solid #007acc;
                background-color: rgba(50, 50, 50, 0.9);
            }
        """)
        
        
        
        layout = QVBoxLayout(card)
        layout.setSpacing(4)
        
        header_layout = QVBoxLayout()
        header_layout.setSpacing(0)

        # Matches count
        matches_label = QLabel(matches + " Matches")
        matches_label.setFont(QFont("Arial", 6))
        matches_label.setWordWrap(True)
        matches_label.setStyleSheet("color: #e2e2e2; ; padding: 0px 8px; background-color: none; border: none")
        matches_label.setAlignment(Qt.AlignRight)
        header_layout.addWidget(matches_label)
        
        # Title
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 8, QFont.Bold))
        title_label.setWordWrap(True)
        title_label.setAlignment(Qt.AlignLeft)
        header_layout.addWidget(title_label)
        

        layout.addLayout(header_layout)
        
        # Description preview
        desc_label = QLabel(description)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("line-height: 1.4;")
        desc_label.setFont(QFont("Arial", 7))
        layout.addWidget(desc_label)
        
        # Add stretch to push buttons to bottom
        layout.addStretch()
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)
        
        summary_btn = QPushButton("Summary")
        summary_btn.setStyleSheet("""
            QPushButton {
                background-color: #4c4c4c;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 11px;
                color: white;
            }
            QPushButton:hover {
                background-color: #636363;
            }
        """)
        summary_btn.clicked.connect(lambda: self.result_selected.emit())
        summary_btn.setCursor(Qt.PointingHandCursor)
        btn_layout.addWidget(summary_btn)
        
        view_btn = QPushButton("View CV")
        view_btn.setStyleSheet("""
            QPushButton {
                background-color: #007acc;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
        """)
        view_btn.setCursor(Qt.PointingHandCursor)
        btn_layout.addWidget(view_btn)
        
        layout.addLayout(btn_layout)
        
        return card
    
    @property
    def back_btn(self):
        return self.backBtn