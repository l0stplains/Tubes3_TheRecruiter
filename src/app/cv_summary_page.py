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
            raise Exception("failed to load ui")

    def clearLayout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()

    
    def getOrCreateLayout(self, widget, layout_type=QVBoxLayout):
        existing_layout = widget.layout()
        if existing_layout is not None:
            self.clearLayout(existing_layout)
            return existing_layout
        else:
            new_layout = layout_type()
            widget.setLayout(new_layout)
            return new_layout

    def populateContent(self, tupleData):
        applicantId, detailId = tuppleData
        # fetch data here idk how bruh

        # contoh data
        summary = {
            "Name": "Refki Ganteng",
            "birthday": "05-19-2025",
            "address": "cianjur",
            "phone": "+621111111"
        }

        skills = ["React", "Express", "HTML"]

        jobs = [
            {
                "position": "CTO",
                "year": "2003-2004",
                "description": "sigma bois"
            },
            {
                "position": "CEO",
                "year": "2006-2010",
                "description": "mewing bois"
            }
        ]

        education = [
            {
                "major": "Huzz",
                "institution": "Rizzler Academy",
                "year": "2022-2026"
            },
            {
                "major": "Rizz",
                "institution": "Mewing Academy",
                "year": "2018-2022"
            }
        ]

        # ntar ubah aj ato gmn kek
        if applicantId == "ubah ini ki":  
            
            # Summary section
            self.summaryTitle.setText(summary["Name"])
            
            # Create VBox for summary details
            summary_layout =self.getOrCreateLayout(self.summaryDesc, QVBoxLayout)
            summary_layout.setSpacing(0)
            
            # Create labels with different styles
            for key, value in summary.items():
                if key == 'Name': continue
                info = QLabel(f"{key}: {value}")
                info.setStyleSheet("margin: 5px; padding: 0px; background-color: none; border: none;")
                summary_layout.addWidget(info)
            
            
            # Set the layout to your summary parent widget
            
            # Skills section - HBox with pill-like styling
            skills_layout = self.getOrCreateLayout(self.skillDesc, QHBoxLayout)
            
            for skill in skills:
                skill_label = QLabel(skill)
                skill_label.setStyleSheet("""
                    QLabel {
                        background-color: #d0d0d0;
                        border-radius: 15px;
                        padding: 8px 16px;
                        font-weight: bold;
                        color: #333;
                    }
                """)
                skills_layout.addWidget(skill_label)
            
            # Add stretch to push skills to the left
            skills_layout.addStretch()
            
            # Job History section
            jobs_layout = self.getOrCreateLayout(self.jobDesc, QVBoxLayout)
            jobs_layout.setSpacing(8)
            
            for job in jobs:
                # Create VBox for each job
                job_widget = QWidget()
                job_layout = QVBoxLayout(job_widget)
                job_layout.setSpacing(0)

                # Position (bold, larger)
                position_label = QLabel(job['position'])
                position_label.setStyleSheet("""
                    QLabel {
                        font-weight: bold;
                        font-size: 14px;
                        color: #d9d9d9;
                        margin: 0px;
                        padding: 0px;
                        background-color: none; border: none;
                    }
                """)
                
                # Year (grey, smaller)
                year_label = QLabel(job['year'])
                year_label.setStyleSheet("""
                    QLabel {
                        color: #b1b1b1;
                        font-size: 10px;
                        margin: 0px;
                        padding: 0px;
                        background-color: none; border: none;
                    }
                """)
                
                # Description (normal)
                desc_label = QLabel(job['description'])
                desc_label.setStyleSheet("""
                    QLabel {
                        color: #d9d9d9;
                        font-size: 12px;
                        margin: 0px;
                        padding: 0px;
                        background-color: none; border: none;
                    }
                """)
                desc_label.setWordWrap(True)
                
                job_layout.addWidget(position_label)
                job_layout.addWidget(year_label)
                job_layout.addWidget(desc_label)
                job_layout.setContentsMargins(0, 0, 0, 0)
                
                jobs_layout.addWidget(job_widget)
            
            
            # Education section
            education_layout = self.getOrCreateLayout(self.educationDesc, QVBoxLayout)
            education_layout.setSpacing(8)
            
            for edu in education:
                # Create VBox for each education
                edu_widget = QWidget()
                edu_layout = QVBoxLayout(edu_widget)
                edu_layout.setSpacing(0)
                
                # Major and Institution (bold)
                major_label = QLabel(f"{edu['major']}")
                major_label.setStyleSheet("""
                    QLabel {
                        font-weight: bold;
                        font-size: 14px;
                        color: #d9d9d9;
                        margin: 0px;
                        padding: 0px;
                        background-color: none; border: none;
                    }
                """)

                institution_label = QLabel(f"{edu['institution']}")
                institution_label.setStyleSheet("""
                    QLabel {
                        font-size: 13px;
                        color: #c4c4c4;
                        margin: 0px;
                        padding: 0px;
                        background-color: none; border: none;
                    }
                """)
                
                # Year (grey, smaller)
                year_label = QLabel(edu['year'])
                year_label.setStyleSheet("""
                    QLabel {
                        color: #b1b1b1;
                        font-size: 10px;
                        margin: 0px;
                        padding: 0px;
                        background-color: none; border: none;
                    }
                """)
                
                edu_layout.addWidget(major_label)
                edu_layout.addWidget(institution_label)
                edu_layout.addWidget(year_label)
                edu_layout.setContentsMargins(0, 0, 0, 0)
                
                education_layout.addWidget(edu_widget)
            

    @property
    def back_btn(self):
        return self.backBtn

