"""
Page module for the Digital Notebook.

This module defines the Page class which represents a single page in the notebook.
"""
import datetime
from typing import Dict, Any, Optional


class Page:
    """
    Represents a single page in the digital notebook.
    
    Each page has content, metadata, and a unique identifier.
    """
    
    def __init__(self, page_id: int, name: Optional[str] = None, content: str = ""):
        """
        Initialize a new page.
        
        Args:
            page_id: Unique identifier for the page
            name: Optional name for the page
            content: Text content of the page
        """
        self.page_id = page_id
        self.name = name or f"Page {page_id}"
        self.content = content
        self.created_at = datetime.datetime.now()
        self.updated_at = self.created_at
        self.metadata = {}
    
    def update_content(self, content: str) -> None:
        """Update the page content and update timestamp."""
        self.content = content
        self.updated_at = datetime.datetime.now()
    
    def rename(self, new_name: str) -> None:
        """Rename the page."""
        self.name = new_name
        self.updated_at = datetime.datetime.now()
    
    def set_metadata(self, key: str, value: Any) -> None:
        """Set a metadata value for the page."""
        self.metadata[key] = value
        self.updated_at = datetime.datetime.now()
    
    def get_metadata(self, key: str) -> Any:
        """Get a metadata value for the page."""
        return self.metadata.get(key)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the page to a dictionary for serialization."""
        return {
            "page_id": self.page_id,
            "name": self.name,
            "content": self.content,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Page':
        """Create a page from a dictionary representation."""
        page = cls(
            page_id=data["page_id"],
            name=data["name"],
            content=data["content"]
        )
        page.created_at = datetime.datetime.fromisoformat(data["created_at"])
        page.updated_at = datetime.datetime.fromisoformat(data["updated_at"])
        page.metadata = data["metadata"]
        return page
