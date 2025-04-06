import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog
import tkinter.font as tkFont
from PIL import Image, ImageTk
import json
import os
from typing import List, Dict
import threading
import time
from datetime import datetime

class StyleGuideGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Animastery - Animation Style Guide")
        self.root.geometry("1200x800")
        
        # Theme states
        self.is_dark_mode = False
        
        # Colors
        self.light_theme = {
            "primary": "#FF6B6B",  # Coral pink
            "secondary": "#4ECDC4",  # Turquoise
            "background": "#f0f0f0",
            "text": "#2C3E50",
            "highlight": "#FFE66D",
            "card": "white"
        }
        
        self.dark_theme = {
            "primary": "#FF6B6B",
            "secondary": "#4ECDC4",
            "background": "#1a1a1a",
            "text": "#ffffff",
            "highlight": "#FFE66D",
            "card": "#2d2d2d"
        }
        
        self.colors = self.light_theme
        
        # Custom fonts
        self.title_font = tkFont.Font(family="Helvetica", size=24, weight="bold")
        self.subtitle_font = tkFont.Font(family="Helvetica", size=16)
        self.body_font = tkFont.Font(family="Helvetica", size=12)
        
        # Categories
        self.categories = [
            "All",
            "Character Design",
            "Animation",
            "Background Art",
            "Special Effects",
            "Color Palette"
        ]
        
        self.setup_ui()
        self.load_style_notes()
        
    def setup_ui(self):
        # Configure ttk style
        self.style = ttk.Style()
        self.style.configure("TCombobox", 
                           fieldbackground=self.colors["card"],
                           background=self.colors["background"])
        
        # Main container with padding
        self.main_container = tk.Frame(self.root, bg=self.colors["background"], padx=20, pady=20)
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Header with logo and title
        header_frame = tk.Frame(self.main_container, bg=self.colors["background"])
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Load and display logo
        try:
            logo_img = Image.open("logo.png")
            logo_img = logo_img.resize((50, 50), Image.Resampling.LANCZOS)
            self.logo_photo = ImageTk.PhotoImage(logo_img)
            logo_label = tk.Label(header_frame, image=self.logo_photo, bg=self.colors["background"])
            logo_label.pack(side=tk.LEFT, padx=(0, 10))
        except:
            pass
        
        # Title
        title_label = tk.Label(
            header_frame,
            text="Animastery",
            font=self.title_font,
            bg=self.colors["background"],
            fg=self.colors["text"]
        )
        title_label.pack(side=tk.LEFT)
        
        # Subtitle
        subtitle_label = tk.Label(
            header_frame,
            text="Animation Style Guide",
            font=self.subtitle_font,
            bg=self.colors["background"],
            fg=self.colors["text"]
        )
        subtitle_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Dark mode toggle
        self.theme_button = tk.Button(
            header_frame,
            text="🌙 Dark Mode",
            command=self.toggle_theme,
            bg=self.colors["card"],
            fg=self.colors["text"],
            font=self.body_font,
            relief=tk.FLAT,
            cursor="hand2"
        )
        self.theme_button.pack(side=tk.RIGHT)
        
        # Search and filter section
        search_frame = tk.Frame(self.main_container, bg=self.colors["background"])
        search_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Category dropdown
        self.category_var = tk.StringVar(value="All")
        self.category_dropdown = ttk.Combobox(
            search_frame,
            textvariable=self.category_var,
            values=self.categories,
            state="readonly",
            font=self.body_font,
            width=20
        )
        self.category_dropdown.pack(side=tk.LEFT, padx=(0, 10))
        
        # Search entry with placeholder
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=self.body_font,
            width=50,
            relief=tk.FLAT,
            bg=self.colors["card"],
            fg="gray"
        )
        self.search_entry.pack(side=tk.LEFT, padx=(0, 10))
        self.search_entry.insert(0, "Search style guide...")
        self.search_entry.bind("<FocusIn>", self.clear_placeholder)
        self.search_entry.bind("<FocusOut>", self.restore_placeholder)
        self.search_entry.bind("<Return>", self.search)
        
        # Search button with hover effect
        self.search_button = tk.Button(
            search_frame,
            text="Search",
            command=self.search,
            bg=self.colors["primary"],
            fg="white",
            font=self.body_font,
            relief=tk.FLAT,
            padx=20,
            pady=5,
            cursor="hand2"
        )
        self.search_button.pack(side=tk.LEFT)
        self.search_button.bind("<Enter>", lambda e: self.search_button.config(bg="#FF5252"))
        self.search_button.bind("<Leave>", lambda e: self.search_button.config(bg=self.colors["primary"]))
        
        # Export button
        self.export_button = tk.Button(
            search_frame,
            text="Export Results",
            command=self.export_results,
            bg=self.colors["secondary"],
            fg="white",
            font=self.body_font,
            relief=tk.FLAT,
            padx=20,
            pady=5,
            cursor="hand2"
        )
        self.export_button.pack(side=tk.RIGHT)
        
        # Results area
        self.results_frame = tk.Frame(self.main_container, bg=self.colors["background"])
        self.results_frame.pack(fill=tk.BOTH, expand=True)
        
        # Results text area with custom styling
        self.results_text = scrolledtext.ScrolledText(
            self.results_frame,
            wrap=tk.WORD,
            font=self.body_font,
            bg=self.colors["card"],
            fg=self.colors["text"],
            padx=15,
            pady=15,
            relief=tk.FLAT
        )
        self.results_text.pack(fill=tk.BOTH, expand=True)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        self.status_bar = tk.Label(
            self.main_container,
            textvariable=self.status_var,
            font=self.body_font,
            bg=self.colors["background"],
            fg=self.colors["text"]
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def toggle_theme(self):
        self.is_dark_mode = not self.is_dark_mode
        self.colors = self.dark_theme if self.is_dark_mode else self.light_theme
        
        # Update UI colors
        self.main_container.configure(bg=self.colors["background"])
        
        # Update frames and labels
        for widget in self.main_container.winfo_children():
            if isinstance(widget, tk.Frame):
                widget.configure(bg=self.colors["background"])
                for child in widget.winfo_children():
                    if isinstance(child, tk.Label):
                        child.configure(bg=self.colors["background"], fg=self.colors["text"])
                    elif isinstance(child, tk.Frame):
                        child.configure(bg=self.colors["background"])
        
        # Update specific widgets
        self.search_entry.configure(bg=self.colors["card"], fg=self.colors["text"])
        self.results_text.configure(bg=self.colors["card"], fg=self.colors["text"])
        self.theme_button.configure(
            text="☀️ Light Mode" if self.is_dark_mode else "🌙 Dark Mode",
            bg=self.colors["card"],
            fg=self.colors["text"]
        )
        self.status_bar.configure(bg=self.colors["background"], fg=self.colors["text"])
        
        # Update ttk style
        self.style.configure("TCombobox",
                           fieldbackground=self.colors["card"],
                           background=self.colors["background"])
        
    def clear_placeholder(self, event):
        if self.search_entry.get() == "Search style guide...":
            self.search_entry.delete(0, tk.END)
            self.search_entry.config(fg=self.colors["text"])
            
    def restore_placeholder(self, event):
        if not self.search_entry.get():
            self.search_entry.insert(0, "Search style guide...")
            self.search_entry.config(fg="gray")
            
    def load_style_notes(self):
        try:
            with open("animastery_style_notes.txt", "r", encoding="utf-8") as file:
                self.style_notes = []
                current_category = "General"
                for line in file:
                    line = line.strip()
                    if line.startswith("## "):
                        current_category = line[3:].strip()
                    elif line:  # Only add non-empty lines
                        self.style_notes.append({
                            "category": current_category,
                            "text": line
                        })
        except Exception as e:
            self.status_var.set(f"Error loading style notes: {str(e)}")
            self.style_notes = []
            
    def search(self, event=None):
        query = self.search_var.get().lower()
        category = self.category_var.get()
        
        if query == "search style guide...":
            return
            
        self.status_var.set("Searching...")
        self.results_text.delete(1.0, tk.END)
        
        # Animate search
        self.animate_search()
        
        # Perform search in background
        threading.Thread(target=self.perform_search, args=(query, category), daemon=True).start()
        
    def animate_search(self):
        dots = ["", ".", "..", "..."]
        for i in range(4):
            self.status_var.set(f"Searching{dots[i]}")
            self.root.update()
            time.sleep(0.2)
            
    def perform_search(self, query, category):
        matches = []
        for note in self.style_notes:
            if (category == "All" or note["category"] == category) and query in note["text"].lower():
                matches.append(note)
                
        # Update UI in main thread
        self.root.after(0, self.display_results, matches)
        
    def display_results(self, matches):
        if matches:
            self.results_text.delete(1.0, tk.END)
            current_category = None
            
            for i, match in enumerate(matches, 1):
                if match["category"] != current_category:
                    current_category = match["category"]
                    self.results_text.insert(tk.END, f"\n{current_category}\n", "category_header")
                    
                # Animate each result
                self.root.after(i * 100, self.animate_result, i, match)
                
            self.status_var.set(f"Found {len(matches)} results")
        else:
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, "No results found. Try a different search term.", "no_results")
            self.status_var.set("No results found")
            
        # Configure tags for styling
        self.results_text.tag_configure("category_header",
                                      font=("Helvetica", 14, "bold"),
                                      foreground=self.colors["secondary"])
        self.results_text.tag_configure("result_header", 
                                      font=("Helvetica", 12, "bold"),
                                      foreground=self.colors["primary"])
        self.results_text.tag_configure("result_text",
                                      font=("Helvetica", 11))
        self.results_text.tag_configure("no_results",
                                      font=("Helvetica", 12),
                                      foreground="gray")
                                      
    def animate_result(self, index, match):
        self.results_text.insert(tk.END, f"Result {index}:\n", "result_header")
        self.results_text.insert(tk.END, f"{match['text']}\n\n", "result_text")
        self.results_text.see(tk.END)
        
    def export_results(self):
        try:
            content = self.results_text.get(1.0, tk.END).strip()
            if not content or content == "No results found. Try a different search term.":
                self.status_var.set("No results to export")
                return
                
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                initialfile=f"animastery_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            )
            
            if filename:
                with open(filename, 'w', encoding='utf-8') as file:
                    file.write("Animastery - Animation Style Guide - Search Results\n")
                    file.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                    file.write(content)
                self.status_var.set(f"Results exported to {os.path.basename(filename)}")
        except Exception as e:
            self.status_var.set(f"Error exporting results: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = StyleGuideGUI(root)
    root.mainloop() 