"""
Tests for the word counting functionality.

This module contains tests for verifying the word counting functionality.
"""
import pytest

from src.core.notebook import Notebook
from src.utils.word_counter import WordCounter


@pytest.fixture
def sample_notebook():
    """Create a sample notebook with test pages for word count testing."""
    notebook = Notebook(name="Test Notebook")
    
    # Create pages with test content
    notebook.create_page(
        name="Simple Page",
        content="This is a simple page with some basic text. It has twenty words total, including some repeated words like 'words' and 'some'."
    )
    
    notebook.create_page(
        name="Complex Page",
        content="""This page has more complex content with multiple paragraphs.

It contains different types of words, including technical terms like Python, programming, and APIs.

There are also numbers like 123 and special characters like !@#$.

This page has a higher total word count and should demonstrate the counter's ability to handle various text patterns."""
    )
    
    notebook.create_page(
        name="Empty Page",
        content=""
    )
    
    return notebook


def test_word_counter_initialization():
    """Test that the word counter can be initialized."""
    # Initialize without a notebook
    word_counter = WordCounter()
    assert word_counter.notebook is None
    
    # Initialize with a notebook
    notebook = Notebook()
    word_counter = WordCounter(notebook)
    assert word_counter.notebook == notebook


def test_set_notebook():
    """Test that a notebook can be set for the word counter."""
    word_counter = WordCounter()
    notebook = Notebook()
    
    word_counter.set_notebook(notebook)
    assert word_counter.notebook == notebook


def test_count_words_in_page():
    """Test counting words in a single page."""
    notebook = Notebook()
    page = notebook.create_page(
        name="Test Page",
        content="This is a test page with exactly ten words."
    )
    
    word_counter = WordCounter(notebook)
    count = word_counter.count_words_in_page(page.page_id)
    
    assert count == 10


def test_count_words_in_empty_page(sample_notebook):
    """Test counting words in an empty page."""
    word_counter = WordCounter(sample_notebook)
    
    # Find the empty page
    empty_page_id = None
    for page_id, page in sample_notebook.pages.items():
        if page.name == "Empty Page":
            empty_page_id = page_id
            break
    
    count = word_counter.count_words_in_page(empty_page_id)
    assert count == 0


def test_count_words_in_complex_page(sample_notebook):
    """Test counting words in a complex page."""
    word_counter = WordCounter(sample_notebook)
    
    # Find the complex page
    complex_page_id = None
    for page_id, page in sample_notebook.pages.items():
        if page.name == "Complex Page":
            complex_page_id = page_id
            break
    
    count = word_counter.count_words_in_page(complex_page_id)
    assert count > 20  # The complex page should have more than 20 words


def test_count_total_words(sample_notebook):
    """Test counting total words in a notebook."""
    word_counter = WordCounter(sample_notebook)
    total_count = word_counter.count_total_words()
    
    # Calculate expected count manually
    expected_count = 0
    for page in sample_notebook.pages.values():
        words = page.content.split()
        expected_count += len(words)
    
    assert total_count == expected_count


def test_get_word_frequency(sample_notebook):
    """Test getting word frequency in a notebook."""
    word_counter = WordCounter(sample_notebook)
    frequency = word_counter.get_word_frequency()
    
    # Check some expected words
    assert "words" in frequency
    assert "page" in frequency
    assert "python" in frequency.keys() or "Python" in frequency.keys()
    
    # Check counts for specific words
    assert frequency["page"] >= 3  # The word "page" appears at least 3 times
    assert frequency["this"] >= 3  # The word "this" appears at least 3 times


def test_get_page_word_count(sample_notebook):
    """Test getting word count for each page in a notebook."""
    word_counter = WordCounter(sample_notebook)
    page_counts = word_counter.get_page_word_count()
    
    # Check that all pages are included
    assert len(page_counts) == len(sample_notebook.pages)
    
    # Check specific counts
    for page_id, count in page_counts.items():
        page = sample_notebook.pages[page_id]
        if page.name == "Empty Page":
            assert count == 0
        elif page.name == "Simple Page":
            assert count == 20  # As stated in the content
        elif page.name == "Complex Page":
            assert count > 20


def test_get_weighted_word_count():
    """Test getting weighted word count based on importance."""
    notebook = Notebook()
    page = notebook.create_page(
        name="Weighted Test",
        content="Important important critical critical critical urgent urgent normal normal normal normal"
    )
    
    word_counter = WordCounter(notebook)
    
    # Set weights
    weights = {
        "important": 2.0,  # Double weight
        "critical": 3.0,   # Triple weight
        "urgent": 1.5,     # 1.5x weight
        "normal": 1.0      # Normal weight
    }
    
    weighted_count = word_counter.get_weighted_word_count(weights)
    
    # Calculate expected count
    # 2 "important" * 2.0 = 4
    # 3 "critical" * 3.0 = 9
    # 2 "urgent" * 1.5 = 3
    # 4 "normal" * 1.0 = 4
    # Total: 20 (raw count: 11)
    expected_count = 20
    
    assert weighted_count == expected_count


def test_get_most_common_words(sample_notebook):
    """Test getting the most common words in a notebook."""
    word_counter = WordCounter(sample_notebook)
    common_words = word_counter.get_most_common_words(5)  # Get top 5
    
    # Check that we get 5 words
    assert len(common_words) == 5
    
    # Check format
    for word, count in common_words:
        assert isinstance(word, str)
        assert isinstance(count, int)
        assert count > 0
    
    # Check ordering (descending by count)
    for i in range(len(common_words) - 1):
        assert common_words[i][1] >= common_words[i+1][1] 