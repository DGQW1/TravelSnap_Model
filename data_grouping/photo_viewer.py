import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import os
from pathlib import Path

class PhotoViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("Travel Photo Viewer")
        self.root.geometry("1200x800")
        
        # Data storage
        self.photo_groups = []
        self.current_group_index = 0
        self.current_photo_index = 0
        self.photo_path = ""
        
        # Create GUI
        self.create_widgets()
        
        # Load photo groups
        self.load_photo_groups()
        
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Load JSON button
        ttk.Button(main_frame, text="Load Photo Groups JSON", 
                  command=self.load_json_file).grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        # Group navigation
        group_frame = ttk.LabelFrame(main_frame, text="Group Navigation", padding="5")
        group_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(group_frame, text="Previous Group", 
                  command=self.previous_group).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(group_frame, text="Next Group", 
                  command=self.next_group).pack(side=tk.LEFT, padx=(0, 5))
        
        # Group info
        self.group_label = ttk.Label(group_frame, text="Group: 0/0", font=("Arial", 12, "bold"))
        self.group_label.pack(side=tk.LEFT, padx=(20, 0))
        
        # Photo navigation
        photo_frame = ttk.LabelFrame(main_frame, text="Photo Navigation", padding="5")
        photo_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(photo_frame, text="Previous Photo", 
                  command=self.previous_photo).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(photo_frame, text="Next Photo", 
                  command=self.next_photo).pack(side=tk.LEFT, padx=(0, 5))
        
        self.photo_label = ttk.Label(photo_frame, text="Photo: 0/0", font=("Arial", 12, "bold"))
        self.photo_label.pack(side=tk.LEFT, padx=(20, 0))
        
        # Image display area
        image_frame = ttk.LabelFrame(main_frame, text="Photo Display", padding="5")
        image_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        image_frame.columnconfigure(0, weight=1)
        image_frame.rowconfigure(0, weight=1)
        
        self.image_label = ttk.Label(image_frame, text="No image loaded")
        self.image_label.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Info display area
        info_frame = ttk.LabelFrame(main_frame, text="Photo Information", padding="5")
        info_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        info_frame.columnconfigure(1, weight=1)
        
        ttk.Label(info_frame, text="Location:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.location_label = ttk.Label(info_frame, text="", font=("Arial", 10, "bold"))
        self.location_label.grid(row=0, column=1, sticky=tk.W)
        
        # Add next location button
        ttk.Button(info_frame, text="Next Location", 
                  command=self.next_group).grid(row=0, column=2, sticky=tk.W, padx=(10, 0))
         
        ttk.Label(info_frame, text="Time:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10))
        self.time_label = ttk.Label(info_frame, text="")
        self.time_label.grid(row=1, column=1, sticky=tk.W)
        
        ttk.Label(info_frame, text="Summary:").grid(row=2, column=0, sticky=tk.W, padx=(0, 10))
        self.summary_label = ttk.Label(info_frame, text="", wraplength=800)
        self.summary_label.grid(row=2, column=1, sticky=tk.W)
        
        # Photo path display
        path_frame = ttk.LabelFrame(main_frame, text="Photo Path", padding="5")
        path_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        path_frame.columnconfigure(0, weight=1)
        
        self.path_label = ttk.Label(path_frame, text="", wraplength=1000)
        self.path_label.grid(row=0, column=0, sticky=tk.W)
        
    def load_photo_groups(self):
        """Try to load photo_groups.json from the current directory"""
        json_path = Path("src/results/photo_groups.json")   
        if json_path.exists():
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    self.photo_groups = json.load(f)
                self.update_display()
                messagebox.showinfo("Success", f"Loaded {len(self.photo_groups)} photo groups")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load photo_groups.json: {e}")
        else:
            messagebox.showinfo("Info", "photo_groups.json not found. Please use 'Load Photo Groups JSON' button.")
    
    def load_json_file(self):
        """Load JSON file from file dialog"""
        file_path = filedialog.askopenfilename(
            title="Select Photo Groups JSON file",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.photo_groups = json.load(f)
                self.current_group_index = 0
                self.current_photo_index = 0
                self.update_display()
                messagebox.showinfo("Success", f"Loaded {len(self.photo_groups)} photo groups")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file: {e}")
    
    def update_display(self):
        """Update the display with current group and photo"""
        if not self.photo_groups:
            return
            
        group = self.photo_groups[self.current_group_index]
        photos = group.get("照片", [])
        
        if photos:
            current_photo = photos[self.current_photo_index]
            
            # Update labels
            self.group_label.config(text=f"Group: {self.current_group_index + 1}/{len(self.photo_groups)}")
            self.photo_label.config(text=f"Photo: {self.current_photo_index + 1}/{len(photos)}")
            
            # Update info
            self.location_label.config(text=group.get("景点名称", "Unknown Location"))
            self.time_label.config(text=group.get("时间", "No time specified"))
            self.summary_label.config(text=group.get("总结", "No summary available"))
            
            # Update photo path
            self.path_label.config(text=f"Photo file: {current_photo}")
            
            # Try to display image if it exists
            self.display_image(current_photo)
        else:
            self.clear_display()
    
    def display_image(self, photo_filename):
        """Display the image if it exists"""
        # Look for the image in common directories
        possible_paths = [
            Path(photo_filename),
            Path("src/processed/img") / photo_filename,
        ]
        
        image_path = None
        for path in possible_paths:
            if path.exists() and path.is_file():
                image_path = path
                break
        
        if image_path:
            try:
                # Load and resize image
                image = Image.open(image_path)
                
                # Calculate resize dimensions (max 600x400)
                max_width, max_height = 600, 400
                width, height = image.size
                
                if width > max_width or height > max_height:
                    ratio = min(max_width / width, max_height / height)
                    new_width = int(width * ratio)
                    new_height = int(height * ratio)
                    image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # Convert to PhotoImage
                photo = ImageTk.PhotoImage(image)
                
                # Update image label
                self.image_label.config(image=photo, text="")
                self.image_label.image = photo  # Keep a reference
                
            except Exception as e:
                self.image_label.config(image="", text=f"Error loading image: {e}")
        else:
            self.image_label.config(image="", text=f"Image not found: {photo_filename}")
    
    def change_location(self):
        """Change the location for the current group"""
        if not self.photo_groups:
            return
            
        # Create a simple dialog for input
        dialog = tk.Toplevel(self.root)
        dialog.title("Change Location")
        dialog.geometry("400x150")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.geometry("+%d+%d" % (self.root.winfo_rootx() + 50, self.root.winfo_rooty() + 50))
        
        # Current location
        current_location = self.photo_groups[self.current_group_index].get("景点名称", "")
        
        ttk.Label(dialog, text="Current Location:").pack(pady=(10, 5))
        ttk.Label(dialog, text=current_location, font=("Arial", 10, "bold")).pack(pady=(0, 10))
        
        ttk.Label(dialog, text="New Location:").pack(pady=(5, 5))
        entry = ttk.Entry(dialog, width=40)
        entry.pack(pady=(0, 10))
        entry.insert(0, current_location)
        entry.select_range(0, tk.END)
        entry.focus()
        
        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=(10, 0))
        
        def save_location():
            new_location = entry.get().strip()
            if new_location:
                self.photo_groups[self.current_group_index]["景点名称"] = new_location
                self.update_display()
                dialog.destroy()
                messagebox.showinfo("Success", f"Location changed to: {new_location}")
            else:
                messagebox.showerror("Error", "Location cannot be empty")
        
        def cancel():
            dialog.destroy()
        
        ttk.Button(button_frame, text="Save", command=save_location).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Cancel", command=cancel).pack(side=tk.LEFT)
        
        # Bind Enter key to save
        entry.bind('<Return>', lambda e: save_location())
        entry.bind('<Escape>', lambda e: cancel())
    
    def clear_display(self):
        """Clear the display"""
        self.image_label.config(image="", text="No image available")
        self.location_label.config(text="")
        self.time_label.config(text="")
        self.summary_label.config(text="")
        self.path_label.config(text="")
    
    def next_group(self):
        """Go to next group"""
        if self.photo_groups:
            self.current_group_index = (self.current_group_index + 1) % len(self.photo_groups)
            self.current_photo_index = 0
            self.update_display()
    
    def previous_group(self):
        """Go to previous group"""
        if self.photo_groups:
            self.current_group_index = (self.current_group_index - 1) % len(self.photo_groups)
            self.current_photo_index = 0
            self.update_display()
    
    def next_photo(self):
        """Go to next photo in current group"""
        if self.photo_groups:
            group = self.photo_groups[self.current_group_index]
            photos = group.get("照片", [])
            if photos:
                self.current_photo_index = (self.current_photo_index + 1) % len(photos)
                self.update_display()
    
    def previous_photo(self):
        """Go to previous photo in current group"""
        if self.photo_groups:
            group = self.photo_groups[self.current_group_index]
            photos = group.get("照片", [])
            if photos:
                self.current_photo_index = (self.current_photo_index - 1) % len(photos)
                self.update_display()

def main():
    root = tk.Tk()
    app = PhotoViewer(root)
    root.mainloop()

if __name__ == "__main__":
    main() 