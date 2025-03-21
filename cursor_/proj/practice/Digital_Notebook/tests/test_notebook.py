"""
Tests for the Notebook class.

This module contains tests for verifying the functionality of the Notebook class.
"""
import pytest
from datetime import datetime

from src.core.notebook import Notebook
from src.core.page import Page


def test_notebook_creation():
    """Test that a notebook can be created with default values."""
    notebook = Notebook()
    
    assert notebook.name == "My Notebook"
    assert notebook.max_pages == 3000
    assert isinstance(notebook.created_at, datetime)
    assert isinstance(notebook.updated_at, datetime)
    assert notebook.pages == {}
    assert notebook.metadata == {}


def test_notebook_custom_values():
    """Test that a notebook can be created with custom values."""
    notebook = Notebook(name="Test Notebook", max_pages=100)
    
    assert notebook.name == "Test Notebook"
    assert notebook.max_pages == 100


def test_create_page():
    """Test that pages can be created in the notebook."""
    notebook = Notebook()
    
    # Create a page
    page = notebook.create_page(name="Test Page", content="Test content")
    
    # Check that the page was created correctly
    assert page.page_id == 1
    assert page.name == "Test Page"
    assert page.content == "Test content"
    
    # Check that the page was added to the notebook
    assert 1 in notebook.pages
    assert notebook.pages[1] == page


def test_create_multiple_pages():
    """Test that multiple pages can be created in the notebook."""
    notebook = Notebook()
    
    # Create multiple pages
    page1 = notebook.create_page(name="Page 1")
    page2 = notebook.create_page(name="Page 2")
    page3 = notebook.create_page(name="Page 3")
    
    # Check page IDs
    assert page1.page_id == 1
    assert page2.page_id == 2
    assert page3.page_id == 3
    
    # Check notebook pages
    assert len(notebook.pages) == 3
    assert 1 in notebook.pages
    assert 2 in notebook.pages
    assert 3 in notebook.pages


def test_get_page():
    """Test that pages can be retrieved from the notebook."""
    notebook = Notebook()
    
    # Create a page
    page = notebook.create_page(name="Test Page")
    
    # Get the page
    retrieved_page = notebook.get_page(page.page_id)
    
    # Check that the retrieved page is correct
    assert retrieved_page == page


def test_get_nonexistent_page():
    """Test that getting a nonexistent page raises an error."""
    notebook = Notebook()
    
    with pytest.raises(KeyError):
        notebook.get_page(999)


def test_delete_page():
    """Test that pages can be deleted from the notebook."""
    notebook = Notebook()
    
    # Create a page
    page = notebook.create_page(name="Test Page")
    
    # Delete the page
    notebook.delete_page(page.page_id)
    
    # Check that the page was deleted
    assert page.page_id not in notebook.pages
    assert len(notebook.pages) == 0


def test_delete_nonexistent_page():
    """Test that deleting a nonexistent page raises an error."""
    notebook = Notebook()
    
    with pytest.raises(KeyError):
        notebook.delete_page(999)


def test_list_pages():
    """Test that pages can be listed from the notebook."""
    notebook = Notebook()
    
    # Create pages
    page1 = notebook.create_page(name="Page 1")
    page2 = notebook.create_page(name="Page 2")
    page3 = notebook.create_page(name="Page 3")
    
    # List pages
    pages = notebook.list_pages()
    
    # Check the list
    assert len(pages) == 3
    assert pages[0] == page1
    assert pages[1] == page2
    assert pages[2] == page3


def test_search_pages():
    """Test that pages can be searched in the notebook."""
    notebook = Notebook()
    
    # Create pages with different content
    notebook.create_page(name="Apple Page", content="This page is about apples")
    notebook.create_page(name="Banana Page", content="This page is about bananas")
    notebook.create_page(name="Apple Banana", content="This page is about both fruits")
    
    # Search for pages containing "apple"
    results = notebook.search_pages("apple")
    
    # Check the results
    assert len(results) == 2
    assert results[0].name == "Apple Page" or results[1].name == "Apple Page"
    assert results[0].name == "Apple Banana" or results[1].name == "Apple Banana"


def test_max_pages_limit():
    """Test that the notebook enforces the maximum page limit."""
    notebook = Notebook(max_pages=2)
    
    # Create pages up to the limit
    notebook.create_page(name="Page 1")
    notebook.create_page(name="Page 2")
    
    # Try to create a page beyond the limit
    with pytest.raises(ValueError):
        notebook.create_page(name="Page 3") 