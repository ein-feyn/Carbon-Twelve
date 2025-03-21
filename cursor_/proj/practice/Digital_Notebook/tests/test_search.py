"""
Tests for the Search module.

This module contains tests for verifying the functionality of the Search module.
"""
import pytest
import re

from src.utils.search import SearchEngine, SearchResult
from src.core.notebook import Notebook
from src.core.page import Page


@pytest.fixture
def sample_notebook():
    """Create a sample notebook with test pages for search testing."""
    notebook = Notebook(name="Test Notebook")
    
    # Create pages with test content
    notebook.create_page(
        name="Python Programming",
        content="Python is a high-level programming language known for its simplicity and readability. "
                "It supports multiple programming paradigms including procedural, object-oriented, and functional."
    )
    
    notebook.create_page(
        name="Data Science",
        content="Data science combines domain expertise, programming skills, and knowledge of mathematics and statistics. "
                "Python is a popular language for data science, with libraries like pandas, numpy, and matplotlib."
    )
    
    notebook.create_page(
        name="Machine Learning",
        content="Machine learning is a subset of artificial intelligence focused on building models that can learn from data. "
                "Popular Python libraries for machine learning include scikit-learn, TensorFlow, and PyTorch."
    )
    
    return notebook


def test_search_engine_initialization():
    """Test that the search engine can be initialized."""
    # Initialize without a notebook
    search_engine = SearchEngine()
    assert search_engine.notebook is None
    
    # Initialize with a notebook
    notebook = Notebook()
    search_engine = SearchEngine(notebook)
    assert search_engine.notebook == notebook


def test_set_notebook():
    """Test that a notebook can be set for the search engine."""
    search_engine = SearchEngine()
    notebook = Notebook()
    
    search_engine.set_notebook(notebook)
    assert search_engine.notebook == notebook


def test_basic_search(sample_notebook):
    """Test basic search functionality."""
    search_engine = SearchEngine(sample_notebook)
    
    # Search for 'python'
    results = search_engine.basic_search("python")
    
    assert len(results) == 2
    assert any(r.page.name == "Python Programming" for r in results)
    assert any(r.page.name == "Data Science" for r in results)
    
    # Case-sensitive search
    results = search_engine.basic_search("Python", case_sensitive=True)
    assert len(results) == 2
    
    # Search for non-existent text
    results = search_engine.basic_search("nonexistent")
    assert len(results) == 0


def test_advanced_search(sample_notebook):
    """Test advanced search functionality."""
    search_engine = SearchEngine(sample_notebook)
    
    # Search in all fields
    results = search_engine.advanced_search("python")
    assert len(results) == 2
    
    # Search in page names only
    results = search_engine.advanced_search("Python", page_name_only=True)
    assert len(results) == 1
    assert results[0].page.name == "Python Programming"
    
    # Whole word search
    results = search_engine.advanced_search("Python", whole_word=True)
    assert len(results) == 2
    
    # Case-sensitive search
    results = search_engine.advanced_search("python", case_sensitive=True)
    assert len(results) == 1  # Only in Data Science content, not in title
    
    # Search with all options
    results = search_engine.advanced_search(
        "Python", 
        case_sensitive=True, 
        whole_word=True, 
        page_name_only=True
    )
    assert len(results) == 1
    assert results[0].page.name == "Python Programming"


def test_regex_search(sample_notebook):
    """Test regex search functionality."""
    search_engine = SearchEngine(sample_notebook)
    
    # Search for words starting with 'program'
    results = search_engine.regex_search(r"\bprogram\w*\b")
    assert len(results) == 2
    
    # Check that contexts are properly extracted
    for result in results:
        if result.page.name == "Python Programming":
            assert "programming language" in result.contexts[0]
        elif result.page.name == "Data Science":
            assert "programming skills" in result.contexts[0]
    
    # Search with compiled regex
    regex = re.compile(r"\bdata\b", re.IGNORECASE)
    results = search_engine.regex_search(regex)
    assert len(results) == 1
    assert results[0].page.name == "Data Science"


def test_search_by_keywords(sample_notebook):
    """Test search by keywords functionality."""
    search_engine = SearchEngine(sample_notebook)
    
    # Search for pages containing both 'python' and 'data'
    results = search_engine.search_by_keywords(["python", "data"])
    assert len(results) == 1
    assert results[0].page.name == "Data Science"
    
    # Search for pages containing 'machine' and 'learning'
    results = search_engine.search_by_keywords(["machine", "learning"])
    assert len(results) == 1
    assert results[0].page.name == "Machine Learning"
    
    # Search for non-existent combination
    results = search_engine.search_by_keywords(["python", "nonexistent"])
    assert len(results) == 0


def test_search_result_dataclass():
    """Test that SearchResult dataclass works correctly."""
    # Create a page and a search result
    page = Page(page_id=1, name="Test Page", content="Test content")
    result = SearchResult(
        page=page,
        score=0.85,
        match_count=2,
        contexts=["context1", "context2"]
    )
    
    # Check attributes
    assert result.page == page
    assert result.score == 0.85
    assert result.match_count == 2
    assert result.contexts == ["context1", "context2"] 