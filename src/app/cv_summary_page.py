from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QScrollArea, QFrame)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5 import uic
import os
from src.core.extractor import PDFExtractor
from src.db.models import db_manager 
from src.search.cv_grouper import CVGrouper

class CVSummaryPage(QWidget):
    def __init__(self):
        super().__init__()
        self.load_ui()
        self.cv_grouper = CVGrouper()
    
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
        applicantId, detailId = tupleData

        query_data = db_manager.get_data_by_applicant_id(applicantId)
        applicant_data = query_data['application_details']
        applicant_profile = query_data['applicant_profile']
        print(query_data)
        pdf_path = ""
        for data in applicant_data:
            if data['detail_id'] == detailId:
                pdf_path = data['cv_path']
        
        # fetch data here idk how bruh
        extractor = PDFExtractor()
        text = extractor.extract_single_pdf(pdf_path)["regex_format"]

        data = self.cv_grouper.group_cv_data(text)

        for key, value in data.items():
            print("-------------------------------------------")
            print(key.upper())
            print("-------------------------------------------")
            print(value)
            print("-------------------------------------------")

        summary = applicant_profile

        skills = data["skills"]
        skills = skills[:10]

        jobs = data["jobs"]
        jobs = jobs[:10]

        education = data["education"]
        education = education[:10]
            
        if summary:
            # Summary section
            self.summaryTitle.setText(f"{summary['first_name']} {summary['last_name']}")
            
            # Create VBox for summary details
            summary_layout = self.getOrCreateLayout(self.summaryDesc, QVBoxLayout)
            summary_layout.setSpacing(0)
            
            # Create labels with different styles
            for key, value in summary.items():
                if key == 'first_name' or key == "last_name" or key == "applicant_id": continue
                info = QLabel(f"{key}: {value}")
                info.setStyleSheet("margin: 5px; padding: 0px; background-color: none; border: none;")
                summary_layout.addWidget(info)
        else:
            summary_layout = self.getOrCreateLayout(self.summaryDesc, QVBoxLayout)
            summary_layout.setSpacing(8)
            fail_label = QLabel(f"failed to find education data")
            fail_label.setStyleSheet("""
                QLabel {
                    font-weight: bold;
                    font-size: 10px;
                    color: #d9d9d9;
                    margin: 0px;
                    padding: 0px;
                    background-color: none; border: none;
                }
            """)
            summary_layout.addWidget(fail_label)
            
        if skills:
            # Skills section - HBox with pill-like styling
            skills_layout = self.getOrCreateLayout(self.skillDesc, QVBoxLayout)
  
            for i, skill in enumerate(skills):
                if i % 5 == 0:  # Start a new row every 4 items
                    row_widget = QWidget()
                    row_layout = QHBoxLayout(row_widget)
                    skills_layout.addWidget(row_widget)
                
                skill_label = QLabel(skill)
                skill_label.setAlignment(Qt.AlignHCenter)
                skill_label.setStyleSheet("""
                    QLabel {
                        border-radius: 10px;
                        padding: 8px 16px;
                        font-size: 8px;                                          
                        font-weight: bold;
                        color: #d9d9d9;
                    }
                """)
                row_layout.addWidget(skill_label)

            # Add stretch to the last row if it's not full
            if len(skills) % 5 != 0:
                row_layout.setAlignment(Qt.AlignHCenter)
            
            # Add stretch to push skills to the left
            skills_layout.addStretch()
        else:
            skills_layout = self.getOrCreateLayout(self.skillDesc, QVBoxLayout)
            skills_layout.setSpacing(8)
            fail_label = QLabel(f"failed to find education data")
            fail_label.setStyleSheet("""
                QLabel {
                    font-weight: bold;
                    font-size: 10px;
                    color: #d9d9d9;
                    margin: 0px;
                    padding: 0px;
                    background-color: none; border: none;
                }
            """)
            skills_layout.addWidget(fail_label)
            skills_layout.addStretch()

            # Job History section
        if jobs:
            jobs_layout = self.getOrCreateLayout(self.jobDesc, QVBoxLayout)
            jobs_layout.setSpacing(8)
            
            for job in jobs:
                # Create VBox for each job
                job_widget = QWidget()
                job_layout = QVBoxLayout(job_widget)
                job_layout.setSpacing(0)

                # Position (bold, larger)
                position_label = QLabel(job['position'][:100])
                position_label.setWordWrap(True)
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
                desc_label = QLabel(job['description'][:100])
                desc_label.setWordWrap(True)
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
        else:
            jobs_layout = self.getOrCreateLayout(self.jobDesc, QVBoxLayout)
            jobs_layout.setSpacing(8)
            fail_label = QLabel(f"failed to find job history data")
            fail_label.setStyleSheet("""
                QLabel {
                    font-weight: bold;
                    font-size: 10px;
                    color: #d9d9d9;
                    margin: 0px;
                    padding: 0px;
                    background-color: none; border: none;
                }
            """)
            jobs_layout.addWidget(fail_label)
            
        # Education section
        if education:
            education_layout = self.getOrCreateLayout(self.educationDesc, QVBoxLayout)
            education_layout.setSpacing(8)
            
            for edu in education:
                # Create VBox for each education
                edu_widget = QWidget()
                edu_layout = QVBoxLayout(edu_widget)
                edu_layout.setSpacing(0)
                
                # Major and Institution (bold)
                major_label = QLabel(f"{edu['major'][:100]}")
                major_label.setWordWrap(True)
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

                institution_label = QLabel(f"{edu['institution'][:100]}")
                institution_label.setWordWrap(True)
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
        else:
            education_layout = self.getOrCreateLayout(self.educationDesc, QVBoxLayout)
            education_layout.setSpacing(8)
            fail_label = QLabel(f"failed to find education data")
            fail_label.setStyleSheet("""
                QLabel {
                    font-weight: bold;
                    font-size: 10px;
                    color: #d9d9d9;
                    margin: 0px;
                    padding: 0px;
                    background-color: none; border: none;
                }
            """)
            education_layout.addWidget(fail_label)

    @property
    def back_btn(self):
        return self.backBtn

