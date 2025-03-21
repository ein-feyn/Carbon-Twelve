"""
Utility components for the Digital Notebook application.

This package contains utility classes for search and word counting.
"""

from src.utils.search import SearchEngine, SearchResult
from src.utils.word_counter import WordCounter
from src.utils.config import Config

__all__ = ["SearchEngine", "SearchResult", "WordCounter", "Config"]
