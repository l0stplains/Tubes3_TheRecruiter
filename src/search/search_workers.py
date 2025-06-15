from pathlib import Path
from src.core.extractor import PDFExtractor
from src.search.boyer_moore import BoyerMooreSearch
from src.search.aho_corasick import AhoCorasickSearch
from src.search.kmp import KMPSearch
from src.search.searcher import KeywordSearcher
from typing import Tuple, List, Dict, Any

def search_exact_worker(
    detail: Dict[str, Any],
    keywords: List[str],
    algo_name: str,
    data_root: str
) -> Dict[str, Any]:
    """
    Perform exact-match (BM or KMP) on a single CV and record missing keywords.
    """
    # Build a Path object so extractor.pdf_path.name works
    pdf_path = Path(data_root) / detail["cv_path"]

    extractor = PDFExtractor(data_root)
    # Pass a Path, not a str
    text = extractor.extract_single_pdf(pdf_path)["pattern_matching"]

    # Choose algorithm
    algo = None
    if algo_name == "BM":
        algo = BoyerMooreSearch() 
    elif algo_name == "KMP":
        algo = KMPSearch()
    else:
        algo = AhoCorasickSearch(keywords)

    ks   = KeywordSearcher(algo, case_sensitive=False, whole_word=False)
    exact = ks.search(text, keywords)
    count = sum(len(v) for v in exact.values())
    missing = [kw for kw, locs in exact.items() if not locs]

    return {
        "detail":      detail,
        "text":        text,
        "exact_raw":   exact,
        "exact_count": count,
        "missing":     missing
    }

def search_fuzzy_worker(
    idx: int,
    text: str,
    missing: List[str],
    threshold: int
) -> Tuple[int, Dict[str, List[Tuple[int,int]]]]:
    """
    Perform fuzzy-match (Levenshtein) on one CV’s missing keywords.
    Returns (original index, fuzzy_raw) so results can be merged back.
    """
    from src.search.levenshtein import LevenshteinSearch
    from src.search.searcher import KeywordSearcher

    # instantiate once per worker
    fuzzy_algo = LevenshteinSearch(threshold=threshold)
    ks_fuzzy   = KeywordSearcher(fuzzy_algo, case_sensitive=False)

    if not missing:
        return idx, {}

    fuzzy = ks_fuzzy.search(text, missing)
    return idx, fuzzy

