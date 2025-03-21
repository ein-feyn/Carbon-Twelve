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
    page_metadata = Column(Text, nullable=False)  # JSON serialized


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
    
    def set_storage_directory(self, directory: str) -> None:
        """
        Set the directory where notebooks will be stored.
        
        Args:
            directory: Directory to use for storage
        """
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
        self.storage_dir = directory
    
    def get_storage_directory(self) -> str:
        """
        Get the current storage directory.
        
        Returns:
            Path to the storage directory
        """
        return self.storage_dir
    
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
                    page_metadata=json.dumps(page.page_metadata)
                )
                session.add(page_record)
            
            session.commit()
        except Exception as e:
            session.rollback()
            raise Exception(f"Failed to save notebook: {str(e)}")
        finally:
            session.close()
    
    def save_notebook_as(self, notebook: Notebook, directory: str, new_name: Optional[str] = None) -> str:
        """
        Save a notebook to a specific directory, optionally with a new name.
        
        Args:
            notebook: The notebook to save
            directory: Directory where the notebook should be saved
            new_name: Optional new name for the notebook
            
        Returns:
            The path to the saved notebook file
            
        Raises:
            ValueError: If the directory is invalid
        """
        # Remember the original storage directory
        original_dir = self.storage_dir
        
        try:
            # Set the new storage directory
            self.set_storage_directory(directory)
            
            # If a new name is provided, temporarily rename the notebook
            original_name = None
            if new_name:
                original_name = notebook.name
                notebook.name = new_name
            
            # Save the notebook
            self.save_notebook(notebook)
            
            # Get the path to the saved file
            db_path = self._get_db_path(notebook.name)
            
            # Restore the original name if it was changed
            if original_name:
                notebook.name = original_name
                
            return db_path
        finally:
            # Restore the original storage directory
            self.storage_dir = original_dir
    
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
                page.page_metadata = json.loads(page_record.page_metadata)
                
                notebook.pages[page.page_id] = page
            
            return notebook
        except Exception as e:
            print(f"Error loading notebook: {str(e)}")
            return None
        finally:
            session.close()
    
    def load_notebook_from_file(self, db_path: str) -> Optional[Notebook]:
        """
        Load a notebook directly from a specific database file.
        
        Args:
            db_path: Path to the database file
            
        Returns:
            The loaded Notebook object, or None if it couldn't be loaded
        """
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
                page.page_metadata = json.loads(page_record.page_metadata)
                
                notebook.pages[page.page_id] = page
            
            return notebook
        except Exception as e:
            print(f"Error loading notebook from file: {str(e)}")
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
    
    def transfer_notebooks(self, source_dir: str, target_dir: str) -> Dict[str, str]:
        """
        Transfer notebooks from one directory to another.
        
        Args:
            source_dir: Source directory containing notebooks
            target_dir: Target directory to move notebooks to
            
        Returns:
            Dictionary of notebook names and their new file paths
            
        Raises:
            ValueError: If source or target directory is invalid
        """
        if not os.path.exists(source_dir):
            raise ValueError(f"Source directory does not exist: {source_dir}")
        
        if not os.path.exists(target_dir):
            os.makedirs(target_dir, exist_ok=True)
        
        # Dictionary to store transferred notebook info
        transferred_notebooks = {}
        
        # List all notebook files in the source directory
        for filename in os.listdir(source_dir):
            if filename.endswith(".db"):
                source_path = os.path.join(source_dir, filename)
                target_path = os.path.join(target_dir, filename)
                
                # Skip if the file already exists in the target directory
                if os.path.exists(target_path):
                    continue
                
                try:
                    # Copy the file from source to target
                    import shutil
                    shutil.copy2(source_path, target_path)
                    
                    # Store the notebook name and its new path
                    notebook_name = os.path.splitext(filename)[0]
                    transferred_notebooks[notebook_name] = target_path
                except Exception as e:
                    print(f"Error transferring notebook {filename}: {str(e)}")
        
        return transferred_notebooks
