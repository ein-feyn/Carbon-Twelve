"""
Search module for the Digital Notebook.

This module provides search functionality for finding content in the notebook.
"""
import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass

from src.core.notebook import Notebook
from src.core.page import Page


@dataclass
class SearchResult:
    """Represents a search result from the notebook."""
    page: Page
    content_snippet: str
    match_start: int
    match_end: int
    relevance_score: float


class SearchEngine:
    """
    Provides search functionality for notebooks.
    
    This class implements various search algorithms to find content in the notebook.
    """
    
    def __init__(self, notebook: Optional[Notebook] = None):
        """
        Initialize the search engine.
        
        Args:
            notebook: Optional notebook to search within
        """
        self.notebook = notebook
        self.context_size = 50  # Characters of context to include around matches
    
    def set_notebook(self, notebook: Notebook) -> None:
        """
        Set the notebook to search within.
        
        Args:
            notebook: The notebook to search
        """
        self.notebook = notebook
    
    def basic_search(self, query: str, case_sensitive: bool = False) -> List[SearchResult]:
        """
        Perform a basic text search in the notebook.
        
        Args:
            query: Text to search for
            case_sensitive: Whether the search should be case-sensitive
            
        Returns:
            List of SearchResult objects
            
        Raises:
            ValueError: If no notebook has been set
        """
        if self.notebook is None:
            raise ValueError("No notebook has been set for search")
        
        results = []
        
        # Prepare the search query
        if not case_sensitive:
            pattern = re.compile(re.escape(query), re.IGNORECASE)
        else:
            pattern = re.compile(re.escape(query))
        
        # Search through all pages
        for page in self.notebook.pages.values():
            # Search in the page content
            for match in pattern.finditer(page.content):
                start, end = match.span()
                
                # Extract a snippet of context around the match
                content_start = max(0, start - self.context_size)
                content_end = min(len(page.content), end + self.context_size)
                
                # Create the content snippet
                if content_start > 0:
                    prefix = "..."
                else:
                    prefix = ""
                    
                if content_end < len(page.content):
                    suffix = "..."
                else:
                    suffix = ""
                    
                snippet = prefix + page.content[content_start:content_end] + suffix
                
                # Calculate a simple relevance score (multiple matches in the same page rank higher)
                score = 1.0
                
                # Add to results
                result = SearchResult(
                    page=page,
                    content_snippet=snippet,
                    match_start=start,
                    match_end=end,
                    relevance_score=score
                )
                results.append(result)
        
        # Sort by relevance score (descending)
        results.sort(key=lambda r: r.relevance_score, reverse=True)
        
        return results
    
    def advanced_search(
        self, 
        query: str, 
        case_sensitive: bool = False,
        whole_words: bool = False,
        include_page_names: bool = True
    ) -> List[SearchResult]:
        """
        Perform an advanced search with more options.
        
        Args:
            query: Text to search for
            case_sensitive: Whether the search should be case-sensitive
            whole_words: Whether to match whole words only
            include_page_names: Whether to search in page names
            
        Returns:
            List of SearchResult objects
            
        Raises:
            ValueError: If no notebook has been set
        """
        if self.notebook is None:
            raise ValueError("No notebook has been set for search")
        
        results = []
        
        # Prepare the search query
        flags = 0 if case_sensitive else re.IGNORECASE
        
        if whole_words:
            pattern = re.compile(r'\b' + re.escape(query) + r'\b', flags)
        else:
            pattern = re.compile(re.escape(query), flags)
        
        # Search through all pages
        for page in self.notebook.pages.values():
            # Calculate page relevance score
            page_score = 0.0
            
            # Search in the page content
            content_matches = list(pattern.finditer(page.content))
            page_score += len(content_matches) * 1.0
            
            # Search in the page name if requested
            name_match = None
            if include_page_names and pattern.search(page.name):
                name_match = pattern.search(page.name)
                page_score += 2.0  # Matches in titles are weighted more heavily
            
            # Process content matches
            for match in content_matches:
                start, end = match.span()
                
                # Extract a snippet of context around the match
                content_start = max(0, start - self.context_size)
                content_end = min(len(page.content), end + self.context_size)
                
                # Create the content snippet
                if content_start > 0:
                    prefix = "..."
                else:
                    prefix = ""
                    
                if content_end < len(page.content):
                    suffix = "..."
                else:
                    suffix = ""
                    
                snippet = prefix + page.content[content_start:content_end] + suffix
                
                # Add to results
                result = SearchResult(
                    page=page,
                    content_snippet=snippet,
                    match_start=start,
                    match_end=end,
                    relevance_score=page_score
                )
                results.append(result)
            
            # Process name match if any
            if name_match:
                start, end = name_match.span()
                
                # Add to results
                result = SearchResult(
                    page=page,
                    content_snippet=f"[Page Name]: {page.name}",
                    match_start=start,
                    match_end=end,
                    relevance_score=page_score
                )
                results.append(result)
        
        # Sort by relevance score (descending)
        results.sort(key=lambda r: r.relevance_score, reverse=True)
        
        return results
    
    def regex_search(self, pattern: str) -> List[SearchResult]:
        """
        Perform a search using regular expressions.
        
        Args:
            pattern: Regular expression pattern to match
            
        Returns:
            List of SearchResult objects
            
        Raises:
            ValueError: If no notebook has been set
            re.error: If the regular expression is invalid
        """
        if self.notebook is None:
            raise ValueError("No notebook has been set for search")
        
        results = []
        
        # Compile the regex pattern
        try:
            regex = re.compile(pattern)
        except re.error as e:
            raise re.error(f"Invalid regular expression: {e}")
        
        # Search through all pages
        for page in self.notebook.pages.values():
            # Search in the page content
            for match in regex.finditer(page.content):
                start, end = match.span()
                
                # Extract a snippet of context around the match
                content_start = max(0, start - self.context_size)
                content_end = min(len(page.content), end + self.context_size)
                
                # Create the content snippet
                if content_start > 0:
                    prefix = "..."
                else:
                    prefix = ""
                    
                if content_end < len(page.content):
                    suffix = "..."
                else:
                    suffix = ""
                    
                snippet = prefix + page.content[content_start:content_end] + suffix
                
                # Calculate a simple relevance score
                score = 1.0
                
                # Add to results
                result = SearchResult(
                    page=page,
                    content_snippet=snippet,
                    match_start=start,
                    match_end=end,
                    relevance_score=score
                )
                results.append(result)
        
        # Sort by relevance score (descending)
        results.sort(key=lambda r: r.relevance_score, reverse=True)
        
        return results
    
    def search_by_keywords(self, keywords: List[str]) -> List[SearchResult]:
        """
        Search for pages that contain all the specified keywords.
        
        Args:
            keywords: List of keywords to search for
            
        Returns:
            List of SearchResult objects
            
        Raises:
            ValueError: If no notebook has been set
        """
        if self.notebook is None:
            raise ValueError("No notebook has been set for search")
        
        results = []
        
        # Create patterns for each keyword
        patterns = [re.compile(r'\b' + re.escape(kw) + r'\b', re.IGNORECASE) for kw in keywords]
        
        # Search through all pages
        for page in self.notebook.pages.values():
            # Check if all keywords are present
            matches = []
            match_all = True
            
            for pattern in patterns:
                match = pattern.search(page.content)
                if match:
                    matches.append(match)
                else:
                    match_all = False
                    break
            
            if match_all and matches:
                # Calculate relevance based on keyword density
                keyword_count = sum(len(list(p.finditer(page.content))) for p in patterns)
                score = keyword_count / max(1, len(page.content.split()))
                
                # Extract a snippet around the first match
                first_match = matches[0]
                start, end = first_match.span()
                
                # Create the content snippet
                content_start = max(0, start - self.context_size)
                content_end = min(len(page.content), end + self.context_size)
                
                if content_start > 0:
                    prefix = "..."
                else:
                    prefix = ""
                    
                if content_end < len(page.content):
                    suffix = "..."
                else:
                    suffix = ""
                    
                snippet = prefix + page.content[content_start:content_end] + suffix
                
                # Add to results
                result = SearchResult(
                    page=page,
                    content_snippet=snippet,
                    match_start=start,
                    match_end=end,
                    relevance_score=score
                )
                results.append(result)
        
        # Sort by relevance score (descending)
        results.sort(key=lambda r: r.relevance_score, reverse=True)
        
        return results
