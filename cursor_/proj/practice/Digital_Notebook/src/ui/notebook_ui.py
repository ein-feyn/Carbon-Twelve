"""
Notebook UI module for the Digital Notebook.

This module provides the main user interface for the Digital Notebook application.
"""
import sys
from typing import Optional, Dict, List, Any

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QLabel, QLineEdit, QPushButton, QTextEdit,
    QSplitter, QListWidget, QListWidgetItem, QMenu, QMessageBox,
    QDialog, QDialogButtonBox, QFormLayout, QStatusBar
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QAction, QIcon, QTextCursor

from src.core.notebook import Notebook
from src.core.page import Page
from src.data.storage import NotebookStorage
from src.utils.search import SearchEngine, SearchResult
from .page_view import PageView


class NotebookUI(QMainWindow):
    """
    Main window for the Digital Notebook application.
    
    This class provides the user interface for interacting with the notebook.
    """
    
    def __init__(self):
        """Initialize the notebook UI."""
        super().__init__()
        
        # Initialize the notebook and storage
        self.storage = NotebookStorage()
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
        self.status_bar.showMessage("Ready")
        
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
        
        save_notebook_action = QAction("&Save Notebook", self)
        save_notebook_action.triggered.connect(self.save_notebook)
        file_menu.addAction(save_notebook_action)
        
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
        
        toolbar.addSeparator()
        
        search_action = QAction("Search", self)
        search_action.triggered.connect(self.show_search)
        toolbar.addAction(search_action)
    
    def create_sidebar(self):
        """Create the sidebar for page navigation."""
        self.sidebar = QWidget()
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        
        # Add label for pages list
        sidebar_layout.addWidget(QLabel("Pages"))
        
        # Create the pages list
        self.pages_list = QListWidget()
        self.pages_list.itemClicked.connect(self.on_page_selected)
        sidebar_layout.addWidget(self.pages_list)
        
        # Add button for creating new pages
        new_page_button = QPushButton("New Page")
        new_page_button.clicked.connect(self.create_new_page)
        sidebar_layout.addWidget(new_page_button)
        
        # Add the sidebar to the main splitter
        self.main_splitter.addWidget(self.sidebar)
    
    def create_content_area(self):
        """Create the main content area."""
        self.content_area = QWidget()
        content_layout = QVBoxLayout(self.content_area)
        
        # Create the page view
        self.page_view = PageView()
        self.page_view.content_changed.connect(self.on_page_content_changed)
        content_layout.addWidget(self.page_view)
        
        # Add the content area to the main splitter
        self.main_splitter.addWidget(self.content_area)
    
    def create_new_notebook(self):
        """Create a new notebook."""
        # Prompt for notebook name
        name, ok = self.prompt_for_text("New Notebook", "Enter a name for the new notebook:")
        if ok and name:
            # Create the notebook
            self.notebook = Notebook(name=name)
            self.search_engine.set_notebook(self.notebook)
            
            # Update the UI
            self.update_pages_list()
            self.setWindowTitle(f"Digital Notebook - {name}")
            self.status_bar.showMessage(f"Created new notebook: {name}")
    
    def open_notebook(self):
        """Open an existing notebook."""
        # Get list of available notebooks
        notebooks = self.storage.list_notebooks()
        
        if not notebooks:
            QMessageBox.information(self, "No Notebooks", "No notebooks found.")
            return
        
        # Create a simple dialog to select a notebook
        dialog = QDialog(self)
        dialog.setWindowTitle("Open Notebook")
        layout = QVBoxLayout(dialog)
        
        notebook_list = QListWidget()
        for name in notebooks:
            notebook_list.addItem(name)
        
        layout.addWidget(QLabel("Select a notebook to open:"))
        layout.addWidget(notebook_list)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        # Show the dialog and process the result
        if dialog.exec() == QDialog.DialogCode.Accepted and notebook_list.currentItem():
            notebook_name = notebook_list.currentItem().text()
            self.notebook = self.storage.load_notebook(notebook_name)
            
            if self.notebook:
                self.search_engine.set_notebook(self.notebook)
                self.update_pages_list()
                self.setWindowTitle(f"Digital Notebook - {self.notebook.name}")
                self.status_bar.showMessage(f"Opened notebook: {self.notebook.name}")
            else:
                QMessageBox.critical(self, "Error", f"Failed to open notebook: {notebook_name}")
    
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
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        # Connect search functionality
        def perform_search():
            query = search_input.text()
            if not query:
                return
            
            # Perform the search
            search_results = self.search_engine.advanced_search(query)
            
            # Display results
            results_list.clear()
            for result in search_results:
                item = QListWidgetItem(f"{result.page.name}: {result.content_snippet}")
                item.setData(Qt.ItemDataRole.UserRole, result.page.page_id)
                results_list.addItem(item)
        
        search_button.clicked.connect(perform_search)
        search_input.returnPressed.connect(perform_search)
        
        # Handle result selection
        def on_result_selected(item):
            page_id = item.data(Qt.ItemDataRole.UserRole)
            dialog.accept()
            self.select_page(page_id)
        
        results_list.itemDoubleClicked.connect(on_result_selected)
        
        # Show the dialog
        dialog.exec()
    
    def show_word_count_analysis(self):
        """Show word count analysis for the current page."""
        if not self.current_page:
            QMessageBox.warning(self, "No Page Selected", "Please select a page to analyze.")
            return
        
        # For now, just show a simple message with the word count
        # In a real implementation, this would show visualizations
        from src.analysis.word_counter import WordCounter
        word_counter = WordCounter()
        count = word_counter.count_words(self.current_page.content)
        
        QMessageBox.information(
            self, "Word Count Analysis", 
            f"The page '{self.current_page.name}' contains {count} words.\n\n"
            f"Word count analysis visualizations will be implemented in a future update."
        )
    
    def update_pages_list(self):
        """Update the list of pages in the sidebar."""
        self.pages_list.clear()
        
        if not self.notebook:
            return
        
        for page in self.notebook.list_pages():
            item = QListWidgetItem(page.name)
            item.setData(Qt.ItemDataRole.UserRole, page.page_id)
            self.pages_list.addItem(item)
    
    def on_page_selected(self, item):
        """Handle selection of a page in the sidebar."""
        page_id = item.data(Qt.ItemDataRole.UserRole)
        self.select_page(page_id)
    
    def select_page(self, page_id):
        """Select and display a page by its ID."""
        if not self.notebook:
            return
        
        try:
            # Get the page
            page = self.notebook.get_page(page_id)
            self.current_page = page
            
            # Update the page view
            self.page_view.set_page(page)
            
            # Update the status bar
            self.status_bar.showMessage(f"Current page: {page.name}")
            
            # Select the page in the list
            for i in range(self.pages_list.count()):
                item = self.pages_list.item(i)
                if item.data(Qt.ItemDataRole.UserRole) == page_id:
                    self.pages_list.setCurrentItem(item)
                    break
        except KeyError:
            QMessageBox.warning(self, "Error", f"Page with ID {page_id} not found.")
    
    def on_page_content_changed(self, content):
        """Handle changes to the page content."""
        if self.current_page:
            self.current_page.update_content(content)
    
    def prompt_for_text(self, title, message, initial_text=""):
        """
        Prompt the user for text input.
        
        Returns:
            Tuple of (text, ok) where ok is True if the user clicked OK
        """
        dialog = QDialog(self)
        dialog.setWindowTitle(title)
        layout = QFormLayout(dialog)
        
        text_input = QLineEdit(initial_text)
        layout.addRow(message, text_input)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        result = dialog.exec()
        return text_input.text(), result == QDialog.DialogCode.Accepted


def run_application():
    """Run the Digital Notebook application."""
    app = QApplication(sys.argv)
    window = NotebookUI()
    window.show()
    sys.exit(app.exec())
