"""
Word counting utilities for the Digital Notebook application.

This module provides functionality for counting and analyzing text in the notebook.
"""

class WordCounter:
    """Class for counting and analyzing words in a notebook."""
    
    def __init__(self, notebook=None):
        """Initialize the word counter.
        
        Args:
            notebook: The notebook to analyze.
        """
        self.notebook = notebook
    
    def set_notebook(self, notebook):
        """Set the notebook to analyze.
        
        Args:
            notebook: The notebook to analyze.
        """
        self.notebook = notebook
    
    def count_words_in_page(self, page_id):
        """Count the number of words in a page.
        
        Args:
            page_id: The ID of the page to count words in.
            
        Returns:
            int: The number of words in the page.
        """
        if not self.notebook:
            return 0
            
        try:
            page = self.notebook.get_page(page_id)
            words = page.content.split()
            return len(words)
        except KeyError:
            return 0
    
    def count_total_words(self):
        """Count the total number of words in the notebook.
        
        Returns:
            int: The total number of words.
        """
        if not self.notebook:
            return 0
            
        total = 0
        for page in self.notebook.pages.values():
            words = page.content.split()
            total += len(words)
        return total
    
    def get_word_frequency(self):
        """Get the frequency of each word in the notebook.
        
        Returns:
            dict: A dictionary mapping words to their frequencies.
        """
        if not self.notebook:
            return {}
            
        frequency = {}
        for page in self.notebook.pages.values():
            words = page.content.lower().split()
            for word in words:
                # Remove punctuation
                word = word.strip('.,;:!?()[]{}"\'-')
                if word:
                    frequency[word] = frequency.get(word, 0) + 1
        return frequency
    
    def get_page_word_count(self):
        """Get the word count for each page.
        
        Returns:
            dict: A dictionary mapping page IDs to word counts.
        """
        if not self.notebook:
            return {}
            
        counts = {}
        for page_id in self.notebook.pages:
            counts[page_id] = self.count_words_in_page(page_id)
        return counts
    
    def get_weighted_word_count(self, weights=None):
        """Get weighted word count based on importance.
        
        Args:
            weights: A dictionary mapping words to their weights.
            
        Returns:
            float: The weighted word count.
        """
        if not self.notebook or not weights:
            return self.count_total_words()
            
        weighted_count = 0
        for page in self.notebook.pages.values():
            words = page.content.lower().split()
            for word in words:
                # Remove punctuation
                word = word.strip('.,;:!?()[]{}"\'-')
                if word in weights:
                    weighted_count += weights[word]
                else:
                    weighted_count += 1
        return weighted_count
    
    def get_most_common_words(self, n=10):
        """Get the most common words in the notebook.
        
        Args:
            n: The number of words to return.
            
        Returns:
            list: A list of (word, count) tuples.
        """
        frequency = self.get_word_frequency()
        sorted_words = sorted(frequency.items(), key=lambda x: x[1], reverse=True)
        return sorted_words[:n]