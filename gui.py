"""
Desktop GUI Module for Portable Log Classifier & Analyzer
Built using Python's native Tkinter (no external dependencies required).
"""

import os
import sys
import threading
import webbrowser
import subprocess
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from main import run_pipeline

class LogClassifierApp:
    def __init__(self, root):
        self.root = root
        self.root.title("로그 데이터 분류 및 품질 분석 프로그램 (Portable)")
        self.root.geometry("680x560")
        self.root.minsize(620, 500)

        # Style & Color Palette (Clean Modern Dark Theme)
        self.bg_color = "#1e293b"
        self.fg_color = "#f8fafc"
        self.accent_color = "#38bdf8"
        self.card_bg = "#0f172a"
        
        self.root.configure(bg=self.bg_color)
        
        # State
        self.report_path = ""
        self.output_dir_path = ""
        self.is_running = False

        self._build_ui()

    def _build_ui(self):
        # Header Frame
        header = tk.Frame(self.root, bg="#0b1120", padx=20, pady=16)
        header.pack(fill=tk.X)

        title_lbl = tk.Label(
            header,
            text="📊 로그 데이터 4단계 분류 & 품질 분석기",
            font=("Segoe UI", 16, "bold"),
            bg="#0b1120",
            fg="#ffffff"
        )
        title_lbl.pack(anchor="w")

        subtitle_lbl = tk.Label(
            header,
            text="업체 > Model > Step > Pass/Fail 자동 분류 및 웹 리포트 생성",
            font=("Segoe UI", 10),
            bg="#0b1120",
            fg="#94a3b8"
        )
        subtitle_lbl.pack(anchor="w", pady=(2, 0))

        # Main Body Frame
        body = tk.Frame(self.root, bg=self.bg_color, padx=20, pady=15)
        body.pack(fill=tk.BOTH, expand=True)

        # Paths Frame
        path_box = tk.LabelFrame(
            body,
            text=" 경로 설정 (Path Settings) ",
            font=("Segoe UI", 10, "bold"),
            bg=self.bg_color,
            fg=self.accent_color,
            padx=12,
            pady=10
        )
        path_box.pack(fill=tk.X, pady=(0, 15))

        # Input Path
        tk.Label(path_box, text="입력 로그 폴더 (Data):", bg=self.bg_color, fg=self.fg_color, font=("Segoe UI", 9)).grid(row=0, column=0, sticky="w", pady=4)
        default_data = os.path.abspath("Data") if os.path.exists("Data") else os.getcwd()
        self.data_var = tk.StringVar(value=default_data)
        self.data_entry = tk.Entry(path_box, textvariable=self.data_var, bg=self.card_bg, fg="#fff", insertbackground="#fff", font=("Consolas", 9))
        self.data_entry.grid(row=0, column=1, sticky="ew", padx=8, pady=4)
        tk.Button(path_box, text="폴더 선택...", command=self._browse_data, bg="#334155", fg="#fff", font=("Segoe UI", 9)).grid(row=0, column=2, pady=4)

        # Output Path
        tk.Label(path_box, text="결과 저장 폴더 (Output):", bg=self.bg_color, fg=self.fg_color, font=("Segoe UI", 9)).grid(row=1, column=0, sticky="w", pady=4)
        default_output = os.path.abspath("output")
        self.output_var = tk.StringVar(value=default_output)
        self.output_entry = tk.Entry(path_box, textvariable=self.output_var, bg=self.card_bg, fg="#fff", insertbackground="#fff", font=("Consolas", 9))
        self.output_entry.grid(row=1, column=1, sticky="ew", padx=8, pady=4)
        tk.Button(path_box, text="폴더 선택...", command=self._browse_output, bg="#334155", fg="#fff", font=("Segoe UI", 9)).grid(row=1, column=2, pady=4)

        path_box.columnconfigure(1, weight=1)

        # Action Buttons Frame
        btn_frame = tk.Frame(body, bg=self.bg_color)
        btn_frame.pack(fill=tk.X, pady=(0, 15))

        self.start_btn = tk.Button(
            btn_frame,
            text="🚀 분류 및 분석 시작 (Start)",
            font=("Segoe UI", 11, "bold"),
            bg="#2563eb",
            fg="#ffffff",
            activebackground="#1d4ed8",
            activeforeground="#ffffff",
            padx=16,
            pady=8,
            cursor="hand2",
            relief=tk.FLAT,
            command=self._start_processing
        )
        self.start_btn.pack(side=tk.LEFT)

        self.open_report_btn = tk.Button(
            btn_frame,
            text="🌐 웹 리포트 열기",
            font=("Segoe UI", 10, "bold"),
            bg="#059669",
            fg="#ffffff",
            padx=14,
            pady=8,
            cursor="hand2",
            relief=tk.FLAT,
            state=tk.DISABLED,
            command=self._open_report
        )
        self.open_report_btn.pack(side=tk.LEFT, padx=(10, 0))

        self.open_folder_btn = tk.Button(
            btn_frame,
            text="📁 결과 폴더 열기",
            font=("Segoe UI", 10),
            bg="#334155",
            fg="#ffffff",
            padx=12,
            pady=8,
            cursor="hand2",
            relief=tk.FLAT,
            state=tk.DISABLED,
            command=self._open_folder
        )
        self.open_folder_btn.pack(side=tk.LEFT, padx=(10, 0))

        # Progress Bar & Status
        self.progress_var = tk.DoubleVar(value=0.0)
        self.progress_bar = ttk.Progressbar(body, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X, pady=(0, 5))

        self.status_lbl = tk.Label(
            body,
            text="준비 완료. 시작 버튼을 누르면 분류 및 분석이 진행됩니다.",
            font=("Segoe UI", 9),
            bg=self.bg_color,
            fg="#94a3b8",
            anchor="w"
        )
        self.status_lbl.pack(fill=tk.X, pady=(0, 10))

        # Console / Log View
        log_box = tk.LabelFrame(
            body,
            text=" 실시간 진행 로그 ",
            font=("Segoe UI", 9, "bold"),
            bg=self.bg_color,
            fg="#94a3b8",
            padx=8,
            pady=6
        )
        log_box.pack(fill=tk.BOTH, expand=True)

        self.log_text = tk.Text(
            log_box,
            bg=self.card_bg,
            fg="#e2e8f0",
            insertbackground="#fff",
            font=("Consolas", 9),
            wrap=tk.WORD
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)

    def _browse_data(self):
        chosen = filedialog.askdirectory(initialdir=self.data_var.get(), title="로그 데이터 폴더 선택")
        if chosen:
            self.data_var.set(os.path.normpath(chosen))

    def _browse_output(self):
        chosen = filedialog.askdirectory(initialdir=self.output_var.get(), title="결과 저장 폴더 선택")
        if chosen:
            self.output_var.set(os.path.normpath(chosen))

    def _log(self, msg):
        self.log_text.insert(tk.END, msg + "\n")
        self.log_text.see(tk.END)

    def _start_processing(self):
        if self.is_running:
            return

        data_dir = self.data_var.get().strip()
        output_dir = self.output_var.get().strip()

        if not os.path.exists(data_dir):
            messagebox.showerror("오류", f"데이터 폴더가 존재하지 않습니다:\n{data_dir}")
            return

        self.is_running = True
        self.start_btn.config(state=tk.DISABLED, bg="#475569")
        self.open_report_btn.config(state=tk.DISABLED)
        self.open_folder_btn.config(state=tk.DISABLED)
        self.log_text.delete("1.0", tk.END)
        self.progress_var.set(0)

        # Run background thread
        thread = threading.Thread(target=self._worker_thread, args=(data_dir, output_dir), daemon=True)
        thread.start()

    def _worker_thread(self, data_dir, output_dir):
        def progress_cb(stage, pct, msg):
            self.root.after(0, lambda: self._update_progress(pct, msg))

        try:
            report, html_path = run_pipeline(
                data_dir=data_dir,
                output_dir=output_dir,
                progress_callback=progress_cb,
                open_browser=True
            )
            self.report_path = html_path
            self.output_dir_path = output_dir

            self.root.after(0, self._on_success)
        except Exception as e:
            self.root.after(0, lambda: self._on_failure(str(e)))

    def _update_progress(self, pct, msg):
        self.progress_var.set(pct)
        self.status_lbl.config(text=msg)
        self._log(f"[{pct:3d}%] {msg}")

    def _on_success(self):
        self.is_running = False
        self.start_btn.config(state=tk.NORMAL, bg="#2563eb")
        self.open_report_btn.config(state=tk.NORMAL)
        self.open_folder_btn.config(state=tk.NORMAL)
        self.status_lbl.config(text="🎉 모든 작업이 완료되었습니다! 웹 리포트가 열렸습니다.")
        messagebox.showinfo("완료", "로그 데이터 분류 및 분석이 완료되었습니다!\n결과 웹 리포트가 브라우저에서 열립니다.")

    def _on_failure(self, err_msg):
        self.is_running = False
        self.start_btn.config(state=tk.NORMAL, bg="#2563eb")
        self.status_lbl.config(text=f"오류 발생: {err_msg}")
        self._log(f"[ERROR] {err_msg}")
        messagebox.showerror("처리 실패", f"작업 중 오류가 발생했습니다:\n{err_msg}")

    def _open_report(self):
        if self.report_path and os.path.exists(self.report_path):
            webbrowser.open(f"file:///{os.path.abspath(self.report_path).replace(os.sep, '/')}")
        else:
            messagebox.showwarning("알림", "리포트 파일이 아직 생성되지 않았습니다.")

    def _open_folder(self):
        out_dir = self.output_dir_path or self.output_var.get()
        if os.path.exists(out_dir):
            if sys.platform == "win32":
                os.startfile(out_dir)
            else:
                subprocess.Popen(["xdg-open", out_dir])
        else:
            messagebox.showwarning("알림", "결과 폴더가 아직 생성되지 않았습니다.")


def launch_gui():
    root = tk.Tk()
    app = LogClassifierApp(root)
    root.mainloop()

if __name__ == "__main__":
    launch_gui()
