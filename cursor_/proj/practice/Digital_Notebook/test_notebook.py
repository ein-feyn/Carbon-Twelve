"""
Simple test script to verify that notebook saving and loading works.
"""
from src.core.notebook import Notebook
from src.data.storage import NotebookStorage

def test_save_load():
    # Create a test notebook
    notebook = Notebook(name="Test Notebook")
    
    # Add a page
    page = notebook.create_page(name="Test Page", content="This is a test page")
    
    # Set some metadata
    notebook.set_metadata("test_key", "test_value")
    page.set_metadata("page_key", "page_value")
    
    # Save the notebook
    storage = NotebookStorage()
    try:
        storage.save_notebook(notebook)
        print("Notebook saved successfully")
    except Exception as e:
        print(f"Error saving notebook: {e}")
        return False
    
    # Load the notebook
    loaded_notebook = storage.load_notebook("Test Notebook")
    if not loaded_notebook:
        print("Failed to load notebook")
        return False
    
    print("Notebook loaded successfully")
    print(f"Loaded notebook name: {loaded_notebook.name}")
    print(f"Loaded notebook metadata: {loaded_notebook.notebook_metadata}")
    
    if len(loaded_notebook.pages) > 0:
        page_id = list(loaded_notebook.pages.keys())[0]
        loaded_page = loaded_notebook.pages[page_id]
        print(f"Loaded page name: {loaded_page.name}")
        print(f"Loaded page content: {loaded_page.content}")
        print(f"Loaded page metadata: {loaded_page.page_metadata}")
    
    return True

if __name__ == "__main__":
    success = test_save_load()
    print(f"Test {'passed' if success else 'failed'}") 