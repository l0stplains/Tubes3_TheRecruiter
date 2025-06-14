from src.search.boyer_moore import BoyerMooreSearch
from src.search.searcher import KeywordSearcher

def run():
    text = (
        "This is a simple example text to test Boyer-Moore search. "
        "The text contains multiple occurrences of 'test' and 'text', "
        "and even some repeated words: test, text, test."
        "and even multi word: Boyer-Moore search, wholeword"
    )
    keywords = ["test", "text", "absent", "Boyer-Moore search", "whole", "wholeword"]

    bm_algo = BoyerMooreSearch()

    # wrap it in searcher
    searcher = KeywordSearcher(
        algorithm=bm_algo,
        case_sensitive=False,
        whole_word=True
    )

    results = searcher.search(text, keywords)

    for kw, positions in results.items():
        if positions:
            print(f"Keyword '{kw}' found at positions: {positions}")
        else:
            print(f"Keyword '{kw}' not found.")

    for kw, positions in results.items():
        if positions:
            print(f"Keyword '{kw}'")
            for i in positions:
                print(f"{i}: {text[i:i+len(kw)]}")
