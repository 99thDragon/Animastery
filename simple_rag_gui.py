import re
import tkinter as tk
from tkinter import ttk, scrolledtext
import time
from tkinter import font as tkfont

def read_knowledge_base(file_path):
    """
    Reads the content of the knowledge base file.
    Returns the content as a string.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        return "Error: The knowledge base file was not found."
    except Exception as e:
        return f"Error reading file: {e}"

def search_knowledge_base(content, query):
    """
    Performs a simple keyword-based search in the content.
    Returns relevant sentences containing the query keywords.
    """
    if not content or content.startswith("Error"):
        return []
    
    # Split content into sentences
    sentences = re.split(r'(?<=[.!?])\s+', content)
    
    # Convert query to lowercase and split into keywords
    keywords = query.lower().split()
    
    # Find sentences containing any of the keywords
    relevant_sentences = []
    for sentence in sentences:
        sentence_lower = sentence.lower()
        if any(keyword in sentence_lower for keyword in keywords):
            relevant_sentences.append(sentence.strip())
    
    return relevant_sentences

class PlaceholderEntry(ttk.Entry):
    def __init__(self, master=None, placeholder="", *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.placeholder = placeholder
        self.placeholder_color = 'grey'
        self.default_fg_color = self['foreground']
        
        self.bind("<FocusIn>", self._clear_placeholder)
        self.bind("<FocusOut>", self._add_placeholder)
        
        self._add_placeholder(None)
    
    def _clear_placeholder(self, event):
        if self.get() == self.placeholder:
            self.delete(0, tk.END)
            self['foreground'] = self.default_fg_color
    
    def _add_placeholder(self, event):
        if not self.get():
            self.insert(0, self.placeholder)
            self['foreground'] = self.placeholder_color

class RAGGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Love Live! Style Guide Assistant")
        
        # Set minimum window size
        self.root.minsize(600, 400)
        
        # Create main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create and configure the grid
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=1)  # Changed from 2 to 3 to accommodate title
        
        # Create custom font for title
        title_font = tkfont.Font(family="Helvetica", size=16, weight="bold")
        
        # Title frame
        title_frame = ttk.Frame(main_frame)
        title_frame.grid(row=0, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Title label
        title_label = ttk.Label(title_frame, 
                              text="Love Live! Sunshine!! Style Guide Search",
                              font=title_font,
                              foreground="#2c3e50")  # Dark blue-gray color
        title_label.pack(side=tk.LEFT)
        
        # Optional: Image support (commented out - uncomment and add image file to use)
        """
        try:
            # Load and display image
            image = tk.PhotoImage(file="logo.png")  # Replace with your image filename
            image_label = ttk.Label(title_frame, image=image)
            image_label.image = image  # Keep a reference
            image_label.pack(side=tk.RIGHT, padx=10)
        except Exception as e:
            print(f"Could not load image: {e}")
        """
        
        # Query label and entry
        ttk.Label(main_frame, text="Enter your query:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.query_entry = PlaceholderEntry(main_frame, 
                                          placeholder="e.g., character design, movement, or colors",
                                          width=50)
        self.query_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Search button
        self.search_button = ttk.Button(main_frame, text="Search", command=self.perform_search)
        self.search_button.grid(row=1, column=2, padx=5, pady=5)
        
        # Progress indicator label
        self.progress_label = ttk.Label(main_frame, text="", foreground="blue")
        self.progress_label.grid(row=1, column=3, padx=5, pady=5)
        
        # Results label
        ttk.Label(main_frame, text="Search Results:").grid(row=2, column=0, columnspan=4, sticky=tk.W, pady=5)
        
        # Results text area
        self.results_text = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, width=70, height=20)
        self.results_text.grid(row=3, column=0, columnspan=4, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Configure text widget tags for highlighting
        self.results_text.tag_configure('highlight', background='yellow', foreground='black')
        
        # Read the knowledge base
        self.knowledge_base = read_knowledge_base("love_live_style_notes.txt")
        
        # Bind Enter key to search
        self.query_entry.bind('<Return>', lambda event: self.perform_search())
    
    def show_progress(self):
        """Shows the progress indicator and updates the button text"""
        self.search_button['text'] = "Searching..."
        self.progress_label['text'] = "Loading..."
        self.root.update()  # Force UI update
    
    def hide_progress(self):
        """Hides the progress indicator and resets the button text"""
        self.search_button['text'] = "Search"
        self.progress_label['text'] = ""
        self.root.update()  # Force UI update
    
    def highlight_keywords(self, text, keywords):
        """
        Highlights all occurrences of keywords in the text widget.
        """
        # Remove any existing highlights
        self.results_text.tag_remove('highlight', '1.0', tk.END)
        
        # Convert keywords to lowercase for case-insensitive search
        keywords = [k.lower() for k in keywords]
        
        # Get the current content
        content = self.results_text.get('1.0', tk.END)
        
        # Find and highlight each keyword
        for keyword in keywords:
            start = '1.0'
            while True:
                # Search for the keyword (case-insensitive)
                pos = self.results_text.search(keyword, start, tk.END, nocase=True)
                if not pos:
                    break
                
                # Calculate end position
                end = f"{pos}+{len(keyword)}c"
                
                # Apply highlight tag
                self.results_text.tag_add('highlight', pos, end)
                
                # Move start position for next search
                start = end
    
    def perform_search(self):
        """Performs the search and updates the results area"""
        # Clear previous results
        self.results_text.delete(1.0, tk.END)
        
        # Get the query
        query = self.query_entry.get().strip()
        
        # Don't search if the query is empty or is the placeholder
        if not query or query == self.query_entry.placeholder:
            self.results_text.insert(tk.END, "Please enter a search query.")
            return
        
        # Show progress indicator
        self.show_progress()
        
        # Simulate a brief delay to show the progress indicator
        self.root.after(100, self._complete_search, query)
    
    def _complete_search(self, query):
        """Completes the search process after the delay"""
        # Perform the search
        results = search_knowledge_base(self.knowledge_base, query)
        
        # Display results
        if results:
            for i, sentence in enumerate(results, 1):
                self.results_text.insert(tk.END, f"{i}. {sentence}\n\n")
            
            # Highlight keywords in the results
            self.highlight_keywords(self.results_text, query.split())
        else:
            self.results_text.insert(tk.END, "No relevant information found for your query.")
        
        # Hide progress indicator
        self.hide_progress()

def main():
    root = tk.Tk()
    app = RAGGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 