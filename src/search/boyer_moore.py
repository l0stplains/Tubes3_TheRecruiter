from typing import List
from .search_abc import StringSearchAlgorithm

class BoyerMooreSearch(StringSearchAlgorithm):
    def search(self, text: str, pattern: str) -> List[int]:
        n, m = len(text), len(pattern)
        if m == 0:
            return list(range(n + 1))

        # last occurrence function table
        lo_func = {c: -1 for c in set(text + pattern)}
        for idx, c in enumerate(pattern):
            lo_func[c] = idx

        result: List[int] = []
        shift = 0
        while shift <= n - m:
            j = m - 1

            # scan (from right)
            while j >= 0 and pattern[j] == text[shift + j]:
                j -= 1

            if j < 0:
                result.append(shift)
                next_idx = shift + m

                # shift efficiently to search next occurrence
                shift += m - lo_func.get(text[next_idx], -1) if next_idx < n else 1
            # mismatch
            else:
                # compute raw skip = j - k
                k = lo_func.get(text[shift + j], -1)
                raw_skip = j - k

                # case 1: if x occurs at k <= j, then raw_skip = j − k > 0,
                #   so we align pattern[k] under text[i].
                # case 2: if x occurs in pattern but k > j, then raw_skip <= 0,
                #   and we do max(1, raw_skip) -> 1, shifting by one.
                # case 3: if x not in pattern, k = −1, so raw_skip = j − (−1) = j+1,
                #   shifting pattern fully past x.
                shift += max(1, raw_skip)
        return result

