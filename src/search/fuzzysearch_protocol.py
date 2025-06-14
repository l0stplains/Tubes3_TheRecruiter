from typing import Protocol, runtime_checkable, List, Dict, Tuple

@runtime_checkable
class FuzzySearchAlgorithm(Protocol):
    def search_fuzzy(
        self,
        text: str,
        patterns: List[str],
        threshold: int
    ) -> Dict[str, List[Tuple[int, int]]]:
        """
        Approximate-match multiple patterns against `text`.

        Args:
            text: The text to search in.
            patterns: List of substrings to find approximately.
            threshold: Maximum allowed Levenshtein distance.

        Returns:
            A dict mapping each pattern to a list of (start_index, distance)
            for each approximate match whose distance <= threshold.
        """
        ...

