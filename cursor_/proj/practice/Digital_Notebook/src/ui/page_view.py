"""
Page View module for the Digital Notebook.

This module provides a widget for displaying and editing notebook pages.
"""
from typing import Optional

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QHBoxLayout, QLabel
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QFont

from src.core.page import Page


class PageView(QWidget):
    """
    Widget for displaying and editing a notebook page.
    
    This class provides a text editor for the page content and displays the page name.
    """
    
    # Signal emitted when page content changes
    content_changed = pyqtSignal(str)
    
    def __init__(self):
        """Initialize the page view."""
        super().__init__()
        
        # Current page being displayed
        self.page: Optional[Page] = None
        
        # Set up the UI
        self.init_ui()
    
    def init_ui(self):
        """Set up the user interface."""
        # Create layout
        layout = QVBoxLayout(self)
        
        # Add header with page name
        header_layout = QHBoxLayout()
        self.page_name_label = QLabel("No page selected")
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        self.page_name_label.setFont(font)
        header_layout.addWidget(self.page_name_label)
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Add text editor for page content
        self.text_editor = QTextEdit()
        self.text_editor.setPlaceholderText("Select a page to start writing...")
        self.text_editor.textChanged.connect(self.on_text_changed)
        layout.addWidget(self.text_editor)
        
        # Set margins and spacing
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
    
    def set_page(self, page: Page):
        """
        Set the page to display.
        
        Args:
            page: Page to display
        """
        self.page = page
        
        # Update the UI
        self.page_name_label.setText(page.name)
        
        # Temporarily disconnect the signal to avoid triggering content_changed
        self.text_editor.textChanged.disconnect(self.on_text_changed)
        self.text_editor.setPlainText(page.content)
        self.text_editor.textChanged.connect(self.on_text_changed)
        
        # Enable editing
        self.text_editor.setReadOnly(False)
    
    def clear(self):
        """Clear the page view."""
        self.page = None
        self.page_name_label.setText("No page selected")
        self.text_editor.clear()
        self.text_editor.setPlaceholderText("Select a page to start writing...")
        self.text_editor.setReadOnly(True)
    
    def on_text_changed(self):
        """Handle changes to the text editor content."""
        if self.page:
            content = self.text_editor.toPlainText()
            self.content_changed.emit(content)
    
    def get_content(self) -> str:
        """
        Get the current content of the text editor.
        
        Returns:
            Current text content
        """
        return self.text_editor.toPlainText()
    
    def set_content(self, content: str):
        """
        Set the content of the text editor.
        
        Args:
            content: Text content to set
        """
        self.text_editor.setPlainText(content)
    
    def set_readonly(self, readonly: bool):
        """
        Set whether the text editor is read-only.
        
        Args:
            readonly: Whether to make the editor read-only
        """
        self.text_editor.setReadOnly(readonly)
    
    def focus_editor(self):
        """Set focus to the text editor."""
        self.text_editor.setFocus()
