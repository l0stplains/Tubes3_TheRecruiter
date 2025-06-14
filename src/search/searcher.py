from typing import List, Dict, Union
from .search_abc import StringSearchAlgorithm
from .multisearch_protocol import MultiPatternSearchAlgorithm

class KeywordSearcher:
    """
    Perform single- or multi-pattern searches with configurable algorithms.

    Attributes:
        algorithm: Either a StringSearchAlgorithm (single-pattern)
                   or a MultiPatternSearchAlgorithm (multi-pattern).
        case_sensitive: If False, searches are case-insensitive.
        whole_word: If True, only whole-word matches are returned.
    """
    def __init__(
        self,
        algorithm: Union[StringSearchAlgorithm, MultiPatternSearchAlgorithm],
        case_sensitive: bool = False,
        whole_word: bool = False
    ):
        self.algorithm = algorithm
        self.case_sensitive = case_sensitive
        self.whole_word = whole_word

    def search(
        self,
        text: str,
        keywords: List[str]
    ) -> Dict[str, List[int]]:
        """
        Search for multiple keywords in `text`.

        Uses `search_multi` if the algorithm supports it, else loops over `search`.
        """
        processed = text if self.case_sensitive else text.lower()
        # Multi-pattern path
        if isinstance(self.algorithm, MultiPatternSearchAlgorithm):
            raw = self.algorithm.search_multi(
                processed,
                [kw if self.case_sensitive else kw.lower() for kw in keywords]
            )
        else:
            raw = {
                kw: self.algorithm.search(
                    processed,
                    kw if self.case_sensitive else kw.lower()
                )
                for kw in keywords
            }

        # Whole-word filtering
        results: Dict[str, List[int]] = {}
        for kw, idxs in raw.items():
            if self.whole_word:
                filtered = []
                term = kw if self.case_sensitive else kw.lower()
                for i in idxs:
                    start_ok = i == 0 or not processed[i-1].isalnum()
                    end_i = i + len(term)
                    end_ok = end_i == len(processed) or not processed[end_i].isalnum()
                    if start_ok and end_ok:
                        filtered.append(i)
                results[kw] = filtered
            else:
                results[kw] = idxs

        return results

