from typing import List, Dict, Protocol, runtime_checkable

@runtime_checkable
class MultiPatternSearchAlgorithm(Protocol):
    def search_multi(self, text: str, patterns: List[str]) -> Dict[str, List[int]]:
        """
        Find occurrences for multiple patterns in one pass.

        Args:
            text: The text to search within.
            patterns: A list of substrings to find.

        Returns:
            A dict mapping each pattern to its list of starting indices in `text`.
        """
        ...
