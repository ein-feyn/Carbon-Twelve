"""
Notebook UI module for the Digital Notebook.

This module provides the main user interface for the Digital Notebook application.
"""
import sys
import os
from typing import Optional, Dict, List, Any

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QLabel, QLineEdit, QPushButton, QTextEdit,
    QSplitter, QListWidget, QListWidgetItem, QMenu, QMessageBox,
    QDialog, QDialogButtonBox, QFormLayout, QStatusBar,
    QFileDialog
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QAction, QIcon, QTextCursor

from src.core.notebook import Notebook
from src.core.page import Page
from src.data.storage import NotebookStorage
from src.utils.search import SearchEngine, SearchResult
from src.utils.config import Config
from .page_view import PageView


class NotebookUI(QMainWindow):
    """
    Main window for the Digital Notebook application.
    
    This class provides the user interface for interacting with the notebook.
    """
    
    def __init__(self):
        """Initialize the notebook UI."""
        super().__init__()
        
        # Initialize the config
        self.config = Config()
        
        # Initialize the notebook and storage with the configured storage directory
        storage_dir = self.config.get_default_storage_dir()
        self.storage = NotebookStorage(storage_dir)
        self.notebook: Optional[Notebook] = None
        self.search_engine = SearchEngine()
        
        # Track the current page
        self.current_page: Optional[Page] = None
        
        # Set up the UI
        self.init_ui()
    
    def init_ui(self):
        """Set up the user interface."""
        # Set window properties
        self.setWindowTitle("Digital Notebook")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create the main widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # Create the menu bar
        self.create_menu_bar()
        
        # Create the toolbar
        self.create_toolbar()
        
        # Create the main splitter
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.main_layout.addWidget(self.main_splitter)
        
        # Create the sidebar for page navigation
        self.create_sidebar()
        
        # Create the content area
        self.create_content_area()
        
        # Set up the status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage(f"Storage directory: {self.storage.get_storage_directory()}")
        
        # Set the initial size ratio between sidebar and content
        self.main_splitter.setSizes([300, 900])
    
    def create_menu_bar(self):
        """Create the application menu bar."""
        menu_bar = self.menuBar()
        
        # File menu
        file_menu = menu_bar.addMenu("&File")
        
        new_notebook_action = QAction("&New Notebook", self)
        new_notebook_action.triggered.connect(self.create_new_notebook)
        file_menu.addAction(new_notebook_action)
        
        open_notebook_action = QAction("&Open Notebook", self)
        open_notebook_action.triggered.connect(self.open_notebook)
        file_menu.addAction(open_notebook_action)
        
        open_notebook_from_file_action = QAction("Open Notebook from &File...", self)
        open_notebook_from_file_action.triggered.connect(self.open_notebook_from_file)
        file_menu.addAction(open_notebook_from_file_action)
        
        file_menu.addSeparator()
        
        save_notebook_action = QAction("&Save Notebook", self)
        save_notebook_action.triggered.connect(self.save_notebook)
        file_menu.addAction(save_notebook_action)
        
        save_notebook_as_action = QAction("Save Notebook &As...", self)
        save_notebook_as_action.triggered.connect(self.save_notebook_as)
        file_menu.addAction(save_notebook_as_action)
        
        file_menu.addSeparator()
        
        set_storage_dir_action = QAction("Set Default Storage &Directory...", self)
        set_storage_dir_action.triggered.connect(self.set_default_storage_directory)
        file_menu.addAction(set_storage_dir_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menu_bar.addMenu("&Edit")
        
        new_page_action = QAction("New &Page", self)
        new_page_action.triggered.connect(self.create_new_page)
        edit_menu.addAction(new_page_action)
        
        rename_page_action = QAction("&Rename Page", self)
        rename_page_action.triggered.connect(self.rename_current_page)
        edit_menu.addAction(rename_page_action)
        
        delete_page_action = QAction("&Delete Page", self)
        delete_page_action.triggered.connect(self.delete_current_page)
        edit_menu.addAction(delete_page_action)
        
        # View menu
        view_menu = menu_bar.addMenu("&View")
        
        toggle_sidebar_action = QAction("Toggle &Sidebar", self)
        toggle_sidebar_action.triggered.connect(self.toggle_sidebar)
        view_menu.addAction(toggle_sidebar_action)
        
        # Search menu
        search_menu = menu_bar.addMenu("&Search")
        
        search_action = QAction("&Search Notebook", self)
        search_action.triggered.connect(self.show_search)
        search_menu.addAction(search_action)
        
        # Analysis menu
        analysis_menu = menu_bar.addMenu("&Analysis")
        
        word_count_action = QAction("&Word Count Analysis", self)
        word_count_action.triggered.connect(self.show_word_count_analysis)
        analysis_menu.addAction(word_count_action)
    
    def create_toolbar(self):
        """Create the application toolbar."""
        toolbar = self.addToolBar("Main Toolbar")
        toolbar.setMovable(False)
        
        # Add toolbar actions
        new_page_action = QAction("New Page", self)
        new_page_action.triggered.connect(self.create_new_page)
        toolbar.addAction(new_page_action)
        
        save_action = QAction("Save", self)
        save_action.triggered.connect(self.save_notebook)
        toolbar.addAction(save_action)
        
        search_action = QAction("Search", self)
        search_action.triggered.connect(self.show_search)
        toolbar.addAction(search_action)
    
    def create_sidebar(self):
        """Create the sidebar for page navigation."""
        self.sidebar = QWidget()
        sidebar_layout = QVBoxLayout(self.sidebar)
        
        # Pages list
        sidebar_layout.addWidget(QLabel("Pages:"))
        self.pages_list = QListWidget()
        self.pages_list.itemClicked.connect(self.on_page_selected)
        sidebar_layout.addWidget(self.pages_list)
        
        # New page button
        new_page_button = QPushButton("New Page")
        new_page_button.clicked.connect(self.create_new_page)
        sidebar_layout.addWidget(new_page_button)
        
        self.main_splitter.addWidget(self.sidebar)
    
    def create_content_area(self):
        """Create the content area for displaying and editing pages."""
        self.page_view = PageView()
        self.page_view.content_changed.connect(self.on_page_content_changed)
        
        self.main_splitter.addWidget(self.page_view)
    
    def create_new_notebook(self):
        """Create a new notebook."""
        # Prompt for notebook name
        name, ok = self.prompt_for_text("New Notebook", "Enter a name for the new notebook:", 
                                        initial_text="My Notebook")
        if ok and name:
            # Create the notebook
            self.notebook = Notebook(name=name)
            self.search_engine.set_notebook(self.notebook)
            
            # Update the UI
            self.update_pages_list()
            self.status_bar.showMessage(f"Created new notebook: {name}")
            self.setWindowTitle(f"Digital Notebook - {name}")
    
    def open_notebook(self):
        """Open an existing notebook."""
        # Get available notebooks from default storage
        default_notebooks = self.storage.list_notebooks()
        
        # Get custom locations from config (we'll need to implement this in the Config class)
        custom_notebooks = self.config.get_recent_notebook_locations() if hasattr(self.config, 'get_recent_notebook_locations') else {}
        
        if not default_notebooks and not custom_notebooks:
            QMessageBox.information(self, "No Notebooks", "No notebooks found in the storage directory or recent custom locations.")
            return
        
        # Create a dialog for selecting a notebook
        dialog = QDialog(self)
        dialog.setWindowTitle("Open Notebook")
        dialog.setMinimumWidth(500)
        layout = QVBoxLayout(dialog)
        
        layout.addWidget(QLabel("Select a notebook to open:"))
        
        notebook_list = QListWidget()
        
        # Add notebooks from default directory
        if default_notebooks:
            default_category = QListWidgetItem("Default Storage:")
            default_category.setFlags(Qt.ItemFlag.NoItemFlags)
            default_category.setBackground(Qt.GlobalColor.lightGray)
            notebook_list.addItem(default_category)
            
            for name, path in default_notebooks.items():
                item = QListWidgetItem(f"  {name}")
                item.setData(Qt.ItemDataRole.UserRole, path)
                notebook_list.addItem(item)
        
        # Add notebooks from custom locations
        if custom_notebooks:
            custom_category = QListWidgetItem("Custom Locations:")
            custom_category.setFlags(Qt.ItemFlag.NoItemFlags)
            custom_category.setBackground(Qt.GlobalColor.lightGray)
            notebook_list.addItem(custom_category)
            
            for path, name in custom_notebooks.items():
                item = QListWidgetItem(f"  {name} ({os.path.dirname(path)})")
                item.setData(Qt.ItemDataRole.UserRole, path)
                notebook_list.addItem(item)
        
        layout.addWidget(notebook_list)
        
        # Add a button to browse for notebooks
        browse_button = QPushButton("Browse for Notebook...")
        browse_button.clicked.connect(lambda: dialog.done(2))  # Use a special return code
        
        buttons = QDialogButtonBox()
        buttons.addButton(QDialogButtonBox.StandardButton.Open)
        buttons.addButton(QDialogButtonBox.StandardButton.Cancel)
        buttons.addButton(browse_button, QDialogButtonBox.ButtonRole.ActionRole)
        
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        result = dialog.exec()
        
        if result == 1:  # QDialog.DialogCode.Accepted
            selected = notebook_list.currentItem()
            if selected and selected.data(Qt.ItemDataRole.UserRole):
                notebook_path = selected.data(Qt.ItemDataRole.UserRole)
                try:
                    # Load the notebook from the path
                    self.notebook = self.storage.load_notebook_from_file(notebook_path)
                    if self.notebook:
                        # Store this path in recent notebooks if it's a custom location
                        if notebook_path not in default_notebooks.values():
                            self.config.add_recent_notebook_location(notebook_path, self.notebook.name)
                        
                        self.search_engine.set_notebook(self.notebook)
                        self.update_pages_list()
                        self.status_bar.showMessage(f"Opened notebook: {self.notebook.name}")
                        self.setWindowTitle(f"Digital Notebook - {self.notebook.name}")
                    else:
                        QMessageBox.critical(self, "Error", f"Failed to load notebook from: {notebook_path}")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to load notebook: {str(e)}")
        elif result == 2:  # Browse button clicked
            self.open_notebook_from_file()
    
    def open_notebook_from_file(self):
        """Open a notebook from a specific file."""
        # Show file dialog to select a notebook file
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Notebook File",
            os.path.expanduser("~"),
            "Notebook Files (*.db);;All Files (*)"
        )
        
        if file_path:
            try:
                # Load the notebook from the selected file
                self.notebook = self.storage.load_notebook_from_file(file_path)
                
                if self.notebook:
                    # Add to recent notebooks list if it's not in the default directory
                    default_dir = self.config.get_default_storage_dir()
                    if os.path.dirname(file_path) != default_dir:
                        self.config.add_recent_notebook_location(file_path, self.notebook.name)
                    
                    # Update the UI
                    self.search_engine.set_notebook(self.notebook)
                    self.update_pages_list()
                    self.status_bar.showMessage(f"Opened notebook from file: {file_path}")
                    self.setWindowTitle(f"Digital Notebook - {self.notebook.name}")
                else:
                    QMessageBox.critical(self, "Error", f"Failed to load notebook from file: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load notebook: {str(e)}")
    
    def save_notebook(self):
        """Save the current notebook."""
        if not self.notebook:
            QMessageBox.warning(self, "No Notebook", "No notebook is currently open.")
            return
        
        try:
            self.storage.save_notebook(self.notebook)
            self.status_bar.showMessage(f"Saved notebook: {self.notebook.name}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save notebook: {str(e)}")
    
    def save_notebook_as(self):
        """Save the current notebook to a specific location."""
        if not self.notebook:
            QMessageBox.warning(self, "No Notebook", "No notebook is currently open.")
            return
        
        # Show directory selection dialog
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Directory to Save Notebook",
            os.path.expanduser("~"),
            QFileDialog.Option.ShowDirsOnly
        )
        
        if directory:
            try:
                # Optionally prompt for a new name
                new_name = None
                change_name = QMessageBox.question(
                    self,
                    "Change Name",
                    "Would you like to save the notebook with a different name?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                
                if change_name == QMessageBox.StandardButton.Yes:
                    new_name, ok = self.prompt_for_text(
                        "New Name",
                        "Enter a new name for the notebook:",
                        initial_text=self.notebook.name
                    )
                    if not ok or not new_name:
                        new_name = None
                
                # Save the notebook to the selected directory
                file_path = self.storage.save_notebook_as(self.notebook, directory, new_name)
                
                # Add to recent notebooks list if it's not in the default directory
                default_dir = self.config.get_default_storage_dir()
                saved_name = new_name if new_name else self.notebook.name
                if os.path.dirname(file_path) != default_dir:
                    self.config.add_recent_notebook_location(file_path, saved_name)
                
                # Ask if user wants to set this as the default directory
                set_default = QMessageBox.question(
                    self,
                    "Set Default Directory",
                    "Would you like to set this as the default storage directory?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                
                if set_default == QMessageBox.StandardButton.Yes:
                    self.config.set_default_storage_dir(directory)
                    self.storage.set_storage_directory(directory)
                
                QMessageBox.information(self, "Success", f"Notebook saved to {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save notebook: {str(e)}")
    
    def set_default_storage_directory(self):
        """Set the default storage directory for notebooks."""
        # Show directory selection dialog
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Default Storage Directory",
            self.storage.get_storage_directory(),
            QFileDialog.Option.ShowDirsOnly
        )
        
        if directory:
            try:
                # Set the new storage directory
                self.storage.set_storage_directory(directory)
                self.config.set_default_storage_dir(directory)
                self.status_bar.showMessage(f"Default storage directory set to: {directory}")
                
                # Ask if user wants to move existing notebooks
                move_notebooks = QMessageBox.question(
                    self,
                    "Move Notebooks",
                    "Would you like to move your existing notebooks to the new directory?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                
                if move_notebooks == QMessageBox.StandardButton.Yes:
                    # This would require implementing a function to move notebooks
                    # For now, just inform the user this isn't implemented
                    QMessageBox.information(
                        self,
                        "Not Implemented",
                        "Moving notebooks is not implemented yet. You'll need to manually copy your notebooks to the new location."
                    )
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to set storage directory: {str(e)}")
    
    def create_new_page(self):
        """Create a new page in the notebook."""
        if not self.notebook:
            QMessageBox.warning(self, "No Notebook", "Please create or open a notebook first.")
            return
        
        # Prompt for page name
        name, ok = self.prompt_for_text("New Page", "Enter a name for the new page:")
        if ok:
            # Create the page
            page = self.notebook.create_page(name=name)
            
            # Update the UI
            self.update_pages_list()
            self.select_page(page.page_id)
            self.status_bar.showMessage(f"Created new page: {page.name}")
    
    def rename_current_page(self):
        """Rename the current page."""
        if not self.current_page:
            QMessageBox.warning(self, "No Page Selected", "Please select a page to rename.")
            return
        
        # Prompt for new name
        name, ok = self.prompt_for_text("Rename Page", "Enter a new name for the page:", 
                                        initial_text=self.current_page.name)
        if ok and name:
            # Rename the page
            self.current_page.rename(name)
            
            # Update the UI
            self.update_pages_list()
            self.select_page(self.current_page.page_id)
            self.status_bar.showMessage(f"Renamed page to: {name}")
    
    def delete_current_page(self):
        """Delete the current page."""
        if not self.current_page:
            QMessageBox.warning(self, "No Page Selected", "Please select a page to delete.")
            return
        
        # Confirm deletion
        response = QMessageBox.question(
            self, "Confirm Delete", 
            f"Are you sure you want to delete the page '{self.current_page.name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if response == QMessageBox.StandardButton.Yes:
            page_id = self.current_page.page_id
            page_name = self.current_page.name
            
            # Delete the page
            self.notebook.delete_page(page_id)
            self.current_page = None
            
            # Update the UI
            self.update_pages_list()
            self.page_view.clear()
            self.status_bar.showMessage(f"Deleted page: {page_name}")
    
    def toggle_sidebar(self):
        """Toggle the visibility of the sidebar."""
        if self.sidebar.isVisible():
            self.sidebar.hide()
        else:
            self.sidebar.show()
    
    def show_search(self):
        """Show the search interface."""
        if not self.notebook:
            QMessageBox.warning(self, "No Notebook", "Please create or open a notebook first.")
            return
        
        # Create a search dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Search Notebook")
        dialog.setMinimumWidth(600)
        layout = QVBoxLayout(dialog)
        
        # Search input
        search_layout = QHBoxLayout()
        search_input = QLineEdit()
        search_button = QPushButton("Search")
        search_layout.addWidget(QLabel("Search for:"))
        search_layout.addWidget(search_input)
        search_layout.addWidget(search_button)
        layout.addLayout(search_layout)
        
        # Results list
        results_list = QListWidget()
        layout.addWidget(QLabel("Results:"))
        layout.addWidget(results_list)
        
        # Close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(dialog.close)
        layout.addWidget(close_button)
        
        # Connect the search functionality
        def perform_search():
            query = search_input.text().strip()
            if not query:
                return
            
            # Clear previous results
            results_list.clear()
            
            # Perform the search
            search_results = self.search_engine.basic_search(query)
            
            # Display results
            for result in search_results:
                item = QListWidgetItem(f"{result.page.name} - {result.match_count} matches")
                item.setData(Qt.ItemDataRole.UserRole, result.page.page_id)
                results_list.addItem(item)
        
        search_button.clicked.connect(perform_search)
        search_input.returnPressed.connect(perform_search)
        
        # Connect result selection
        def on_result_selected(item):
            page_id = item.data(Qt.ItemDataRole.UserRole)
            dialog.close()
            self.select_page(page_id)
        
        results_list.itemDoubleClicked.connect(on_result_selected)
        
        # Show the dialog
        dialog.exec()
    
    def show_word_count_analysis(self):
        """Show word count analysis for the notebook."""
        if not self.notebook:
            QMessageBox.warning(self, "No Notebook", "Please create or open a notebook first.")
            return
        
        # For now, just show basic word count stats
        total_words = 0
        page_counts = {}
        
        for page_id, page in self.notebook.pages.items():
            words = len(page.content.split())
            total_words += words
            page_counts[page.name] = words
        
        # Create a dialog to display the results
        dialog = QDialog(self)
        dialog.setWindowTitle("Word Count Analysis")
        dialog.setMinimumWidth(400)
        layout = QVBoxLayout(dialog)
        
        layout.addWidget(QLabel(f"Total Words: {total_words}"))
        layout.addWidget(QLabel("Words per Page:"))
        
        for name, count in page_counts.items():
            layout.addWidget(QLabel(f"{name}: {count} words"))
        
        close_button = QPushButton("Close")
        close_button.clicked.connect(dialog.close)
        layout.addWidget(close_button)
        
        dialog.exec()
    
    def update_pages_list(self):
        """Update the list of pages in the sidebar."""
        self.pages_list.clear()
        if self.notebook:
            for page in self.notebook.list_pages():
                item = QListWidgetItem(page.name)
                item.setData(Qt.ItemDataRole.UserRole, page.page_id)
                self.pages_list.addItem(item)
    
    def on_page_selected(self, item):
        """Handle selection of a page in the list."""
        page_id = item.data(Qt.ItemDataRole.UserRole)
        self.select_page(page_id)
    
    def select_page(self, page_id):
        """Select and display a page."""
        if not self.notebook:
            return
        
        try:
            # Get the page
            page = self.notebook.get_page(page_id)
            self.current_page = page
            
            # Display the page in the page view
            self.page_view.set_page(page)
            
            # Update the status bar
            self.status_bar.showMessage(f"Page: {page.name}")
            
            # Select the page in the list
            for i in range(self.pages_list.count()):
                item = self.pages_list.item(i)
                if item.data(Qt.ItemDataRole.UserRole) == page_id:
                    self.pages_list.setCurrentItem(item)
                    break
        except KeyError:
            QMessageBox.warning(self, "Error", f"Could not find page with ID {page_id}")
    
    def on_page_content_changed(self, content):
        """Handle changes to the page content."""
        if self.current_page:
            self.current_page.update_content(content)
    
    def prompt_for_text(self, title, message, initial_text=""):
        """Show a dialog to prompt for text input."""
        dialog = QDialog(self)
        dialog.setWindowTitle(title)
        layout = QFormLayout(dialog)
        
        # Input field
        input_field = QLineEdit(initial_text)
        layout.addRow(message, input_field)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        result = dialog.exec()
        return input_field.text().strip(), result == QDialog.DialogCode.Accepted


def run_application():
    """Run the Digital Notebook application."""
    app = QApplication(sys.argv)
    window = NotebookUI()
    window.show()
    sys.exit(app.exec())
