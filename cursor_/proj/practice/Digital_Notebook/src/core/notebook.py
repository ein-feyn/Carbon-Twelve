"""
Notebook module for the Digital Notebook.

This module defines the Notebook class that manages a collection of pages.
"""
import datetime
from typing import Dict, List, Optional, Any
from .page import Page


class Notebook:
    """
    Represents a digital notebook containing multiple pages.
    
    The notebook manages page creation, retrieval, and organization.
    """
    
    def __init__(self, name: str = "My Notebook", max_pages: int = 3000):
        """
        Initialize a new notebook.
        
        Args:
            name: Name of the notebook
            max_pages: Maximum number of pages the notebook can contain
        """
        self.name = name
        self.max_pages = max_pages
        self.created_at = datetime.datetime.now()
        self.updated_at = self.created_at
        self.pages: Dict[int, Page] = {}
        self.metadata = {}
    
    def create_page(self, name: Optional[str] = None, content: str = "") -> Page:
        """
        Create a new page in the notebook.
        
        Args:
            name: Optional name for the page
            content: Initial content for the page
            
        Returns:
            The newly created Page object
            
        Raises:
            ValueError: If the notebook has reached its maximum page limit
        """
        if len(self.pages) >= self.max_pages:
            raise ValueError(f"Cannot create new page: maximum of {self.max_pages} pages reached")
        
        # Generate a new page ID
        new_id = 1
        if self.pages:
            new_id = max(self.pages.keys()) + 1
        
        # Create and store the new page
        page = Page(page_id=new_id, name=name, content=content)
        self.pages[new_id] = page
        self.updated_at = datetime.datetime.now()
        
        return page
    
    def get_page(self, page_id: int) -> Page:
        """
        Get a page by its ID.
        
        Args:
            page_id: ID of the page to retrieve
            
        Returns:
            The requested Page object
            
        Raises:
            KeyError: If no page exists with the given ID
        """
        if page_id not in self.pages:
            raise KeyError(f"No page exists with ID {page_id}")
        
        return self.pages[page_id]
    
    def delete_page(self, page_id: int) -> None:
        """
        Delete a page from the notebook.
        
        Args:
            page_id: ID of the page to delete
            
        Raises:
            KeyError: If no page exists with the given ID
        """
        if page_id not in self.pages:
            raise KeyError(f"No page exists with ID {page_id}")
        
        del self.pages[page_id]
        self.updated_at = datetime.datetime.now()
    
    def list_pages(self) -> List[Page]:
        """
        Get a list of all pages in the notebook.
        
        Returns:
            List of Page objects, sorted by page ID
        """
        return [self.pages[key] for key in sorted(self.pages.keys())]
    
    def search_pages(self, query: str) -> List[Page]:
        """
        Search for pages containing the query string.
        
        Args:
            query: String to search for in page content and names
            
        Returns:
            List of matching Page objects
        """
        results = []
        for page in self.pages.values():
            if (query.lower() in page.name.lower() or 
                query.lower() in page.content.lower()):
                results.append(page)
        
        return results
    
    def set_metadata(self, key: str, value: Any) -> None:
        """Set a metadata value for the notebook."""
        self.metadata[key] = value
        self.updated_at = datetime.datetime.now()
    
    def get_metadata(self, key: str) -> Any:
        """Get a metadata value for the notebook."""
        return self.metadata.get(key)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the notebook to a dictionary for serialization."""
        return {
            "name": self.name,
            "max_pages": self.max_pages,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "pages": {str(pid): page.to_dict() for pid, page in self.pages.items()},
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Notebook':
        """Create a notebook from a dictionary representation."""
        notebook = cls(
            name=data["name"],
            max_pages=data["max_pages"]
        )
        notebook.created_at = datetime.datetime.fromisoformat(data["created_at"])
        notebook.updated_at = datetime.datetime.fromisoformat(data["updated_at"])
        notebook.metadata = data["metadata"]
        
        # Restore pages
        for pid_str, page_data in data["pages"].items():
            page = Page.from_dict(page_data)
            notebook.pages[page.page_id] = page
            
        return notebook
