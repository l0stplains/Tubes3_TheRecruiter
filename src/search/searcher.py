from typing import (
    List, Dict, Union, Tuple
)
from re import compile as rx, escape
from .search_abc import StringSearchAlgorithm
from .multisearch_protocol import MultiPatternSearchAlgorithm
from .fuzzysearch_protocol import FuzzySearchAlgorithm

class KeywordSearcher:
    """
    Dispatch to exact‑match or fuzzy‑match based on the algorithm instance.

    Args:
      algorithm: 
        - exact-match: StringSearchAlgorithm or MultiPatternSearchAlgorithm  
        - fuzzy-match: FuzzySearchAlgorithm  
      case_sensitive: If False, lower‑cases both text and patterns.  
      whole_word: If True, applies word‑boundary filtering (exact only).
    """
    def __init__(
        self,
        algorithm: Union[
            StringSearchAlgorithm,
            MultiPatternSearchAlgorithm,
            FuzzySearchAlgorithm
        ],
        case_sensitive: bool = False,
        whole_word: bool = False
    ):
        self.algorithm     = algorithm
        self.case_sensitive = case_sensitive
        self.whole_word     = whole_word

    def search(
            self,
            text: str,
            keywords: List[str]
        ) -> Dict[str, Union[List[int], List[Tuple[int,int]]]]:
            # normalize case once
            proc_text = text if self.case_sensitive else text.lower()
            proc_keys = [
                kw if self.case_sensitive else kw.lower()
                for kw in keywords
            ]

            norm_to_orig: Dict[str, str] = {
                nk: orig for nk, orig in zip(proc_keys, keywords)
            }

            if isinstance(self.algorithm, FuzzySearchAlgorithm):
                raw = self.algorithm.search_fuzzy(proc_text, proc_keys)
            else:
                if isinstance(self.algorithm, MultiPatternSearchAlgorithm):
                    raw = self.algorithm.search_multi(proc_text, proc_keys)
                else:
                    raw = {
                        nk: self.algorithm.search(proc_text, nk)
                        for nk in proc_keys
                    }

                if self.whole_word:
                    filtered: Dict[str, List[int]] = {nk: [] for nk in proc_keys}
                    # build a combined word‑boundary regex
                    pattern = rx(r'\b(' + '|'.join(map(escape, proc_keys)) + r')\b')
                    for m in pattern.finditer(proc_text):
                        filtered[m.group(1)].append(m.start())
                    raw = filtered

            return {
                norm_to_orig.get(nk, nk): positions
                for nk, positions in raw.items()
            }
