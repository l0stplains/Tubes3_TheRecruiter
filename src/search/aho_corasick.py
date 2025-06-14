from collections import deque, defaultdict
from typing import Dict, List, Optional, Protocol, runtime_checkable
from .multisearch_protocol import MultiPatternSearchAlgorithm

class TrieNode:
    """
    @brief Node in the Trie data structure for Aho-Corasick algorithm.
    """
    def __init__(self) -> None:
        self.children: Dict[str, 'TrieNode'] = {}
        self.is_end_of_pattern: bool = False
        self.pattern: Optional[str] = None
        self.failure: Optional['TrieNode'] = None
        self.output: List[str] = []

class AhoCorasickSearch(MultiPatternSearchAlgorithm):
    """
    @brief Aho-Corasick algorithm implementation for multi-pattern string matching.
    """
    
    def __init__(self, patterns: List[str]) -> None:
        """
        @brief Initialize and build the Aho-Corasick automaton.
        @param patterns List of string patterns to search for
        @throw TypeError If patterns is not a list of strings
        """
        if not isinstance(patterns, list):
            raise TypeError("Patterns must be a list of strings.")
            
        self.root = TrieNode()
        self.patterns = patterns
        self._build_trie(patterns)
        self._build_failure_function()

    def _build_trie(self, patterns: List[str]) -> None:
        """
        @brief Build the trie structure from all input patterns.
        @param patterns List of patterns to insert into the trie
        """
        for pattern in patterns:
            if not pattern:
                continue
            
            current = self.root
            for char in pattern:
                if char not in current.children:
                    current.children[char] = TrieNode()
                current = current.children[char]
            
            current.is_end_of_pattern = True
            current.pattern = pattern
            current.output.append(pattern)

    def _build_failure_function(self) -> None:
        """
        @brief Build failure links for efficient pattern matching.
        """
        queue = deque()
        
        for child in self.root.children.values():
            child.failure = self.root
            queue.append(child)
        
        while queue:
            current = queue.popleft()
            
            for char, child in current.children.items():
                queue.append(child)
                
                failure = current.failure
                while failure is not None and char not in failure.children:
                    failure = failure.failure
                
                if failure is not None:
                    child.failure = failure.children[char]
                    child.output.extend(child.failure.output)
                else:
                    child.failure = self.root

    def search_multi(self, text: str, patterns: List[str]) -> Dict[str, List[int]]:
        """
        @brief Search for all patterns in the given text.
        @param text The input text to search within
        @param patterns List of patterns to find (ignored - uses patterns from constructor)
        @return Dictionary mapping each found pattern to list of starting positions
        """
        if not text:
            return {}
        
        results = defaultdict(list)
        current = self.root
        
        for i, char in enumerate(text):
            while current is not None and char not in current.children:
                current = current.failure
            
            if current is None:
                current = self.root
                continue
            
            current = current.children[char]
            
            if current.output:
                for matched_pattern in current.output:
                    start_pos = i - len(matched_pattern) + 1
                    results[matched_pattern].append(start_pos)
        
        return dict(results)

    def search_patterns(self, text: str) -> Dict[str, List[int]]:
        """
        @brief Convenience method to search for patterns set during initialization.
        @param text The input text to search within
        @return Dictionary mapping each found pattern to list of starting positions
        """
        return self.search_multi(text, self.patterns)