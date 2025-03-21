"""
Storage module for the Digital Notebook.

This module provides functionality for saving and loading notebooks from storage.
"""
import json
import os
import sqlite3
from typing import Optional, Dict, Any
from pathlib import Path
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from src.core.notebook import Notebook

Base = declarative_base()


class NotebookRecord(Base):
    """SQLAlchemy model for notebook metadata."""
    __tablename__ = 'notebooks'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    notebook_metadata = Column(Text, nullable=False)  # JSON serialized


class PageRecord(Base):
    """SQLAlchemy model for page data."""
    __tablename__ = 'pages'
    
    id = Column(Integer, primary_key=True)
    notebook_id = Column(Integer, nullable=False)
    page_id = Column(Integer, nullable=False)
    name = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    notebook_metadata = Column(Text, nullable=False)  # JSON serialized


class NotebookStorage:
    """
    Handles storage and retrieval of notebooks.
    
    This class provides methods for saving notebooks to disk and loading them back.
    """
    
    def __init__(self, storage_dir: str = None):
        """
        Initialize the storage manager.
        
        Args:
            storage_dir: Directory to store notebook files
        """
        if storage_dir is None:
            # Use a default location in the user's home directory
            self.storage_dir = os.path.join(str(Path.home()), '.digital_notebook')
        else:
            self.storage_dir = storage_dir
            
        # Ensure the storage directory exists
        os.makedirs(self.storage_dir, exist_ok=True)
    
    def _get_db_path(self, notebook_name: str) -> str:
        """Get the database file path for a notebook."""
        # Sanitize the notebook name for use in a filename
        safe_name = "".join(c if c.isalnum() or c in " _-" else "_" for c in notebook_name)
        return os.path.join(self.storage_dir, f"{safe_name}.db")
    
    def _initialize_db(self, db_path: str) -> None:
        """Initialize the database schema."""
        engine = create_engine(f"sqlite:///{db_path}")
        Base.metadata.create_all(engine)
    
    def save_notebook(self, notebook: Notebook) -> None:
        """
        Save a notebook to storage.
        
        Args:
            notebook: The notebook to save
        """
        db_path = self._get_db_path(notebook.name)
        self._initialize_db(db_path)
        
        engine = create_engine(f"sqlite:///{db_path}")
        Session = sessionmaker(bind=engine)
        session = Session()
        
        try:
            # Save notebook metadata
            notebook_record = session.query(NotebookRecord).filter_by(id=1).first()
            if notebook_record is None:
                notebook_record = NotebookRecord(id=1)
                
            notebook_record.name = notebook.name
            notebook_record.created_at = notebook.created_at
            notebook_record.updated_at = notebook.updated_at
            notebook_record.notebook_metadata = json.dumps(notebook.notebook_metadata)
            
            # Add or update the notebook record
            session.add(notebook_record)
            
            # Delete existing pages (simple approach - could be optimized)
            session.query(PageRecord).filter_by(notebook_id=1).delete()
            
            # Save all pages
            for page_id, page in notebook.pages.items():
                page_record = PageRecord(
                    notebook_id=1,
                    page_id=page_id,
                    name=page.name,
                    content=page.content,
                    created_at=page.created_at,
                    updated_at=page.updated_at,
                    notebook_metadata=json.dumps(page.notebook_metadata)
                )
                session.add(page_record)
            
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()
    
    def load_notebook(self, notebook_name: str) -> Optional[Notebook]:
        """
        Load a notebook from storage.
        
        Args:
            notebook_name: Name of the notebook to load
            
        Returns:
            The loaded Notebook object, or None if it doesn't exist
        """
        db_path = self._get_db_path(notebook_name)
        if not os.path.exists(db_path):
            return None
        
        engine = create_engine(f"sqlite:///{db_path}")
        Session = sessionmaker(bind=engine)
        session = Session()
        
        try:
            # Load notebook metadata
            notebook_record = session.query(NotebookRecord).filter_by(id=1).first()
            if notebook_record is None:
                return None
            
            # Create notebook object
            notebook = Notebook(name=notebook_record.name)
            notebook.created_at = notebook_record.created_at
            notebook.updated_at = notebook_record.updated_at
            notebook.notebook_metadata = json.loads(notebook_record.notebook_metadata)
            
            # Load all pages
            page_records = session.query(PageRecord).filter_by(notebook_id=1).all()
            for page_record in page_records:
                from src.core.page import Page
                
                page = Page(
                    page_id=page_record.page_id,
                    name=page_record.name,
                    content=page_record.content
                )
                page.created_at = page_record.created_at
                page.updated_at = page_record.updated_at
                page.notebook_metadata = json.loads(page_record.notebook_metadata)
                
                notebook.pages[page.page_id] = page
            
            return notebook
        except:
            return None
        finally:
            session.close()
    
    def list_notebooks(self) -> Dict[str, str]:
        """
        List all available notebooks.
        
        Returns:
            Dictionary of notebook names and their file paths
        """
        notebooks = {}
        for filename in os.listdir(self.storage_dir):
            if filename.endswith(".db"):
                notebook_name = os.path.splitext(filename)[0]
                notebooks[notebook_name] = os.path.join(self.storage_dir, filename)
        
        return notebooks
    
    def delete_notebook(self, notebook_name: str) -> bool:
        """
        Delete a notebook from storage.
        
        Args:
            notebook_name: Name of the notebook to delete
            
        Returns:
            True if the notebook was deleted, False otherwise
        """
        db_path = self._get_db_path(notebook_name)
        if os.path.exists(db_path):
            os.remove(db_path)
            return True
        
        return False
