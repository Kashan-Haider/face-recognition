import tkinter as tk
from tkinter import ttk, messagebox
import cv2
from deepface import DeepFace
from PIL import Image, ImageTk
import os
from datetime import datetime, timedelta
import json
import pandas as pd
import plotly.express as px
import webbrowser

class ModernAttendanceSystem(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("Enterprise Attendance System")
        self.configure(bg="#0f172a")
        self.attributes('-zoomed', True)  # Full screen
        
        self.colors = {
            'primary': '#3b82f6',
            'primary_dark': '#1d4ed8',
            'primary_light': '#60a5fa',
            'secondary': '#475569',
            'success': '#22c55e',
            'error': '#ef4444',
            'warning': '#f59e0b',
            'background': '#0f172a',
            'card': '#1e293b',
            'card_dark': '#0f172a',
            'text': '#f8fafc',
            'textDark': '#000000',
            'subtext': '#94a3b8',
            'border': '#2d3748'
        }
        
        self.db_path = "db"
        self.camera = None
        self.camera_active = False
        self.current_page = "home"
        
        self._create_styles()
        self._create_widgets()
        self._create_layout()
        self._create_navigation()

    def _create_styles(self):
        style = ttk.Style()
        style.theme_use('default')
        
        button_styles = {
            'Primary.TButton': {'bg': self.colors['primary'], 'fg': self.colors['text']},
            'Secondary.TButton': {'bg': self.colors['secondary'], 'fg': self.colors['text']},
            'Success.TButton': {'bg': self.colors['success'], 'fg': self.colors['text']},
            'Error.TButton': {'bg': self.colors['error'], 'fg': self.colors['text']},
            'Nav.TButton': {'bg': self.colors['card_dark'], 'fg': self.colors['text']}
        }
        
        for name, colors in button_styles.items():
            style.configure(
                name,
                background=colors['bg'],
                foreground=colors['fg'],
                padding=(20, 10),
                font=('Inter', 11, 'bold')
            )
            
        style.configure(
            'Card.TFrame',
            background=self.colors['card']
        )

    def _create_navigation(self):
        self.nav_frame = tk.Frame(self.main_frame, bg=self.colors['card_dark'])
        self.nav_frame.pack(side='left', fill='y', padx=2)
        
        nav_buttons = [
            ("Home", self.show_home_page),
            ("Statistics", self.show_statistics_page),
            ("Reports", self.show_reports_page),
            ("Settings", self.show_settings_page)
        ]
        
        for text, command in nav_buttons:
            btn = ttk.Button(
                self.nav_frame,
                text=text,
                style='Nav.TButton',
                command=command
            )
            btn.pack(pady=5, padx=10, fill='x')

    def show_home_page(self):
        self.current_page = "home"
        self._clear_main_content()
        
        # Recreate the home page widgets
        self.header_frame = tk.Frame(self.content_frame, bg=self.colors['card'])
        self.title_label = tk.Label(
            self.header_frame,
            text="Enterprise Face Recognition Attendance",
            font=('Inter', 28, 'bold'),
            bg=self.colors['card'],
            fg=self.colors['text']
        )
        
        self.camera_frame = tk.Frame(
            self.content_frame,
            bg=self.colors['card'],
            highlightbackground=self.colors['primary'],
            highlightthickness=2
        )
        self.camera_label = tk.Label(
            self.camera_frame,
            text="Ready to start",
            bg=self.colors['card'],
            fg=self.colors['subtext'],
            font=('Inter', 14)
        )
        
        self.controls_frame = tk.Frame(self.content_frame, bg=self.colors['card'])
        self.toggle_camera_btn = ttk.Button(
            self.controls_frame,
            text="Start Camera",
            style='Primary.TButton',
            command=self.toggle_camera
        )
        self.verify_btn = ttk.Button(
            self.controls_frame,
            text="Verify Identity",
            style='Success.TButton',
            command=self.verify_face,
            state='disabled'
        )
        
        self.status_label = tk.Label(
            self.content_frame,
            text="Welcome to the Enterprise Attendance System",
            wraplength=800,
            justify="center",
            bg=self.colors['card'],
            fg=self.colors['text'],
            font=('Inter', 14)
        )
        
        # Layout the widgets
        self.header_frame.pack(fill='x', pady=(20, 30), padx=20)
        self.title_label.pack(pady=10)
        self.camera_frame.pack(fill='both', expand=True, padx=20, pady=10)
        self.camera_label.pack(expand=True, pady=10)
        self.controls_frame.pack(fill='x', pady=20, padx=20)
        self.toggle_camera_btn.pack(side='left', padx=5)
        self.verify_btn.pack(side='left', padx=5)
        self.status_label.pack(fill='x', pady=20, padx=20)

    def show_statistics_page(self):
        self.current_page = "statistics"
        self._clear_main_content()
        
        stats_frame = ttk.Frame(self.content_frame, style='Card.TFrame')
        stats_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Generate attendance statistics
        attendance_data = self._load_attendance_data()
        if attendance_data:
            self._generate_attendance_charts(stats_frame, attendance_data)
        else:
            tk.Label(
                stats_frame,
                text="No attendance data available",
                bg=self.colors['card'],
                fg=self.colors['text'],
                font=('Inter', 14)
            ).pack(pady=20)

    def show_reports_page(self):
        self.current_page = "reports"
        self._clear_main_content()
        
        reports_frame = ttk.Frame(self.content_frame, style='Card.TFrame')
        reports_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Add report generation options
        tk.Label(
            reports_frame,
            text="Generate Reports",
            font=('Inter', 18, 'bold'),
            bg=self.colors['card'],
            fg=self.colors['text']
        ).pack(pady=10)
        
        report_types = [
            ("Daily Attendance Report", self.generate_daily_report),
            ("Monthly Summary", self.generate_monthly_report),
            ("Late Arrivals Report", self.generate_late_report),
            ("Export All Data (CSV)", self.export_attendance_data)
        ]
        
        for text, command in report_types:
            ttk.Button(
                reports_frame,
                text=text,
                style='Primary.TButton',
                command=command
            ).pack(pady=5)

    def show_settings_page(self):
        self.current_page = "settings"
        self._clear_main_content()
        
        settings_frame = ttk.Frame(self.content_frame, style='Card.TFrame')
        settings_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        tk.Label(
            settings_frame,
            text="Settings",
            font=('Inter', 18, 'bold'),
            bg=self.colors['card'],
            fg=self.colors['text']
        ).pack(pady=10)
        
        # Add settings options
        settings = [
            ("Working Hours", "09:00-17:00"),
            ("Late Threshold (minutes)", "15"),
            ("Camera Device", "0"),
            ("Verification Threshold", "0.6")
        ]
        
        for setting, default in settings:
            frame = tk.Frame(settings_frame, bg=self.colors['card'])
            frame.pack(fill='x', pady=5, padx=20)
            
            tk.Label(
                frame,
                text=setting,
                bg=self.colors['card'],
                fg=self.colors['text'],
                font=('Inter', 12)
            ).pack(side='left')
            
            entry = ttk.Entry(frame)
            entry.insert(0, default)
            entry.pack(side='right')

    def _clear_main_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def _create_widgets(self):
        self.main_frame = ttk.Frame(self, style='Card.TFrame')
        self.content_frame = ttk.Frame(self.main_frame, style='Card.TFrame')
        
        # Header
        self.header_frame = tk.Frame(self.content_frame, bg=self.colors['card'])
        self.title_label = tk.Label(
            self.header_frame,
            text="Enterprise Face Recognition Attendance",
            font=('Inter', 28, 'bold'),
            bg=self.colors['card'],
            fg=self.colors['text']
        )
        
        # Camera frame with improved styling
        self.camera_frame = tk.Frame(
            self.content_frame,
            bg=self.colors['card'],
            highlightbackground=self.colors['primary'],
            highlightthickness=2
        )
        self.camera_label = tk.Label(
            self.camera_frame,
            text="Ready to start",
            bg=self.colors['card'],
            fg=self.colors['subtext'],
            font=('Inter', 14)
        )
        
        # Controls with better styling
        self.controls_frame = tk.Frame(self.content_frame, bg=self.colors['card'])
        
        self.toggle_camera_btn = ttk.Button(
            self.controls_frame,
            text="Start Camera",
            style='Primary.TButton',
            command=self.toggle_camera
        )
        
        self.verify_btn = ttk.Button(
            self.controls_frame,
            text="Verify Identity",
            style='Success.TButton',
            command=self.verify_face,
            state='disabled'
        )
        
        self.try_again_btn = ttk.Button(
            self.controls_frame,
            text="Try Again",
            style='Secondary.TButton',
            command=self.reset_system
        )
        
        # Status with improved visibility
        self.status_label = tk.Label(
            self.content_frame,
            text="Welcome to the Enterprise Attendance System",
            wraplength=800,
            justify="center",
            bg=self.colors['card'],
            fg=self.colors['text'],
            font=('Inter', 14)
        )

    def _create_layout(self):
        self.main_frame.pack(fill='both', expand=True)
        self.content_frame.pack(side='right', fill='both', expand=True)
        
        # Header
        self.header_frame.pack(fill='x', pady=(20, 30), padx=20)
        self.title_label.pack(pady=10)
        
        # Camera
        self.camera_frame.pack(fill='both', expand=True, padx=20, pady=10)
        self.camera_label.pack(expand=True, pady=10)
        
        # Controls
        self.controls_frame.pack(fill='x', pady=20, padx=20)
        self.toggle_camera_btn.pack(side='left', padx=5)
        self.verify_btn.pack(side='left', padx=5)
        
        # Status
        self.status_label.pack(fill='x', pady=20, padx=20)

    def _generate_attendance_charts(self, parent_frame, data):
        # Convert attendance data to pandas DataFrame
        df = pd.DataFrame(data).transpose()
        
        # Daily attendance chart
        daily_attendance = len(df.columns)
        tk.Label(
            parent_frame,
            text=f"Today's Attendance: {daily_attendance}",
            bg=self.colors['card'],
            fg=self.colors['text'],
            font=('Inter', 16, 'bold')
        ).pack(pady=10)
        
        # Create attendance trends chart
        fig = px.line(
            x=df.index,
            y=[len(day) for day in df.values],
            title="Attendance Trends",
            labels={'x': 'Date', 'y': 'Attendance Count'}
        )
        fig.write_html("attendance_chart.html")
        ttk.Button(
            parent_frame,
            text="View Attendance Trends",
            style='Primary.TButton',
            command=lambda: webbrowser.open('attendance_chart.html')
        ).pack(pady=10)

    def _load_attendance_data(self):
        if os.path.exists("attendance.json"):
            with open("attendance.json", 'r') as f:
                return json.load(f)
        return {}

    def generate_daily_report(self):
        data = self._load_attendance_data()
        today = datetime.now().strftime("%Y-%m-%d")
        
        if today in data:
            report = f"Daily Attendance Report - {today}\n\n"
            for name, time in data[today].items():
                report += f"{name}: {time}\n"
            
            self._save_report(report, f"daily_report_{today}.txt")
            messagebox.showinfo("Success", "Daily report generated successfully!")
        else:
            messagebox.showwarning("No Data", "No attendance records for today.")

    def generate_monthly_report(self):
        data = self._load_attendance_data()
        current_month = datetime.now().strftime("%Y-%m")
        
        monthly_data = {date: records for date, records in data.items() 
                       if date.startswith(current_month)}
        
        if monthly_data:
            report = f"Monthly Attendance Report - {current_month}\n\n"
            for date, records in monthly_data.items():
                report += f"\nDate: {date}\n"
                for name, time in records.items():
                    report += f"{name}: {time}\n"
            
            self._save_report(report, f"monthly_report_{current_month}.txt")
            messagebox.showinfo("Success", "Monthly report generated successfully!")
        else:
            messagebox.showwarning("No Data", "No attendance records for this month.")

    def generate_late_report(self):
        data = self._load_attendance_data()
        today = datetime.now().strftime("%Y-%m-%d")
        
        if today in data:
            late_threshold = timedelta(minutes=15)  # Configurable in settings
            start_time = datetime.strptime("09:00:00", "%H:%M:%S")  # Configurable
            
            report = f"Late Arrivals Report - {today}\n\n"
            late_count = 0
            
            for name, time_str in data[today].items():
                arrival_time = datetime.strptime(time_str, "%H:%M:%S")
                if arrival_time.time() > (start_time + late_threshold).time():
                    report += f"{name}: {time_str} (Late)\n"
                    late_count += 1
            
            if late_count > 0:
                self._save_report(report, f"late_report_{today}.txt")
                messagebox.showinfo("Success", "Late arrivals report generated!")
            else:
                messagebox.showinfo("No Late Arrivals", "No late arrivals today!")
        else:
            messagebox.showwarning("No Data", "No attendance records for today.")

    def export_attendance_data(self):
        data = self._load_attendance_data()
        if data:
            df = pd.DataFrame.from_dict(data, orient='index')
            df.to_csv("attendance_export.csv")
            messagebox.showinfo("Success", "Data exported to attendance_export.csv")
        else:
            messagebox.showwarning("No Data", "No attendance records to export.")

    def _save_report(self, content, filename):
        with open(filename, 'w') as f:
            f.write(content)
   
    
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