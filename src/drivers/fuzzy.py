from src.search.levenshtein import LevenshteinSearch
from src.search.boyer_moore import BoyerMooreSearch
from src.search.searcher import KeywordSearcher

def run():
    text = "POV ngetik di hp pske jwwmpoll"
    keywords = ["ngetik", "jempol"]

    # boyer
    exact_algo = BoyerMooreSearch()
    ks_exact   = KeywordSearcher(exact_algo, whole_word=False)
    print(ks_exact.search(text, keywords))

    # fuzzy‑match
    fuzzy_algo = LevenshteinSearch(threshold=2)
    ks_fuzzy   = KeywordSearcher(fuzzy_algo)
    print(ks_fuzzy.search(text, keywords))


