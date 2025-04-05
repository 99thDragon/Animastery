# Love Live! Sunshine!! Style Guide Assistant

A simple Retrieval-Augmented Generation (RAG) system with a graphical user interface designed to help learn and understand the animation style of Love Live! Sunshine!!. This tool allows users to search through a curated knowledge base of animation style information using natural language queries.

## Features

- **Text-based Knowledge Base**: Stores comprehensive information about the Love Live! Sunshine!! animation style
- **Keyword-based Search**: Simple but effective search functionality with case-insensitive matching
- **GUI Interface**: User-friendly interface built with tkinter featuring:
  - Clean, modern design
  - Placeholder text for query examples
  - Progress indicators
  - Scrollable results area
- **Keyword Highlighting**: Visual highlighting of search terms in results for better context
- **Progress Indicator**: Visual feedback during search operations

## Files Included

- `simple_rag_gui.py`: Main GUI application with enhanced visual features
- `simple_rag.py`: Original command-line version for basic functionality
- `love_live_style_notes.txt`: Knowledge base containing detailed style information
- `.gitignore`: Git configuration file for Python projects
- `README.md`: Project documentation

## Installation

1. **Prerequisites**:
   - Python 3.x
   - tkinter (usually comes with Python)
   - No additional packages required

2. **Setup**:
   ```bash
   # Clone the repository
   git clone https://github.com/99thDragon/love-live-style-guide.git
   cd love-live-style-guide
   ```

## How to Use

1. **Running the Application**:
   ```bash
   python simple_rag_gui.py
   ```

2. **Using the Search**:
   - Enter your query in the search box (e.g., "character movement")
   - Click "Search" or press Enter
   - View results with highlighted keywords
   - Scroll through results if needed
   - The progress indicator will show when the search is processing

3. **Understanding Results**:
   - Results are displayed in numbered format
   - Keywords from your query are highlighted in yellow
   - Each result is separated by blank lines for better readability

## Example Queries

Try these example queries to explore the style guide:
- "character movement"
- "color palette"
- "facial expressions"
- "background art"
- "musical sequences"
- "character design"

## Project Structure

```
love-live-style-guide/
├── README.md              # Project documentation
├── simple_rag_gui.py     # Main GUI application
├── simple_rag.py         # Command-line version
├── love_live_style_notes.txt  # Knowledge base
└── .gitignore            # Git configuration
```

## Contributing

We welcome contributions! Here's how you can help:

1. **Adding Style Information**:
   - Edit `love_live_style_notes.txt` to add more style details
   - Follow the existing format for consistency

2. **Improving Search**:
   - Enhance the search algorithm in `simple_rag_gui.py`
   - Add more sophisticated matching techniques

3. **GUI Enhancements**:
   - Modify the interface in `simple_rag_gui.py`
   - Add new visual features
   - Improve user experience

4. **New Features**:
   - Add image support
   - Implement advanced search filters
   - Add export functionality

## Development Workflow

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is open source and available under the MIT License. See the LICENSE file for details.

## Acknowledgments

- Love Live! Sunshine!! for the inspiration
- Python and tkinter for the development tools
- The open-source community for their support

## Future Plans

- [ ] Add image support for visual examples
- [ ] Implement semantic search capabilities
- [ ] Create a web-based version
- [ ] Add user authentication for collaborative editing
- [ ] Develop a mobile app version 