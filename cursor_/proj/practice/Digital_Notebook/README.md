# Digital Notebook

A Python application for creating and managing digital notebooks with text analysis and visualization features.

## Features

- Create and manage multiple notebooks
- Add, edit, rename, and delete pages within notebooks
- Automatic word counting with weighted word system
- Advanced search functionality (basic, advanced, regex, keyword-based)
- Text analysis and visualization
- Modern PyQt6-based user interface

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/Digital_Notebook.git
   cd Digital_Notebook
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the application:
   ```
   python src/main.py
   ```

## Usage

### Basic Operations

- **Create a new notebook**: File > New
- **Open an existing notebook**: File > Open
- **Save the current notebook**: File > Save
- **Add a new page**: Edit > New Page
- **Delete a page**: Select the page and click Edit > Delete Page
- **Rename a page**: Select the page and click Edit > Rename Page

### Search

The application provides several search options:

- **Basic search**: Simple text search across all pages
- **Advanced search**: Search with options for case sensitivity, whole word matching, and limiting to page names
- **Regex search**: Use regular expressions for more complex search patterns
- **Keyword search**: Find pages containing all specified keywords

### Word Count Analysis

- View word count statistics for individual pages or the entire notebook
- Apply custom weights to certain words for weighted word counting
- Visualize word frequency and distribution

## Project Structure

```
Digital_Notebook/
├── src/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── notebook.py
│   │   └── page.py
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── notebook_ui.py
│   │   └── page_view.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── search.py
│   │   └── word_counter.py
│   └── main.py
├── tests/
│   ├── test_notebook.py
│   ├── test_search.py
│   └── test_word_count.py
├── data/
│   └── (saved notebooks)
├── requirements.txt
├── setup.py
└── README.md
```

## Development

### Running Tests

```
pytest
```

### Building Documentation

```
sphinx-build -b html docs/source docs/build
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- PyQt6 for the GUI framework
- pytest for testing
- All contributors who have helped with the development 