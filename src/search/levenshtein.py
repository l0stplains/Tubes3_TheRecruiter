import math
from typing import List, Dict, Tuple
from .fuzzysearch_protocol import FuzzySearchAlgorithm

class LevenshteinSearch(FuzzySearchAlgorithm):
    def __init__(self, tolerance: float):
        """
        Build a fuzzy searcher using a relative Levenshtein tolerance (0–1).
        """
        if not 0 <= tolerance <= 1:
            raise ValueError("Tolerance must be a float between 0 and 1.")
        self.tolerance = tolerance

    def search_fuzzy(
        self,
        text: str,
        patterns: List[str],
        tolerance: float = None
    ) -> Dict[str, List[Tuple[int, int]]]:
        """
        For each pattern, slide a window of length len(pattern) over text,
        compute the full Levenshtein distance, and record matches <= tolerance.
        """
        from codecs import decode  # no extra deps

        # use instance tolerance if none passed explicitly
        tol = tolerance if tolerance is not None else self.tolerance
        if not 0 <= tol <= 1:
            raise ValueError("Tolerance must be between 0 and 1.")
        results: Dict[str, List[Tuple[int, int]]] = {}

        for pat in patterns:
            m = len(pat)
            matches: List[Tuple[int, int]] = []
            if m == 0:
                # empty pattern matches at every position with distance 0
                matches = [(i, 0) for i in range(len(text) + 1)]
            else:
                max_edits = math.ceil(m * tol)
                for i in range(len(text) - m + 1):
                    window = text[i : i + m]
                    d = self._levenshtein(window, pat, max_edits)
                    if d <= max_edits:
                        matches.append((i, d))
            results[pat] = matches

        return results

    def _levenshtein(self, s1: str, s2: str, max_dist: int) -> int:
        """
        Standard DP, but stop early if all values in a row exceed max_dist.
        """
        n, m = len(s1), len(s2)
        # rows: previous and current
        prev = list(range(m + 1))
        curr = [0] * (m + 1)

        for i in range(1, n + 1):
            curr[0] = i
            min_row = curr[0]
            for j in range(1, m + 1):
                cost = 0 if s1[i - 1] == s2[j - 1] else 1
                curr[j] = min(
                    prev[j] + 1, # deletion
                    curr[j - 1] + 1, # insertion
                    prev[j - 1] + cost # substitution
                )
                min_row = min(min_row, curr[j])
            if min_row > max_dist:
                return max_dist + 1
            prev, curr = curr, prev

        return prev[m]

