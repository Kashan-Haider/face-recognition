import tkinter as tk
from tkinter import ttk
import cv2
from deepface import DeepFace
from PIL import Image, ImageTk
import os
from datetime import datetime
import json
import threading

class AttendanceSystem(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("Face Recognition Attendance")
        self.configure(bg="#f0f2f5")
        self.geometry("900x700")
        
        self.colors = {
            'primary': '#4a90e2',
            'success': '#2ecc71',
            'error': '#e74c3c',
            'background': '#f0f2f5',
            'card': '#ffffff',
            'text': '#2c3e50'
        }
        
        self.db_path = "db"  # Folder containing reference images
        self.camera = None
        self.camera_active = False
        
        self._create_styles()
        self._create_widgets()
        self._create_layout()
        
    def _create_styles(self):
        style = ttk.Style()
        style.theme_use('default')
        
        style.configure(
            'Custom.TButton',
            background=self.colors['primary'],
            foreground='white',
            padding=10,
            font=('Helvetica', 10)
        )
        
        style.configure(
            'Card.TFrame',
            background=self.colors['card']
        )

    def _create_widgets(self):
        self.main_frame = ttk.Frame(self, style='Card.TFrame', padding="20")
        
        # Camera frame
        self.camera_frame = ttk.Frame(self.main_frame, style='Card.TFrame')
        self.camera_label = tk.Label(
            self.camera_frame,
            text="Camera not started",
            bg=self.colors['card']
        )
        
        # Controls
        self.controls_frame = ttk.Frame(self.main_frame, style='Card.TFrame')
        self.toggle_camera_btn = ttk.Button(
            self.controls_frame,
            text="Start Camera",
            style='Custom.TButton',
            command=self.toggle_camera
        )
        self.verify_btn = ttk.Button(
            self.controls_frame,
            text="Verify Face",
            style='Custom.TButton',
            command=self.verify_face,
            state='disabled'
        )
        
        # Status display
        self.status_frame = ttk.Frame(self.main_frame, style='Card.TFrame')
        self.status_label = tk.Label(
            self.status_frame,
            text="Welcome! Start the camera to begin verification.",
            wraplength=600,
            justify="center",
            bg=self.colors['card'],
            fg=self.colors['text'],
            font=('Helvetica', 12)
        )

    def _create_layout(self):
        self.main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Camera area
        self.camera_frame.pack(fill='both', expand=True, pady=10)
        self.camera_label.pack(pady=10)
        
        # Controls
        self.controls_frame.pack(fill='x', pady=20)
        self.toggle_camera_btn.pack(side='left', padx=5)
        self.verify_btn.pack(side='left', padx=5)
        
        # Status
        self.status_frame.pack(fill='x', pady=10)
        self.status_label.pack(pady=10)

    def toggle_camera(self):
        if not self.camera_active:
            self.camera = cv2.VideoCapture(0)
            self.camera_active = True
            self.toggle_camera_btn.config(text="Stop Camera")
            self.verify_btn.config(state='normal')
            self.update_camera()
        else:
            self.camera_active = False
            self.camera.release()
            self.toggle_camera_btn.config(text="Start Camera")
            self.verify_btn.config(state='disabled')
            self.camera_label.config(image='')
            self.camera_label.config(text="Camera stopped")

    def update_camera(self):
        if self.camera_active:
            ret, frame = self.camera.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = cv2.resize(frame, (640, 480))
                image = Image.fromarray(frame)
                photo = ImageTk.PhotoImage(image=image)
                self.camera_label.config(image=photo)
                self.camera_label.image = photo
            self.after(10, self.update_camera)

    def verify_face(self):
        if not self.camera_active:
            return
            
        ret, frame = self.camera.read()
        if not ret:
            return
            
        # Save current frame temporarily
        temp_path = "temp.jpg"
        cv2.imwrite(temp_path, frame)
        
        # Check against database
        best_match = None
        min_distance = float('inf')
        
        try:
            for img_name in os.listdir(self.db_path):
                if img_name.lower().endswith(('.png', '.jpg', '.jpeg')):
                    db_img_path = os.path.join(self.db_path, img_name)
                    result = DeepFace.verify(
                        img1_path=temp_path,
                        img2_path=db_img_path,
                        enforce_detection=True
                    )
                    
                    if result['verified'] and result['distance'] < min_distance:
                        min_distance = result['distance']
                        best_match = img_name.split('.')[0]  # Remove extension
            
            if best_match:
                self._record_attendance(best_match)
                self.status_label.config(
                    text=f"✓ Welcome {best_match}!\nAttendance recorded at {datetime.now().strftime('%H:%M:%S')}",
                    fg=self.colors['success']
                )
            else:
                self.status_label.config(
                    text="❌ No matching face found in database",
                    fg=self.colors['error']
                )
                
        except Exception as e:
            self.status_label.config(
                text=f"Error during verification: {str(e)}",
                fg=self.colors['error']
            )
            
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def _record_attendance(self, name):
        date = datetime.now().strftime("%Y-%m-%d")
        time = datetime.now().strftime("%H:%M:%S")
        
        attendance_file = "attendance.json"
        attendance_data = {}
        
        if os.path.exists(attendance_file):
            with open(attendance_file, 'r') as f:
                attendance_data = json.load(f)
        
        if date not in attendance_data:
            attendance_data[date] = {}
            
        attendance_data[date][name] = time
        
        with open(attendance_file, 'w') as f:
            json.dump(attendance_data, f, indent=4)

if __name__ == "__main__":
    app = AttendanceSystem()
    app.mainloop()