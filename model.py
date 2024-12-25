import tkinter as tk
from tkinter import ttk
import cv2
from deepface import DeepFace
from PIL import Image, ImageTk
import os
from datetime import datetime
import json

class ModernAttendanceSystem(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("Smart Attendance System")
        self.configure(bg="#0f172a")
        self.geometry("720x1280")  
        self.resizable(True, True)  # Fixed window size
        
        self.colors = {
            'primary': '#3b82f6',
            'primary_light': '#BEBEBE',
            'secondary': '#475569',
            'success': '#22c55e',
            'error': '#ef4444',
            'background': '#0f172a',
            'card': '#1e293b',
            'text': '#f8fafc',
            'textDark': '#000000',
            'subtext': '#94a3b8'
        }
        
        self.db_path = "db"
        self.camera = None
        self.camera_active = False
        
        self._create_styles()
        self._create_widgets()
        self._create_layout()

    def _create_styles(self):
        style = ttk.Style()
        style.theme_use('default')
        
        style.configure(
            'Primary.TButton',
            background=self.colors['primary_light'],
            foreground=self.colors['textDark'],
            padding=(20, 10),
            font=('Inter', 11, 'bold')
        )
        
        style.configure(
            'Secondary.TButton',
            background=self.colors['secondary'],
            foreground=self.colors['textDark'],
            padding=(20, 10),
            font=('Inter', 11)
        )
        
        style.configure(
            'Card.TFrame',
            background=self.colors['card']
        )

    def _create_widgets(self):
        self.main_frame = ttk.Frame(self, style='Card.TFrame')
        
        # Header
        self.header_frame = tk.Frame(self.main_frame, bg=self.colors['card'])
        self.title_label = tk.Label(
            self.header_frame,
            text="Face Recognition Attendance",
            font=('Inter', 24, 'bold'),
            bg=self.colors['card'],
            fg=self.colors['text']
        )
        
        # Camera frame
        self.camera_frame = tk.Frame(
            self.main_frame,
            bg=self.colors['card'],
            highlightbackground=self.colors['primary'],
            highlightthickness=2
        )
        self.camera_label = tk.Label(
            self.camera_frame,
            text="Camera not started",
            bg=self.colors['card'],
            fg=self.colors['subtext'],
            font=('Inter', 12)
        )
        
        # Controls
        self.controls_frame = tk.Frame(self.main_frame, bg=self.colors['card'])
        
        self.toggle_camera_btn = ttk.Button(
            self.controls_frame,
            text="Start Camera",
            style='Primary.TButton',
            command=self.toggle_camera
        )
        
        self.verify_btn = ttk.Button(
            self.controls_frame,
            text="Verify Face",
            style='Secondary.TButton',
            command=self.verify_face,
            state='disabled'
        )
        
        self.try_again_btn = ttk.Button(
            self.controls_frame,
            text="Try Again",
            style='Secondary.TButton',
            command=self.reset_system
        )
        
        # Status
        self.status_label = tk.Label(
            self.main_frame,
            text="Welcome! Start the camera to begin verification.",
            wraplength=600,
            justify="center",
            bg=self.colors['card'],
            fg=self.colors['text'],
            font=('Inter', 12)
        )

    def _create_layout(self):
        self.main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Header
        self.header_frame.pack(fill='x', pady=(0, 20))
        self.title_label.pack(pady=10)
        
        # Camera
        self.camera_frame.pack(fill='both', expand=True, padx=10, pady=10)
        self.camera_label.pack(expand=True, pady=10)
        
        # Controls
        self.controls_frame.pack(fill='x', pady=15)
        self.toggle_camera_btn.pack(side='left', padx=5)
        self.verify_btn.pack(side='left', padx=5)
        
        # Status
        self.status_label.pack(fill='x', pady=10)

    def update_camera(self):
        if self.camera_active:
            ret, frame = self.camera.read()
            if ret:
                # Draw guide overlay
                h, w = frame.shape[:2]
                center_x, center_y = w//2, h//2
                size = min(w, h) // 2
                width = int(size * 0.5)  # Experiment with this ratio for best results
                height = int(size * 0.8)

                cv2.ellipse(frame, (center_x, center_y), (width, height), 0, 0, 360, (78, 99, 235), 2)
                
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = cv2.resize(frame, (640, 480))  # Smaller camera preview
                image = Image.fromarray(frame)
                photo = ImageTk.PhotoImage(image=image)
                self.camera_label.config(image=photo)
                self.camera_label.image = photo
            self.after(10, self.update_camera)

    def toggle_camera(self):
        if not self.camera_active:
            self.camera = cv2.VideoCapture(0)
            self.camera_active = True
            self.toggle_camera_btn.config(text="Stop Camera")
            self.verify_btn.config(state='normal')
            self.update_camera()
            self.status_label.config(
                text="Camera active. Position your face in the frame and click Verify.",
                fg=self.colors['text']
            )
        else:
            self.camera_active = False
            self.camera.release()
            self.toggle_camera_btn.config(text="Start Camera")
            self.verify_btn.config(state='disabled')
            self.camera_label.config(image='')
            self.camera_label.config(text="Camera stopped")

    def verify_face(self):
        if not self.camera_active:
            return
            
        ret, frame = self.camera.read()
        if not ret:
            return
            
        temp_path = "temp.jpg"
        cv2.imwrite(temp_path, frame)
        
        try:
            best_match = None
            min_distance = float('inf')
            
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
                        best_match = img_name.split('.')[0]
            
            if best_match:
                self._record_attendance(best_match)
                self.show_success(best_match)
            else:
                self.show_failure()
                
        except Exception as e:
            self.show_failure(str(e))
            
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            self.camera_active = False
            self.camera.release()
            self.verify_btn.config(state='disabled')
            self.toggle_camera_btn.pack_forget()
            self.verify_btn.pack_forget()
            self.try_again_btn.pack(expand=True)

    def show_success(self, name):
        self.status_label.config(
            text=f"✓ Welcome {name}!\nAttendance recorded at {datetime.now().strftime('%H:%M:%S')}",
            fg=self.colors['success']
        )

    def show_failure(self, error_msg=""):
        message = "❌ No matching face found" if not error_msg else f"❌ Error: {error_msg}"
        self.status_label.config(text=message, fg=self.colors['error'])

    def reset_system(self):
        self.camera_label.config(text="Camera not started", image='')
        self.try_again_btn.pack_forget()
        self.toggle_camera_btn.pack(side='left', padx=5)
        self.verify_btn.pack(side='left', padx=5)
        self.status_label.config(
            text="Welcome! Start the camera to begin verification.",
            fg=self.colors['text']
        )

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
    app = ModernAttendanceSystem()
    app.mainloop()