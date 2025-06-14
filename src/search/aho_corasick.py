from typing import List, Dict
from .multisearch_protocol import MultiPatternSearchAlgorithm

class AhoCorasickSearch(MultiPatternSearchAlgorithm):
    def __init__(self, patterns: List[str]):
        """
        desc
        """
        # TODO: bikin trie or apalah g tw
        ...

    def search_multi(self, text: str, patterns: List[str]) -> Dict[str, List[int]]:
        """
        desc
        """
        # TODO: traverse text, collect matches for each pattern
        # @return Dict[str, List[int]] -> Keynya setiap keyword
        # trus List[int] nya itu array of first index dari setiap occurencenya
        ...

