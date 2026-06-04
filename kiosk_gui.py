import tkinter as tk
from tkinter import simpledialog, messagebox
import cv2
import platform
import os
import threading
import time
from PIL import Image, ImageTk
from attendance_engine import AttendanceEngine
import db_manager
from openpyxl import Workbook
from openpyxl.styles import Font

class KioskApp:
    def __init__(self, window):
        self.window = window
        self.window.title("Mega Healthcare Biometrics")
        self.window.geometry("1000x800")
        self.window.configure(bg="#f0f2f5")
        
        self.engine = AttendanceEngine()
        
        # --- STATE VARIABLES ---
        self.camera = None
        self.is_scanning = False
        self.current_mode = None
        
        # Threading Variables
        self.latest_frame = None
        self.ai_running = False
        self.pending_success = None  # NEW: The "Sticky Note" for thread-safe UI updates
        self.pending_error = None

        # --- HEADER ---
        header = tk.Frame(window, bg="#dc2626", height=100)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)
        tk.Label(header, text="MEGA HEALTHCARE.", fg="#fee2e2", bg="#dc2626", font=("Segoe UI", 12)).pack(pady=(15, 0))
        tk.Label(header, text="ATTENDANCE BIOMETRICS", fg="white", bg="#dc2626", font=("Segoe UI", 24, "bold")).pack()

        # --- MAIN CONTAINER ---
        self.main_container = tk.Frame(window, bg="#f0f2f5")
        self.main_container.pack(fill="both", expand=True)

        self.build_menu_view()
        self.build_camera_view()
        self.build_success_view()

        self.return_to_menu()

    # ==========================================
    # VIEW BUILDERS
    # ==========================================
    def build_menu_view(self):
        self.menu_frame = tk.Frame(self.main_container, bg="#f0f2f5")
        
        try:
            raw_logo = Image.open("static/logo.png").convert("RGBA")
            raw_logo = raw_logo.resize((1280, 750), Image.Resampling.LANCZOS)
            raw_logo.putalpha(30) 
            self.bg_img = ImageTk.PhotoImage(raw_logo)
            tk.Label(self.menu_frame, image=self.bg_img, bg="#f0f2f5").place(relx=0.5, rely=0.5, anchor="center")
        except:
            pass 

        btn_container = tk.Frame(self.menu_frame, bg="#f0f2f5")
        btn_container.place(relx=0.5, rely=0.5, anchor="center")

        btn_in = tk.Label(btn_container, text="CHECK IN", bg="#10b981", fg="white", font=("Segoe UI", 20, "bold"), width=12, pady=30, cursor="hand2")
        btn_in.bind("<Button-1>", lambda e: self.start_camera_mode('check_in'))
        btn_in.pack(side="left", padx=20)

        btn_out = tk.Label(btn_container, text="CHECK OUT", bg="#ef4444", fg="white", font=("Segoe UI", 20, "bold"), width=12, pady=30, cursor="hand2")
        btn_out.bind("<Button-1>", lambda e: self.start_camera_mode('check_out'))
        btn_out.pack(side="right", padx=20)

        admin_btn = tk.Label(self.menu_frame, text="Admin Export", fg="#94a3b8", bg="#f0f2f5", font=("Segoe UI", 12, "underline"), cursor="hand2")
        admin_btn.bind("<Button-1>", lambda e: self.export_data())
        admin_btn.place(relx=0.95, rely=0.95, anchor="se")

    def build_camera_view(self):
        self.camera_frame = tk.Frame(self.main_container, bg="#f0f2f5")
        
        self.cam_title = tk.Label(self.camera_frame, text="Scanning... Please face the camera.", fg="#0a192f", bg="#f0f2f5", font=("Segoe UI", 18, "bold"))
        self.cam_title.pack(pady=(30, 10))

        self.cam_status = tk.Label(self.camera_frame, text="", fg="#ef4444", bg="#f0f2f5", font=("Segoe UI", 14))
        self.cam_status.pack(pady=(0, 10))

        vid_border = tk.Frame(self.camera_frame, bg="#dc2626", bd=5)
        vid_border.pack()
        self.vid_label = tk.Label(vid_border, bg="black")
        self.vid_label.pack()

        cancel_btn = tk.Label(self.camera_frame, text="Cancel", bg="#dc2626", fg="white", font=("Segoe UI", 14), padx=30, pady=10, cursor="hand2")
        cancel_btn.bind("<Button-1>", lambda e: self.return_to_menu())
        cancel_btn.pack(pady=30)

    def build_success_view(self):
        self.success_frame = tk.Frame(self.main_container, bg="#f0f2f5")
        
        box = tk.Frame(self.success_frame, bg="white", highlightbackground="#e2e8f0", highlightthickness=2)
        box.place(relx=0.5, rely=0.5, anchor="center")
        
        tk.Label(box, text="Attendance Marked!", fg="#10b981", bg="white", font=("Segoe UI", 28, "bold")).pack(pady=(40, 10), padx=50)
        self.success_name = tk.Label(box, text="Employee Name", fg="#334155", bg="white", font=("Segoe UI", 22))
        self.success_name.pack(pady=5)
        self.success_msg = tk.Label(box, text="Time logged successfully.", fg="#64748b", bg="white", font=("Segoe UI", 14))
        self.success_msg.pack(pady=(0, 30))

        rtn_btn = tk.Label(box, text="Return to Main Screen", bg="#dc2626", fg="white", font=("Segoe UI", 14), padx=30, pady=10, cursor="hand2")
        rtn_btn.bind("<Button-1>", lambda e: self.return_to_menu())
        rtn_btn.pack(pady=(0, 40))

    # ==========================================
    # LOGIC CONTROLLERS
    # ==========================================
    def show_view(self, frame_to_show):
        self.menu_frame.pack_forget()
        self.camera_frame.pack_forget()
        self.success_frame.pack_forget()
        frame_to_show.pack(fill="both", expand=True)
        
        # Force a hard redraw of the entire window for macOS
        self.window.update_idletasks()
        self.window.update()

    def start_camera_mode(self, mode):
        self.current_mode = mode
        self.cam_title.config(text="Checking In..." if mode == 'check_in' else "Checking Out...")
        self.cam_status.config(text="") 
        
        self.pending_success = None
        self.pending_error = None
        self.show_view(self.camera_frame)

        if platform.system() == 'Windows':
            self.camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        else:
            self.camera = cv2.VideoCapture(0, cv2.CAP_AVFOUNDATION)

        self.is_scanning = True
        self.ai_running = True

        self.video_loop()
        threading.Thread(target=self.ai_worker, daemon=True).start()

    def video_loop(self):
        """Runs on the Main Thread. Handles video AND checks for sticky notes from AI."""
        
        # 1. Check if the AI thread left a success note
        if self.pending_success:
            name, msg = self.pending_success
            self.pending_success = None
            self.trigger_success(name, msg)
            return # Exit loop completely!

        # 2. Check if the AI thread left an error note
        if self.pending_error:
            self.cam_status.config(text=self.pending_error)
            self.pending_error = None
            self.window.update_idletasks()

        if not self.is_scanning or self.camera is None:
            return

        # 3. Draw the camera frame smoothly
        ret, frame = self.camera.read()
        if ret:
            self.latest_frame = frame.copy() 

            display_frame = cv2.resize(frame, (640, 480))
            rgb_frame = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(rgb_frame)
            imgtk = ImageTk.PhotoImage(image=img)
            self.vid_label.imgtk = imgtk
            self.vid_label.configure(image=imgtk)

        self.window.after(30, self.video_loop)

    def ai_worker(self):
        """Runs in the Background. Leaves 'sticky notes' for the main thread."""
        while self.ai_running:
            if self.latest_frame is None:
                time.sleep(0.1)
                continue

            _, name, msg = self.engine.process_frame(self.latest_frame, self.current_mode)
            
            if not self.ai_running:
                break

            if name and name.lower() != "unknown":
                # Leave a success sticky note for the Main Thread to find
                self.pending_success = (name, msg)
                self.ai_running = False 
                break
            elif name == "Unknown":
                # Leave an error sticky note
                self.pending_error = "Face not recognized. Keep looking at the camera..."

            time.sleep(0.3)

    def trigger_success(self, name, msg):
        self.is_scanning = False
        self.ai_running = False
        
        if self.camera is not None:
            self.camera.release()
            self.camera = None

        self.success_name.config(text=name)
        self.success_msg.config(text=msg)
        self.show_view(self.success_frame)
        
        self.window.after(4000, self.return_to_menu)

    def return_to_menu(self):
        self.is_scanning = False
        self.ai_running = False
        self.pending_success = None
        
        if self.camera is not None:
            self.camera.release()
            self.camera = None
            
        self.show_view(self.menu_frame)

    def export_data(self):
        pwd = simpledialog.askstring("Admin Required", "Enter Admin Password:", show='*')
        if pwd != "admin":
            if pwd is not None: messagebox.showerror("Error", "Incorrect Password")
            return
        try:
            records = db_manager.get_all_attendance_data()
            wb = Workbook()
            ws = wb.active
            ws.title = "Attendance Log"

            ws.append(["Date", "Employee Name", "Check In", "Check Out"])
            for col in ['A', 'B', 'C', 'D']:
                ws.column_dimensions[col].width = 20
                ws[f'{col}1'].font = Font(bold=True)
                
            for record in records:
                ws.append([record[0], record[1].title(), record[2] or "-", record[3] or "-"])

            desktop_path = os.path.join(os.path.expanduser("~"), "Desktop", "Attendance_Report.xlsx")
            wb.save(desktop_path)
            messagebox.showinfo("Success", f"Report saved successfully to:\n{desktop_path}")
            
        except Exception as e:
            messagebox.showerror("Export Error", str(e))

    def on_closing(self):
        self.is_scanning = False
        self.ai_running = False
        if self.camera is not None:
            self.camera.release()
        self.window.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = KioskApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()