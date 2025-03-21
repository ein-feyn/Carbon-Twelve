"""
Text Analyzer module for the Digital Notebook.

This module provides text analysis capabilities beyond simple word counting,
integrating with the word counter to provide comprehensive text insights.
"""
import re
import string
from typing import Dict, List, Any, Optional
from collections import Counter

from .word_counter import WordCounter


class TextAnalyzer:
    """
    Provides comprehensive text analysis functionality.
    
    This class builds on the word counter to provide additional insights into text,
    including readability metrics, keyword extraction, and more.
    """
    
    def __init__(self, word_counter: Optional[WordCounter] = None):
        """
        Initialize the text analyzer.
        
        Args:
            word_counter: Optional WordCounter instance to use
                          (will create a new one if not provided)
        """
        self.word_counter = word_counter or WordCounter()
        
    def analyze_text(self, text: str) -> Dict[str, Any]:
        """
        Perform comprehensive analysis of the text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with various analysis metrics
        """
        # Get basic word count analysis from the word counter
        basic_analysis = self.word_counter.analyze_text(text)
        
        # Add additional analysis
        readability = self.calculate_readability(text)
        keywords = self.extract_keywords(text)
        sentence_count = len(re.split(r'[.!?]+', text))
        
        # Combine the analyses
        analysis = {
            **basic_analysis,
            "readability": readability,
            "keywords": keywords,
            "sentence_count": sentence_count,
        }
        
        return analysis
    
    def calculate_readability(self, text: str) -> Dict[str, float]:
        """
        Calculate readability metrics for the text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with readability metrics
        """
        word_count = self.word_counter.count_words(text)
        
        # Count sentences (rough approximation)
        sentences = re.split(r'[.!?]+', text)
        sentence_count = max(1, len(sentences) - 1)  # Account for potential empty string at end
        
        # Count syllables (rough approximation)
        syllable_count = self._count_syllables(text)
        
        # Calculate Flesch-Kincaid Grade Level
        if word_count > 0 and sentence_count > 0:
            flesch_kincaid = 0.39 * (word_count / sentence_count) + 11.8 * (syllable_count / word_count) - 15.59
        else:
            flesch_kincaid = 0
        
        # Calculate Flesch Reading Ease
        if word_count > 0 and sentence_count > 0:
            flesch_reading_ease = 206.835 - 1.015 * (word_count / sentence_count) - 84.6 * (syllable_count / word_count)
        else:
            flesch_reading_ease = 0
            
        return {
            "flesch_kincaid_grade": flesch_kincaid,
            "flesch_reading_ease": flesch_reading_ease,
            "average_words_per_sentence": word_count / max(1, sentence_count),
            "average_syllables_per_word": syllable_count / max(1, word_count),
        }
    
    def _count_syllables(self, text: str) -> int:
        """
        Count the number of syllables in the text (approximate).
        
        This is a simplified approach and won't be entirely accurate.
        
        Args:
            text: Text to analyze
            
        Returns:
            Approximate number of syllables
        """
        # Convert to lowercase
        text = text.lower()
        
        # Replace punctuation with spaces
        for p in string.punctuation:
            text = text.replace(p, " ")
            
        # Split into words
        words = text.split()
        
        # Count syllables
        count = 0
        for word in words:
            word_count = self._count_syllables_in_word(word)
            count += word_count
            
        return count
    
    def _count_syllables_in_word(self, word: str) -> int:
        """
        Count the number of syllables in a word (approximate).
        
        Args:
            word: Word to analyze
            
        Returns:
            Approximate number of syllables
        """
        # Special cases
        if len(word) <= 3:
            return 1
            
        # Count vowel groups
        count = 0
        vowels = "aeiouy"
        prev_is_vowel = False
        
        for char in word:
            is_vowel = char in vowels
            
            if is_vowel and not prev_is_vowel:
                count += 1
                
            prev_is_vowel = is_vowel
            
        # Adjust for silent e at end
        if word.endswith('e') and len(word) > 2 and word[-2] not in vowels:
            count -= 1
            
        # Ensure at least one syllable
        return max(1, count)
    
    def extract_keywords(self, text: str, top_n: int = 5) -> List[str]:
        """
        Extract the most important keywords from the text.
        
        Args:
            text: Text to analyze
            top_n: Number of top keywords to return
            
        Returns:
            List of the most important keywords
        """
        # Convert to lowercase
        text = text.lower()
        
        # Remove punctuation
        for p in string.punctuation:
            text = text.replace(p, " ")
            
        # Split into words
        words = text.split()
        
        # Remove common stop words
        stop_words = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
            "with", "by", "about", "of", "is", "are", "was", "were", "be", "been",
            "being", "have", "has", "had", "do", "does", "did", "i", "you", "he",
            "she", "it", "we", "they", "them", "their", "this", "that", "these",
            "those", "my", "your", "his", "her", "its", "our", "their"
        }
        
        filtered_words = [word for word in words if word not in stop_words and len(word) > 2]
        
        # Count word frequency
        word_counts = Counter(filtered_words)
        
        # Get the top N keywords
        return [word for word, _ in word_counts.most_common(top_n)]
    
    def track_progress(self, text_history: List[str]) -> Dict[str, Any]:
        """
        Track progress over a history of text versions.
        
        Args:
            text_history: List of text versions in chronological order
            
        Returns:
            Dictionary with progress metrics
        """
        word_counts = [self.word_counter.count_words(text) for text in text_history]
        
        # Calculate changes between versions
        word_deltas = [
            word_counts[i] - word_counts[i-1] if i > 0 else word_counts[0]
            for i in range(len(word_counts))
        ]
        
        # Calculate cumulative word counts
        cumulative_counts = []
        running_total = 0
        for count in word_counts:
            running_total = count  # Use the actual count, not the delta
            cumulative_counts.append(running_total)
        
        # Calculate other metrics for each version
        analyses = [self.analyze_text(text) for text in text_history]
        
        return {
            "word_counts": word_counts,
            "word_deltas": word_deltas,
            "cumulative_counts": cumulative_counts,
            "analyses": analyses,
        }
    
    def compare_texts(self, text1: str, text2: str) -> Dict[str, Any]:
        """
        Compare two text samples.
        
        Args:
            text1: First text to compare
            text2: Second text to compare
            
        Returns:
            Dictionary with comparison metrics
        """
        analysis1 = self.analyze_text(text1)
        analysis2 = self.analyze_text(text2)
        
        # Extract keywords from both texts
        keywords1 = set(self.extract_keywords(text1, top_n=20))
        keywords2 = set(self.extract_keywords(text2, top_n=20))
        
        # Find common and unique keywords
        common_keywords = keywords1.intersection(keywords2)
        unique_to_1 = keywords1 - keywords2
        unique_to_2 = keywords2 - keywords1
        
        return {
            "text1_analysis": analysis1,
            "text2_analysis": analysis2,
            "common_keywords": list(common_keywords),
            "unique_to_text1": list(unique_to_1),
            "unique_to_text2": list(unique_to_2),
            "word_count_difference": analysis2["word_count"] - analysis1["word_count"],
            "readability_difference": {
                "flesch_kincaid_grade": analysis2["readability"]["flesch_kincaid_grade"] - analysis1["readability"]["flesch_kincaid_grade"],
                "flesch_reading_ease": analysis2["readability"]["flesch_reading_ease"] - analysis1["readability"]["flesch_reading_ease"],
            }
        }
