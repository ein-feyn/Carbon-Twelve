"""
Main entry point for the Digital Notebook application.

This module initializes and runs the application.
"""
import sys
from PyQt6.QtWidgets import QApplication

from src.ui.notebook_ui import NotebookUI


def main():
    """Initialize and run the Digital Notebook application."""
    app = QApplication(sys.argv)
    window = NotebookUI()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
