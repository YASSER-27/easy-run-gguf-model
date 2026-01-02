import subprocess
import threading
import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
import webbrowser

# إعداد السمة العامة
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class YasserAI_Mini_Engine:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Mini By Yassir")
        self.root.geometry("400x470") # حجم أصغر ومدمج
        self.root.configure(fg_color="#000000")
        
        self.process = None
        self.model_path = ctk.StringVar()
        self.use_gpu = ctk.BooleanVar(value=True) # خيار الـ GPU مفعل افتراضياً

        # --- Header ---
        ctk.CTkLabel(root, text="GGUF MODEL", font=("Inter", 24, "bold"), text_color="#FFFFFF").pack(pady=(25, 5))
        
        # --- Model Card (Compact) ---
        self.card = ctk.CTkFrame(root, fg_color="#0A0A0A", border_width=1, border_color="#1A1A1A", corner_radius=12)
        self.card.pack(pady=10, padx=30, fill="x")
        
        self.lbl_status = ctk.CTkLabel(self.card, text="NO MODEL", font=("Consolas", 10), text_color="#666666")
        self.lbl_status.pack(side="left", padx=15, pady=15)
        
        ctk.CTkButton(self.card, text="LOAD", command=self.add_model, width=60, height=28, 
                      corner_radius=15, fg_color="#FFFFFF", text_color="#000000", font=("Inter", 10, "bold")).pack(side="right", padx=15)

        # --- Engine Settings (CPU/GPU Switch) ---
        self.settings_frame = ctk.CTkFrame(root, fg_color="transparent")
        self.settings_frame.pack(pady=10)

        self.gpu_switch = ctk.CTkSwitch(self.settings_frame, text="USE GPU ACCELERATION", variable=self.use_gpu,
                                        font=("Inter", 10), progress_color="#FFFFFF")
        self.gpu_switch.pack()

        # --- Progress Bar ---
        self.progress = ctk.CTkProgressBar(root, height=2, fg_color="#0A0A0A", progress_color="#FFFFFF")
        self.progress.pack(pady=10, padx=30, fill="x")
        self.progress.set(0)

        # --- Controls ---
        self.btn_start = ctk.CTkButton(root, text="START ENGINE", command=self.start_server,
                                       height=45, corner_radius=10, font=("Inter", 12, "bold"),
                                       fg_color="#FFFFFF", text_color="#000000", hover_color="#CCCCCC")
        self.btn_start.pack(pady=10, padx=30, fill="x")

        self.btn_stop = ctk.CTkButton(root, text="STOP", command=self.stop_server,
                                      height=40, corner_radius=10, font=("Inter", 12, "bold"),
                                      fg_color="#1A1A1A", text_color="#FF4444", border_width=1, 
                                      border_color="#330000", state="disabled")
        self.btn_stop.pack(pady=5, padx=30, fill="x")

        # --- Mini Logs ---
        self.log_area = ctk.CTkTextbox(root, fg_color="#050505", border_width=1, border_color="#1A1A1A",
                                       text_color="#AAAAAA", font=("Consolas", 9), corner_radius=10)
        self.log_area.pack(pady=(15, 25), padx=30, fill="both", expand=True)

    def add_model(self):
        f = filedialog.askopenfilename(filetypes=[("GGUF Files", "*.gguf")])
        if f:
            self.model_path.set(f)
            self.lbl_status.configure(text=os.path.basename(f)[:15]+"...", text_color="#FFFFFF")

    def log(self, msg):
        self.log_area.insert("end", f"> {msg}\n")
        self.log_area.see("end")

    def start_server(self):
        model = self.model_path.get()
        if not model:
            return messagebox.showwarning("System", "Select model first!")

        # تحديد عدد الطبقات بناءً على المفتاح (Switch)
        layers = "20" if self.use_gpu.get() else "0"
        mode_text = "GPU" if self.use_gpu.get() else "CPU"

        exe_path = os.path.join(os.path.dirname(__file__), "llama-server.exe")
        command = [
            exe_path, "-m", model,
            "--host", "0.0.0.0", "--port", "8080",
            "-c", "2048", "--n-gpu-layers", layers
        ]

        def run():
            try:
                self.process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, 
                                                text=True, creationflags=subprocess.CREATE_NO_WINDOW)
                self.root.after(0, lambda: self.btn_start.configure(state="disabled", text=f"RUNNING ON {mode_text}"))
                self.root.after(0, lambda: self.btn_stop.configure(state="normal"))
                self.root.after(0, self.progress.start)
                
                self.root.after(3000, lambda: webbrowser.open("http://localhost:8080"))
                
                for line in self.process.stdout:
                    self.root.after(0, lambda l=line: self.log(l.strip()))
            except Exception as e:
                self.root.after(0, lambda: self.log(f"Error: {e}"))

        self.log(f"Initializing {mode_text} Engine...")
        threading.Thread(target=run, daemon=True).start()

    def stop_server(self):
        if self.process:
            subprocess.call(['taskkill', '/F', '/T', '/PID', str(self.process.pid)])
            self.process = None
            self.btn_start.configure(state="normal", text="START ENGINE")
            self.btn_stop.configure(state="disabled")
            self.progress.stop()
            self.progress.set(0)
            self.log("Server Stopped.")

if __name__ == "__main__":
    app_root = ctk.CTk()
    app = YasserAI_Mini_Engine(app_root)
    app_root.mainloop()