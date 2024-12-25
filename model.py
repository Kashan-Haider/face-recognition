import tkinter as tk
from tkinter import filedialog, ttk
from deepface import DeepFace
from pathlib import Path
import json
from PIL import Image, ImageTk

class ModernFaceComparer(tk.Tk):
    def __init__(self):
        super().__init__()

        # Configure main window
        self.title("Face Comparison")
        self.configure(bg="#f0f2f5")
        self.geometry("800x600")
        
        # Custom colors
        self.colors = {
            'primary': '#4a90e2',
            'secondary': '#67b246',
            'background': '#f0f2f5',
            'card': '#ffffff',
            'text': '#2c3e50'
        }

        # Initialize variables
        self.img1_path = tk.StringVar()
        self.img2_path = tk.StringVar()
        self.img1_preview = None
        self.img2_preview = None

        self._create_styles()
        self._create_widgets()
        self._create_layout()

    def _create_styles(self):
        # Configure ttk styles
        style = ttk.Style()
        style.theme_use('default')
        
        # Button style
        style.configure(
            'Custom.TButton',
            background=self.colors['primary'],
            foreground='white',
            padding=10,
            font=('Helvetica', 10),
            borderwidth=0
        )
        
        # Frame style
        style.configure(
            'Card.TFrame',
            background=self.colors['card'],
            relief='flat',
            borderwidth=0
        )

    def _create_widgets(self):
        # Main container
        self.main_frame = ttk.Frame(self, style='Card.TFrame', padding="20")
        
        # Image selection frames
        self.img1_frame = ttk.Frame(self.main_frame, style='Card.TFrame')
        self.img2_frame = ttk.Frame(self.main_frame, style='Card.TFrame')

        # Create preview labels
        self.preview1_label = tk.Label(
            self.img1_frame,
            text="No image selected",
            bg=self.colors['card'],
            fg=self.colors['text']
        )
        self.preview2_label = tk.Label(
            self.img2_frame,
            text="No image selected",
            bg=self.colors['card'],
            fg=self.colors['text']
        )

        # Buttons
        self.btn1 = ttk.Button(
            self.img1_frame,
            text="Select Image 1",
            style='Custom.TButton',
            command=lambda: self.select_image(1)
        )
        self.btn2 = ttk.Button(
            self.img2_frame,
            text="Select Image 2",
            style='Custom.TButton',
            command=lambda: self.select_image(2)
        )
        self.compare_btn = ttk.Button(
            self.main_frame,
            text="Compare Faces",
            style='Custom.TButton',
            command=self.compare_images
        )

        # Result display
        self.result_frame = ttk.Frame(self.main_frame, style='Card.TFrame')
        self.result_label = tk.Label(
            self.result_frame,
            text="",
            wraplength=600,
            justify="left",
            bg=self.colors['card'],
            fg=self.colors['text'],
            font=('Helvetica', 10)
        )

    def _create_layout(self):
        # Configure grid
        self.main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Image selection area
        self.img1_frame.pack(side='left', fill='both', expand=True, padx=10)
        self.img2_frame.pack(side='right', fill='both', expand=True, padx=10)

        # Preview labels
        self.preview1_label.pack(pady=10)
        self.preview2_label.pack(pady=10)

        # Buttons
        self.btn1.pack(pady=5)
        self.btn2.pack(pady=5)
        self.compare_btn.pack(pady=20)

        # Result area
        self.result_frame.pack(fill='both', expand=True, pady=20)
        self.result_label.pack(pady=10)

    def select_image(self, image_num):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.jpg *.jpeg *.png")]
        )
        if file_path:
            if image_num == 1:
                self.img1_path.set(file_path)
                self._update_preview(file_path, self.preview1_label)
            else:
                self.img2_path.set(file_path)
                self._update_preview(file_path, self.preview2_label)

    def _update_preview(self, image_path, label):
        try:
            # Load and resize image for preview
            image = Image.open(image_path)
            image.thumbnail((150, 150))
            photo = ImageTk.PhotoImage(image)
            label.config(image=photo)
            label.image = photo  # Keep a reference
        except Exception as e:
            label.config(text=f"Error loading preview: {str(e)}")

    def compare_images(self):
        if not self.img1_path.get() or not self.img2_path.get():
            self.result_label.config(
                text="Please select both images first.",
                fg='#e74c3c'
            )
            return

        try:
            result = DeepFace.verify(
                img1_path=self.img1_path.get(),
                img2_path=self.img2_path.get()
            )
            
            # Format result
            is_match = result['verified']
            distance = result['distance']
            
            # Create formatted result text
            if is_match:
                match_text = "✓ Images are a match"
                color = self.colors['secondary']
            else:
                match_text = "✗ Images do not match"
                color = '#e74c3c'
                
            result_text = f"{match_text}\nConfidence Distance: {distance:.4f}\nModel: {result['model']}"
            
            self.result_label.config(text=result_text, fg=color)
            
        except Exception as e:
            self.result_label.config(
                text=f"Error during comparison: {str(e)}",
                fg='#e74c3c'
            )

if __name__ == "__main__":
    app = ModernFaceComparer()
    app.mainloop()