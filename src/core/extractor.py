import os
import re
from pathlib import Path
from typing import Dict, List, Tuple
import fitz  # PyMuPDF

class PDFExtractor:
    def __init__(self, data_folder: str = "data"):
        """
        Initialize PDF Extractor
        Args:
            data_folder: Path to folder containing PDF files
        """
        if data_folder == "data":
            try:
                current_path = Path(__file__).resolve()
                project_root = next((p for p in current_path.parents if (p / "pyproject.toml").exists()), Path.cwd())
            except NameError:
                project_root = Path.cwd()
            self.data_folder = project_root / "data"
        else:
            self.data_folder = Path(data_folder)

        self.extracted_data = {'regex_format': {}, 'pattern_matching': {}}

        if not self.data_folder.exists():
            print(f"[-] Data folder '{self.data_folder}' not found!")
            try:
                self.data_folder.mkdir(parents=True, exist_ok=True)
                print(f"[+] Created data folder: {self.data_folder}")
            except Exception as e:
                print(f"[-] Could not create data folder: {e}")
            return
        # print(f"[+] PDF Extractor initialized with data folder: {self.data_folder}")

    def extract_text_from_pdf(self, pdf_path: Path) -> str:
            """Extract raw text from PDF file"""
            try:
                doc = fitz.open(str(pdf_path))
                text = ""
                for page_num, page in enumerate(doc):
                    # Add the text of the current page
                    text += page.get_text()
                    
                    # If it's not the last page, add a clean separator (no more "Page Break")
                    if page_num < len(doc) - 1:
                        text += "\n\n"  # Changed from "\n\n--- Page Break ---\n\n"
                        
                doc.close()
                return text
            except Exception as e:
                print(f"[-] Error extracting text from {pdf_path}: {e}")
                return ""

    def format_for_regex(self, raw_text: str) -> str:
        """Format text for regex processing - preserve original structure with proper spacing"""
        if not raw_text: return ""
        text = re.sub(r'([a-z])([A-Z])', r'\1 \2', raw_text)
        text = re.sub(r'([a-z])(of|and|the|in|for|with|to)([A-Z])', r'\1 \2 \3', text)
        text = re.sub(r'\.([A-Z])', r'. \1', text)
        text = re.sub(r'[ \t]+', ' ', text)
        text = re.sub(r' *\n *', '\n', text)
        sections = ['Skills', 'Summary', 'Highlights', 'Accomplishments', 'Experience', 'Education', 'Projects']
        for section in sections:
            pattern1 = re.compile(f'({section.upper()}|{section})\\n([A-Z])')
            text = pattern1.sub(r'\1\n\n\2', text)
            pattern2 = re.compile(f'([a-z\\.])\\n({section.upper()}|{section})\\n')
            text = pattern2.sub(r'\1\n\n\2\n', text)
        return text.strip()

    def format_for_pattern_matching(self, raw_text: str) -> str:
        """Format text for pattern matching - continuous lowercase"""
        if not raw_text: return ""
        text = raw_text.lower()
        text = re.sub(r'[^\w\s\.,\-\+\(\)/]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def extract_single_pdf(self, pdf_path: Path) -> Dict[str, str]:
        """Extract text from a single PDF in both formats, ensuring ASCII-only characters."""
        # print(f"[*] Processing: {pdf_path.name}")
        raw_text = self.extract_text_from_pdf(pdf_path)
        if not raw_text:
            print(f"[-] No text extracted from {pdf_path.name}")
            return {"regex_format": "", "pattern_matching": ""}
        ascii_text = re.sub(r'[^\x00-\x7F]+', ' ', raw_text)
        regex_text = self.format_for_regex(ascii_text)
        pattern_text = self.format_for_pattern_matching(ascii_text)
        return {"regex_format": regex_text, "pattern_matching": pattern_text}

    def extract_all_pdfs(self) -> Dict[str, Dict[str, str]]:
        """
        Extract text from all PDF files in the data folder and display a snippet for each.
        """
        print(f"\n[*] Starting One-on-One PDF Extraction and Display from: {self.data_folder}")
        print("="*60)

        pdf_files = sorted(list(self.data_folder.glob("*.pdf")), key=lambda x: x.name)

        if not pdf_files:
            print(f"[-] No PDF files found in {self.data_folder}")
            return {}

        print(f"[+] Found {len(pdf_files)} PDF files. Processing now...\n")
        
        results = {}
        for pdf_file in pdf_files:
            extracted = self.extract_single_pdf(pdf_file)
            results[pdf_file.name] = extracted
            self.extracted_data['regex_format'][pdf_file.name] = extracted['regex_format']
            self.extracted_data['pattern_matching'][pdf_file.name] = extracted['pattern_matching']
            
            if extracted["regex_format"]:
                print(f"--- Extracted Snippet for: {pdf_file.name} ---")
                regex_text = extracted['regex_format']
                snippet = regex_text[:300] + "..." if len(regex_text) > 300 else regex_text
                print(snippet)
            else:
                print("--- No content extracted. ---")
            
            print("-" * 50 + "\n")

        print(f"[+] Successfully extracted text from {len(results)} PDF files.")
        return results
    
    # --- MODIFICATION START ---
    def save_extracted_text(self, output_folder: str = "extracted_texts"):
        """Save extracted texts to separate files using correct pathlib usage."""
        output_path = Path(output_folder)
        regex_folder = output_path / "regex_format"
        pattern_folder = output_path / "pattern_matching"
        
        # Create directories if they don't exist
        output_path.mkdir(exist_ok=True)
        regex_folder.mkdir(exist_ok=True)
        pattern_folder.mkdir(exist_ok=True)

        # Loop through all processed PDF names once
        for pdf_name in self.extracted_data['regex_format'].keys():
            # Get the filename without the extension (e.g., "10276858" from "10276858.pdf")
            file_stem = Path(pdf_name).stem

            # Save regex format
            regex_new_filename = f"{file_stem}_regex.txt"
            regex_filepath = regex_folder / regex_new_filename
            with open(regex_filepath, 'w', encoding='utf-8') as f:
                f.write(self.extracted_data['regex_format'][pdf_name])
            
            # Save pattern matching format
            pattern_new_filename = f"{file_stem}_pattern.txt"
            pattern_filepath = pattern_folder / pattern_new_filename
            with open(pattern_filepath, 'w', encoding='utf-8') as f:
                f.write(self.extracted_data['pattern_matching'][pdf_name])
                
        print(f"\n[+] Extracted texts saved to '{output_folder}'")
    # --- MODIFICATION END ---

    def get_extraction_stats(self) -> Dict[str, int]:
        """Get statistics about the extraction"""
        stats = {
            'total_pdfs': len(self.extracted_data['regex_format']),
            'successful_extractions': sum(1 for text in self.extracted_data['regex_format'].values() if text.strip()),
            'failed_extractions': sum(1 for text in self.extracted_data['regex_format'].values() if not text.strip()),
        }
        if stats['successful_extractions'] > 0:
            regex_lengths = [len(text) for text in self.extracted_data['regex_format'].values() if text.strip()]
            pattern_lengths = [len(text) for text in self.extracted_data['pattern_matching'].values() if text.strip()]
            stats['avg_regex_length'] = sum(regex_lengths) // len(regex_lengths)
            stats['avg_pattern_length'] = sum(pattern_lengths) // len(pattern_lengths)
        else:
            stats['avg_regex_length'] = 0
            stats['avg_pattern_length'] = 0
        return stats

    def search_keywords_demo(self, keywords: List[str]):
        """Demo function to show keyword searching in extracted texts"""
        print(f"\n{'='*60}")
        print("KEYWORD SEARCH DEMONSTRATION")
        print(f"{'='*60}\nSearching for keywords: {', '.join(keywords)}")
        for keyword in keywords:
            print(f"\n--- Results for '{keyword}' ---")
            found_count = 0
            for pdf_name, text in self.extracted_data['pattern_matching'].items():
                if keyword.lower() in text:
                    count = text.count(keyword.lower())
                    print(f"  > Found in '{pdf_name}': {count} occurrences")
                    found_count += 1
            if found_count == 0:
                print(f"  > No matches found for '{keyword}'")


def main():
    """Main function to demonstrate PDF extraction"""
    print("PDF EXTRACTOR FOR CV ATS SYSTEM")
    print("="*50)
    
    extractor = PDFExtractor("data")
    
    results = extractor.extract_all_pdfs()
    
    if not results:
        print("\n[-] No PDFs processed. Please check your data folder.")
        return
    
    stats = extractor.get_extraction_stats()
    print(f"\n[+] EXTRACTION STATISTICS:")
    print(f"    Total PDFs: {stats['total_pdfs']}")
    print(f"    Successful: {stats['successful_extractions']}")
    print(f"    Failed: {stats['failed_extractions']}")
    print(f"    Avg Regex Length: {stats['avg_regex_length']} chars")
    print(f"    Avg Pattern Length: {stats['avg_pattern_length']} chars")
    
    extractor.save_extracted_text()
    
    demo_keywords = ["python", "experience", "management", "data", "skills"]
    extractor.search_keywords_demo(demo_keywords)
    
    print(f"\n[+] PDF extraction process completed!")

if __name__ == "__main__":
    main()
