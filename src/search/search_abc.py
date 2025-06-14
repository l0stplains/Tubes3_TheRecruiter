from abc import ABC, abstractmethod
from typing import List

class StringSearchAlgorithm(ABC):
    @abstractmethod
    def search(self, text: str, pattern: str) -> List[int]:
        """
        Find occurrences of a single pattern.

        Args:
            text: The text to search within.
            pattern: The substring to find.

        Returns:
            A list of starting indices where `pattern` is found in `text`.
        """
        ...
