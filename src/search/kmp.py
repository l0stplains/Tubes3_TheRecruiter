from typing import List
from .search_abc import StringSearchAlgorithm

class KMPSearch(StringSearchAlgorithm):
    def search(self, text: str, pattern: str) -> List[int]:
        n, m = len(text), len(pattern)
        if m == 0:
            return list(range(n + 1))

        # calculate border function
        b_func = self._compute_border_function(pattern)

        result: List[int] = []
        i = 0
        j = 0

        while (i < n):
            # matched character
            if text[i] == pattern[j]:
                i += 1
                j += 1

            # matched whole keyword
            if (j == m):
                result.append(i - j)
                j = b_func[j - 1]

            elif i < n and pattern[j] != text[i]:
                if j != 0:
                    j = b_func[j - 1]
                else:
                    i += 1

        return result


    def _compute_border_function(self, pattern: str) -> List[int]:
        m = len(pattern)
        b_func = [0] * m
        j = 0
        i = 1

        while i < m:
            if pattern[i] == pattern[j]:
                j += 1
                b_func[i] = j
                i += 1
            else:
                if j != 0:
                    # Consider the previous longest prefix suffix
                    j = b_func[j - 1]
                else:
                    b_func[i] = 0
                    i += 1
        
        return b_func
        
        

