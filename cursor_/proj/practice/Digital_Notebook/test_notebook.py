"""
Simple test script to verify that notebook saving and loading works.
"""
import os
from pathlib import Path
from src.core.notebook import Notebook
from src.data.storage import NotebookStorage
from src.utils.config import Config

def test_save_load():
    # Create a test notebook
    notebook = Notebook(name="Test Notebook")
    
    # Add a page
    page = notebook.create_page(name="Test Page", content="This is a test page")
    
    # Set some metadata
    notebook.set_metadata("test_key", "test_value")
    page.set_metadata("page_key", "page_value")
    
    # Initialize storage with default location
    config = Config()
    storage_dir = config.get_default_storage_dir()
    storage = NotebookStorage(storage_dir)
    
    # Save the notebook
    try:
        storage.save_notebook(notebook)
        print("Notebook saved successfully to default location")
    except Exception as e:
        print(f"Error saving notebook: {e}")
        return False
    
    # Test saving to a custom location
    custom_dir = os.path.join(str(Path.home()), "test_notebooks")
    try:
        os.makedirs(custom_dir, exist_ok=True)
        file_path = storage.save_notebook_as(notebook, custom_dir, "Custom Named Notebook")
        print(f"Notebook saved successfully to custom location: {file_path}")
    except Exception as e:
        print(f"Error saving notebook to custom location: {e}")
        return False
    
    # Load the notebook from the default location
    loaded_notebook = storage.load_notebook("Test Notebook")
    if not loaded_notebook:
        print("Failed to load notebook from default location")
        return False
    
    print("Notebook loaded successfully from default location")
    print(f"Loaded notebook name: {loaded_notebook.name}")
    print(f"Loaded notebook metadata: {loaded_notebook.notebook_metadata}")
    
    if len(loaded_notebook.pages) > 0:
        page_id = list(loaded_notebook.pages.keys())[0]
        loaded_page = loaded_notebook.pages[page_id]
        print(f"Loaded page name: {loaded_page.name}")
        print(f"Loaded page content: {loaded_page.content}")
        print(f"Loaded page metadata: {loaded_page.page_metadata}")
    
    # Load the notebook from the custom location
    custom_notebook = storage.load_notebook_from_file(file_path)
    if not custom_notebook:
        print("Failed to load notebook from custom location")
        return False
    
    print("\nNotebook loaded successfully from custom location")
    print(f"Loaded notebook name: {custom_notebook.name}")
    
    return True

if __name__ == "__main__":
    success = test_save_load()
    print(f"\nTest {'passed' if success else 'failed'}") 