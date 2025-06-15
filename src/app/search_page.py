from typing import List, Dict, Any, Tuple, Optional
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QGridLayout, QFrame)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from PyQt5 import uic
from src.db.models import db_manager
from src.search.boyer_moore import BoyerMooreSearch
from src.search.levenshtein import LevenshteinSearch
from src.search.searcher import KeywordSearcher

import os, time
from multiprocessing import Pool
from src.search.search_workers import (
    search_exact_worker,
    search_fuzzy_worker
)

import time
from multiprocessing import Pool
import os
import math

class SearchPage(QWidget):
    result_selected = pyqtSignal(tuple)
    cv_selected = pyqtSignal(tuple)
    
    def __init__(self):
        super().__init__()
        self.load_ui()
        self.use_multiprocessing = True # for benchmarking
        self.setup_search_functionality()

    def _search_single_cv(
        self,
        args: Any
    ) -> Dict[str, Any]:
        """
        Worker function for Pool.map:
         - args = (detail_dict, keywords, algo_name)
        """
        detail, keywords, algo_name = args
        path = detail["cv_path"]

        text = self.extractor.extract_single_pdf(path)["pattern_matching"]

        if algo_name == "BM":
            algo = BoyerMooreSearch()
        else:
            algo = KMPSearch()
        ks_exact = KeywordSearcher(algo, case_sensitive=False, whole_word=False)
        exact_raw = ks_exact.search(text, keywords)
        exact_count = sum(len(v) for v in exact_raw.values())

        missing = [kw for kw, positions in exact_raw.items() if not positions]

        return {
            "detail": detail,
            "text": text,
            "exact_raw": exact_raw,
            "exact_count": exact_count,
            "missing": missing
        }

    
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
        keywords        = [kw.strip() for kw in self.searchBar.text().split(",") if kw.strip()]
        algo_name       = self.algoDropdown.currentText()      # "BM" or "KMP"
        max_match       = self.maxMatch.value()               # desired number of CVs
        fuzzy_tolerance = 0.2
        if not keywords or max_match <= 0:
            return

        applicants = db_manager.get_all_applicants_data()
        exact_tasks: List[Tuple[Dict[str,Any], List[str], str, str]] = []
        for app in applicants:
            profile = app["applicant_profile"]
            for detail in app["application_details"]:
                task_detail = {
                    **detail,               # detail_id, application_role, cv_path
                    "applicant_profile": profile
                }
                exact_tasks.append((task_detail, keywords, algo_name, ""))

        t0 = time.time()
        if self.use_multiprocessing:
            with Pool(os.cpu_count()) as pool:
                cv_results = pool.starmap(search_exact_worker, exact_tasks)
        else:
            cv_results = [
                search_exact_worker(*args)
                for args in exact_tasks
            ]
        t_exact = time.time() - t0

        cv_results.sort(key=lambda r: r["exact_count"], reverse=True)
        exact_selected = cv_results[:max_match]
        exact_hits = [r for r in exact_selected if r["exact_count"] > 0]
        E = len(exact_hits)

        total_exact_scanned = len(exact_tasks) 
        total_fuzzy_scanned = 0
        fuzzy_selected: List[Dict[str, Any]] = []
        if E < max_match:
            # candidates for fuzzy are any CV with exact_count==0
            no_exact = [r for r in cv_results if r["exact_count"] == 0]
            total_fuzzy_scanned = len(no_exact)

            # prepare fuzzy tasks on no_exact...
            fuzzy_tasks = [
                (idx, r["text"], keywords, fuzzy_tolerance)
                for idx, r in enumerate(no_exact)
            ]

            t1 = time.time()
            if self.use_multiprocessing:
                with Pool(os.cpu_count()) as pool:
                    fuzzy_out = pool.starmap(search_fuzzy_worker, fuzzy_tasks)
            else:
                fuzzy_out = [
                    search_fuzzy_worker(*args)
                    for args in fuzzy_tasks
                ]
            t_fuzzy = time.time() - t1

            # merge fuzzy results back into 'remaining'
            for idx, fuzzy_raw in fuzzy_out:
                no_exact[idx]["fuzzy_raw"] = fuzzy_raw
                # total fuzzy matches count
                no_exact[idx]["fuzzy_count"] = sum(len(v) for v in fuzzy_raw.values())

            # pick top (max_match - E) by fuzzy_count > 0
            remaining = [r for r in no_exact if r.get("fuzzy_count", 0) > 0]
            remaining.sort(key=lambda r: r["fuzzy_count"], reverse=True)
            slots = max_match - E
            fuzzy_selected = remaining[:slots]
        else:
            t_fuzzy = 0.0

        for res in exact_selected:
            res.setdefault("fuzzy_count", 0)
        for res in fuzzy_selected:
            res.setdefault("exact_count", 0)

        all_candidates = exact_selected + fuzzy_selected

        all_candidates = [
            r for r in all_candidates
            if (r["exact_count"] > 0) or (r["fuzzy_count"] > 0)
        ]

        all_candidates.sort(
            key=lambda r: (r["exact_count"], r["fuzzy_count"]),
            reverse=True
        )

        final_selection = all_candidates[:max_match]

        print(f"Exact‐match time: {t_exact:.3f}s")
        print(f"Fuzzy‐match time: {t_fuzzy:.3f}s")

        t_exact_ms = t_exact * 1000
        t_fuzzy_ms = t_fuzzy * 1000

        # Show search summary
        fuzzy_text = "" if t_fuzzy == 0.0 and total_fuzzy_scanned == 0 else f"| Fuzzy‐match: {total_fuzzy_scanned}CV{'s' if total_fuzzy_scanned > 1 else ''} scanned in {t_fuzzy_ms:.2f}ms "
        self.summaryTime.setText(f"Exact‐match: {total_exact_scanned}CV{'s' if total_exact_scanned > 1 else ''} scanned in {t_exact_ms:.2f}ms {fuzzy_text}| Algorithm: {algo_name} | Results: {len(final_selection)}")
        self.searchSummary.show()
        
        # Clear previous results
        for i in reversed(range(self.results_layout.count())):
            child = self.results_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        # HELLLO REFKI ATO GHANA
        # INI DISINI ASUMSINYA BAKAL DAPET APPLICATION ID YAH
        # BUAT DAPETIN DATA UNTUK CV SUMMARY NYA. OKEH THANKS
        # Refki: DONE JIB
        cards = []
        for rank, res in enumerate(final_selection, 1):
            if res.get("fuzzy_raw"):
                desc = self.format_keyword_report(res['exact_raw'], res['fuzzy_raw'])
                total = self.count_occurrences(res['exact_raw'], res['fuzzy_raw'])
            else:
                desc = self.format_keyword_report(res['exact_raw'])
                total = self.count_occurrences(res['exact_raw'])
            count = total['total_exact'] + total['total_fuzzy']
            profile = res['detail']['applicant_profile']
            card = self.create_result_card(f"{profile['first_name']} {profile['last_name']}", desc, str(count), profile['applicant_id'], res['detail']['detail_id'])
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
    
    def create_result_card(self, title, description, matches, applicantId, detailId):
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
        summary_btn.clicked.connect(lambda: self.result_selected.emit((applicantId, detailId)))
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
        view_btn.clicked.connect(lambda: self.cv_selected.emit((applicantId, detailId)))
        btn_layout.addWidget(view_btn)
        
        layout.addLayout(btn_layout)
        
        return card
    
    @property
    def back_btn(self):
        return self.backBtn

    def format_keyword_report(
        self,
        exact_raw: Dict[str, List[int]],
        fuzzy_raw: Dict[str, List[Tuple[int,int]]] = None
    ) -> str:
        """
        Build a report string of matched keywords.

        Args:
            exact_raw:   Mapping keyword -> list of exact‐match positions.
            fuzzy_raw:   (Optional) Mapping keyword -> list of fuzzy.
                         If provided and non‐empty, fuzzy lines are appended.
        Returns:
            A multi‐line string like:
            
            Matched keywords:
            1. React: 1 occurrence
            2. Express: 2 occurrences
            ...
            Fuzzy keywords:
            1. Nodejs: 1 fuzzy occurrence
            ...
        """
        lines = ["Matched keywords:"]

        # Exact matches first
        for i, (kw, poses) in enumerate(exact_raw.items(), start=1):
            count = len(poses)
            if count > 0:
                occ = "occurrence" if count == 1 else "occurrences"
                lines.append(f"{i}. {kw}: {count} {occ}")

        # Fuzzy matches, if any
        if fuzzy_raw:
            # filter to only those with at least one fuzzy hit
            fuzzy_hits = {kw: hits for kw, hits in fuzzy_raw.items() if hits}
            if fuzzy_hits:
                lines.append("")  # blank line
                lines.append("Fuzzy matches:")
                for i, (kw, hits) in enumerate(fuzzy_hits.items(), start=1):
                    count = len(hits)
                    occ = "fuzzy occurrence" if count == 1 else "fuzzy occurrences"
                    lines.append(f"{i}. {kw}: {count} {occ}")

        return "\n".join(lines)

    def count_occurrences(
        self,
        exact_raw: Dict[str, List[int]],
        fuzzy_raw: Optional[Dict[str, List[Tuple[int,int]]]] = None
    ) -> Dict[str, object]:
        """
        Count exact and fuzzy matches.

        Args:
          exact_raw: mapping keyword -> list of exact‐match positions.
          fuzzy_raw: mapping keyword -> list of (pos, dist) for fuzzy matches (optional).

        Returns:
          A dict containing:
            - exact_counts: Dict[keyword, int]
            - total_exact: int
            - fuzzy_counts: Dict[keyword, int]
            - total_fuzzy: int
        """
        # per‑keyword exact counts
        exact_counts = {kw: len(pos_list) for kw, pos_list in exact_raw.items()}
        total_exact  = sum(exact_counts.values())

        # per‑keyword fuzzy counts (if provided)
        if fuzzy_raw is not None:
            fuzzy_counts = {kw: len(hits) for kw, hits in fuzzy_raw.items()}
            total_fuzzy  = sum(fuzzy_counts.values())
        else:
            fuzzy_counts = {}
            total_fuzzy  = 0

        return {
            "total_exact": total_exact,
            "total_fuzzy": total_fuzzy
        }



