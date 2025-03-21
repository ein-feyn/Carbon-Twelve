"""
Word Counter module for the Digital Notebook.

This module implements the weighted word counting system as described in the requirements.
It assigns weights to different text elements and provides methods for counting and analyzing text.
"""
import re
from typing import Dict, List, Tuple, Set, Optional, Any
import string


class WordCounter:
    """
    Implements a weighted word counting system.
    
    This class provides methods for counting words in text using a weight-based approach,
    where letters have weights between 0 and 1, and complete words sum to 1.
    """
    
    def __init__(self, letter_weight: float = 0.5):
        """
        Initialize the word counter with specified weights.
        
        Args:
            letter_weight: Weight to assign to letters (between 0 and 1)
        """
        self.letter_weight = letter_weight
        
        # Initialize character weights
        self.char_weights = {}
        
        # Assign weights to different character types
        # Letters get the specified letter_weight
        for char in string.ascii_letters:
            self.char_weights[char] = letter_weight
            
        # Spaces, punctuation, and other characters get zero weight
        for char in string.whitespace + string.punctuation + string.digits:
            self.char_weights[char] = 0.0
            
        # Special handling for the first word in a line/document
        self.first_word_adjustment = 0.25
    
    def count_words(self, text: str) -> int:
        """
        Count the number of words in the text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Number of words in the text
        """
        # Simple approach: split on whitespace
        words = re.findall(r'\b\w+\b', text)
        return len(words)
    
    def weighted_count(self, text: str) -> float:
        """
        Perform a weighted count of the text.
        
        Each word contributes a weight of 1 to the total.
        
        Args:
            text: Text to analyze
            
        Returns:
            Weighted count of the text
        """
        return float(self.count_words(text))
    
    def get_character_weights(self, text: str) -> Dict[str, float]:
        """
        Calculate the total weight contributed by each character type.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary mapping character types to their total weight
        """
        char_totals = {}
        
        for char in text:
            if char not in char_totals:
                char_totals[char] = 0.0
            
            weight = self.char_weights.get(char, 0.0)
            char_totals[char] += weight
        
        return char_totals
    
    def analyze_text(self, text: str) -> Dict[str, Any]:
        """
        Perform comprehensive analysis of the text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with various analysis metrics
        """
        word_count = self.count_words(text)
        weighted_count = self.weighted_count(text)
        char_weights = self.get_character_weights(text)
        
        # Count characters by type
        letter_count = sum(1 for c in text if c in string.ascii_letters)
        digit_count = sum(1 for c in text if c in string.digits)
        punctuation_count = sum(1 for c in text if c in string.punctuation)
        whitespace_count = sum(1 for c in text if c in string.whitespace)
        
        # Calculate average word length
        words = re.findall(r'\b\w+\b', text)
        avg_word_length = sum(len(word) for word in words) / max(1, len(words))
        
        return {
            "word_count": word_count,
            "weighted_count": weighted_count,
            "character_counts": {
                "letters": letter_count,
                "digits": digit_count,
                "punctuation": punctuation_count,
                "whitespace": whitespace_count,
                "total": len(text)
            },
            "character_weights": char_weights,
            "average_word_length": avg_word_length,
        }
    
    def plot_data(self, text: str) -> Dict[str, List[float]]:
        """
        Generate data for plotting word count progression.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with data points for plotting
        """
        words = re.findall(r'\b\w+\b', text)
        
        # Calculate cumulative word counts
        cumulative_counts = []
        running_count = 0
        
        for i, word in enumerate(words):
            running_count += 1
            cumulative_counts.append(running_count)
        
        # Generate x-axis values (word positions)
        x_values = list(range(1, len(words) + 1))
        
        return {
            "x_values": x_values,
            "y_values": cumulative_counts
        }
    
    def get_word_weights(self, words: List[str]) -> Dict[str, float]:
        """
        Calculate the weight of each word.
        
        In this implementation, each word has a weight of 1.
        
        Args:
            words: List of words to calculate weights for
            
        Returns:
            Dictionary mapping words to their weights
        """
        return {word: 1.0 for word in words}
    
    def custom_weighted_count(self, text: str, char_weights: Dict[str, float]) -> float:
        """
        Calculate the weighted count using custom character weights.
        
        Args:
            text: Text to analyze
            char_weights: Dictionary mapping characters to weights
            
        Returns:
            Custom weighted count of the text
        """
        # Split the text into words
        words = re.findall(r'\b\w+\b', text)
        
        # Count each word as 1
        return float(len(words))
