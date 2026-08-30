import os
import sys
import time
import subprocess
import threading
import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
import json

# Ensure requests is available, otherwise fail gracefully
try:
    import requests
except ImportError:
    requests = None

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

class CodeGateLauncher(tk.Tk):
    def __init__(self, auto_start=False):
        super().__init__()
        self.title("CodeGate")
        self.geometry("380x350")
        self.resizable(False, False)
        
        # Paths
        self.runtime_dir = os.path.join(PROJECT_ROOT, ".runtime")
        self.logs_dir = os.path.join(self.runtime_dir, "logs")
        self.backend_pid_file = os.path.join(self.runtime_dir, "backend.pid")
        self.frontend_pid_file = os.path.join(self.runtime_dir, "frontend.pid")
        self.backend_log_file = os.path.join(self.logs_dir, "backend.log")
        self.frontend_log_file = os.path.join(self.logs_dir, "frontend.log")
        self.launcher_log_file = os.path.join(self.logs_dir, "launcher.log")
        
        self.python_exe = os.path.join(PROJECT_ROOT, ".venv", "Scripts", "python.exe")
        self.dashboard_dir = os.path.join(PROJECT_ROOT, "dashboard")
        
        self._setup_directories()
        
        # Process handles
        self.backend_proc = None
        self.frontend_proc = None
        
        # State
        self.backend_status = "UNKNOWN"
        self.frontend_status = "UNKNOWN"
        self.backend_ready = False
        self.frontend_ready = False
        self.auto_opened = False
        
        self._build_ui()
        self._check_initial_state()
        
        if auto_start:
            self.after(500, self.start_codegate)
            
        self.after(3000, self._poll_health) # Poll every 3 seconds

    def _setup_directories(self):
        os.makedirs(self.logs_dir, exist_ok=True)
        
    def _log(self, message):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{timestamp}] {message}\n"
        try:
            with open(self.launcher_log_file, "a", encoding="utf-8") as f:
                f.write(line)
        except Exception:
            pass

    def _build_ui(self):
        main_frame = ttk.Frame(self, padding="15 15 15 15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        ttk.Label(main_frame, text="CodeGate System Status", font=("Helvetica", 14, "bold")).pack(pady=(0, 15))
        
        # Status Frame
        status_frame = ttk.LabelFrame(main_frame, text="Services", padding="10 10 10 10")
        status_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.lbl_backend = ttk.Label(status_frame, text="Backend: STOPPED")
        self.lbl_backend.pack(anchor="w")
        
        self.lbl_frontend = ttk.Label(status_frame, text="Frontend: STOPPED")
        self.lbl_frontend.pack(anchor="w")
        
        self.lbl_db = ttk.Label(status_frame, text="Database: UNKNOWN")
        self.lbl_db.pack(anchor="w")
        
        self.lbl_github = ttk.Label(status_frame, text="GitHub: UNKNOWN")
        self.lbl_github.pack(anchor="w")
        
        self.lbl_ai = ttk.Label(status_frame, text="AI: UNKNOWN")
        self.lbl_ai.pack(anchor="w")
        
        self.lbl_webhook = ttk.Label(status_frame, text="Webhook: NOT CONFIGURED")
        self.lbl_webhook.pack(anchor="w")
        
        # Buttons Frame
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X)
        
        self.btn_start = ttk.Button(btn_frame, text="START CODEGATE", command=self.start_codegate)
        self.btn_start.pack(fill=tk.X, pady=3)
        
        self.btn_stop = ttk.Button(btn_frame, text="STOP CODEGATE", command=self.stop_codegate)
        self.btn_stop.pack(fill=tk.X, pady=3)
        
        self.btn_open = ttk.Button(btn_frame, text="OPEN DASHBOARD", command=self.open_dashboard)
        self.btn_open.pack(fill=tk.X, pady=3)
        
        self.btn_logs = ttk.Button(btn_frame, text="VIEW LOGS", command=self.view_logs)
        self.btn_logs.pack(fill=tk.X, pady=3)
        
    def _update_ui_state(self):
        self.lbl_backend.config(text=f"Backend: {self.backend_status}")
        self.lbl_frontend.config(text=f"Frontend: {self.frontend_status}")
        
        if self.backend_status in ["STARTING", "READY"] or self.frontend_status in ["STARTING", "READY"]:
            self.btn_start.state(['disabled'])
            self.btn_stop.state(['!disabled'])
        else:
            self.btn_start.state(['!disabled'])
            self.btn_stop.state(['disabled'])
            
        if self.frontend_ready:
            self.btn_open.state(['!disabled'])
        else:
            self.btn_open.state(['disabled'])
            
    def _check_initial_state(self):
        self._log("Checking initial state...")
        
        b_healthy = self._check_backend_health()
        f_healthy = self._check_frontend_health()
        
        if b_healthy:
            self.backend_status = "READY"
            self.backend_ready = True
        else:
            self.backend_status = "STOPPED"
            self.backend_ready = False
            
        if f_healthy:
            self.frontend_status = "READY"
            self.frontend_ready = True
        else:
            self.frontend_status = "STOPPED"
            self.frontend_ready = False
            
        self._update_ui_state()
        
    def _check_backend_health(self):
        if not requests: return False
        try:
            r = requests.get("http://127.0.0.1:8000/api/v1/system/status", timeout=2)
            if r.status_code == 200:
                data = r.json()
                self._update_system_labels(data)
                return True
        except Exception:
            pass
        return False
        
    def _check_frontend_health(self):
        if not requests: return False
        try:
            r = requests.get("http://127.0.0.1:5173", timeout=2)
            return r.status_code == 200
        except Exception:
            pass
        return False
        
    def _update_system_labels(self, data):
        db = data.get("database", {}).get("status", "UNKNOWN")
        gh = data.get("github", {}).get("status", "UNKNOWN")
        ai = data.get("ai", {}).get("status", "UNKNOWN")
        
        self.lbl_db.config(text=f"Database: {db}")
        self.lbl_github.config(text=f"GitHub: {gh}")
        self.lbl_ai.config(text=f"AI: {ai}")
        
    def _poll_health(self):
        if self.backend_status == "READY":
            if not self._check_backend_health():
                self.backend_status = "ERROR"
                self.backend_ready = False
        
        if self.frontend_status == "READY":
            if not self._check_frontend_health():
                self.frontend_status = "ERROR"
                self.frontend_ready = False
                
        self._update_ui_state()
        self.after(3000, self._poll_health)
        
    def _get_npm_cmd(self):
        try:
            res = subprocess.run(["where", "npm.cmd"], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            if res.returncode == 0:
                return res.stdout.strip().split('\n')[0]
        except Exception:
            pass
        return "npm.cmd"

    def start_codegate(self):
        if requests is None:
            messagebox.showerror("Error", "Requests library not found. Launch environment is broken.")
            return

        if not os.path.exists(self.python_exe):
            messagebox.showerror("Error", f"Python not found:\n{self.python_exe}")
            return
            
        if not os.path.exists(os.path.join(self.dashboard_dir, "package.json")):
            messagebox.showerror("Error", f"Dashboard not found:\n{self.dashboard_dir}")
            return
            
        self.auto_opened = False
        threading.Thread(target=self._startup_sequence, daemon=True).start()
        
    def _startup_sequence(self):
        self._log("Starting CodeGate...")
        
        # Backend
        if not self._check_backend_health():
            self.backend_status = "STARTING"
            self.after(0, self._update_ui_state)
            
            try:
                env = os.environ.copy()
                self.backend_proc = subprocess.Popen(
                    [self.python_exe, "-m", "uvicorn", "codegate.api.main:app", "--host", "127.0.0.1", "--port", "8000"],
                    cwd=PROJECT_ROOT,
                    env=env,
                    stdout=open(self.backend_log_file, "w"),
                    stderr=subprocess.STDOUT,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                with open(self.backend_pid_file, "w") as f:
                    f.write(str(self.backend_proc.pid))
                    
                # Wait for backend
                ready = False
                for _ in range(15):
                    time.sleep(2)
                    if self._check_backend_health():
                        ready = True
                        break
                    if self.backend_proc.poll() is not None:
                        break
                        
                if not ready:
                    self.backend_status = "ERROR"
                    self._log("Backend failed to start.")
                    self.after(0, self._update_ui_state)
                    self.after(0, lambda: messagebox.showerror("Backend Error", "Backend failed to start.\nCheck .runtime/logs/backend.log"))
                    return
            except Exception as e:
                self.backend_status = "ERROR"
                self._log(f"Backend spawn error: {e}")
                self.after(0, self._update_ui_state)
                return
                
        self.backend_status = "READY"
        self.backend_ready = True
        self.after(0, self._update_ui_state)
        
        # Frontend
        if not self._check_frontend_health():
            self.frontend_status = "STARTING"
            self.after(0, self._update_ui_state)
            
            try:
                npm_exe = self._get_npm_cmd()
                
                # Check node_modules
                if not os.path.exists(os.path.join(self.dashboard_dir, "node_modules")):
                    self._log("Installing frontend dependencies...")
                    subprocess.run([npm_exe, "install"], cwd=self.dashboard_dir, creationflags=subprocess.CREATE_NO_WINDOW)
                
                self.frontend_proc = subprocess.Popen(
                    [npm_exe, "run", "dev", "--", "--host", "127.0.0.1", "--port", "5173", "--strictPort"],
                    cwd=self.dashboard_dir,
                    stdout=open(self.frontend_log_file, "w"),
                    stderr=subprocess.STDOUT,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                with open(self.frontend_pid_file, "w") as f:
                    f.write(str(self.frontend_proc.pid))
                    
                # Wait for frontend
                ready = False
                for _ in range(15):
                    time.sleep(2)
                    if self._check_frontend_health():
                        ready = True
                        break
                    if self.frontend_proc.poll() is not None:
                        break
                        
                if not ready:
                    self.frontend_status = "ERROR"
                    self._log("Frontend failed to start.")
                    self.after(0, self._update_ui_state)
                    self.after(0, lambda: messagebox.showerror("Frontend Error", "Frontend failed to start.\nCheck .runtime/logs/frontend.log"))
                    return
            except Exception as e:
                self.frontend_status = "ERROR"
                self._log(f"Frontend spawn error: {e}")
                self.after(0, self._update_ui_state)
                return
                
        self.frontend_status = "READY"
        self.frontend_ready = True
        self.after(0, self._update_ui_state)
        
        if not self.auto_opened:
            self.auto_opened = True
            self.after(0, self.open_dashboard)
            
    def _kill_pid(self, pid_file):
        if os.path.exists(pid_file):
            try:
                with open(pid_file, "r") as f:
                    pid = int(f.read().strip())
                # taskkill /F /T /PID forces process tree kill
                subprocess.run(["taskkill", "/F", "/T", "/PID", str(pid)], creationflags=subprocess.CREATE_NO_WINDOW, capture_output=True)
                os.remove(pid_file)
            except Exception:
                pass

    def stop_codegate(self):
        self._log("Stopping CodeGate...")
        
        if self.backend_proc:
            self._kill_pid(self.backend_pid_file)
            self.backend_proc = None
            
        if self.frontend_proc:
            self._kill_pid(self.frontend_pid_file)
            self.frontend_proc = None
            
        # Fallback cleanup for PIDs even if not spawned by this GUI instance
        self._kill_pid(self.backend_pid_file)
        self._kill_pid(self.frontend_pid_file)
        self._kill_pid(os.path.join(self.runtime_dir, "smee.pid"))
        
        self.backend_status = "STOPPED"
        self.frontend_status = "STOPPED"
        self.backend_ready = False
        self.frontend_ready = False
        
        self.lbl_db.config(text="Database: UNKNOWN")
        self.lbl_github.config(text="GitHub: UNKNOWN")
        self.lbl_ai.config(text="AI: UNKNOWN")
        
        self._update_ui_state()

    def open_dashboard(self):
        if self.frontend_ready:
            webbrowser.open("http://127.0.0.1:5173/dashboard")
            
    def view_logs(self):
        os.startfile(self.logs_dir)

if __name__ == "__main__":
    auto = "--start" in sys.argv
    app = CodeGateLauncher(auto_start=auto)
    app.mainloop()
