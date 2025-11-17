# visualization_menu.py
import os
import sys
import subprocess
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

# ---- Paths ----
BASE_DIR = os.path.dirname(__file__)
RESULTS_DIR = os.path.abspath(os.path.join(BASE_DIR, "results"))

VISUALIZATION_TOP = os.path.join(BASE_DIR, "visualization.py")
VISUALIZATION_EA = os.path.join(BASE_DIR, "visualization_ea.py")
VISUALIZATION_SIDE = os.path.join(BASE_DIR, "visualization_side.py")


class GraphMenu:
    def __init__(self, master: tk.Tk):
        self.master = master
        master.title("Solar layout – menu")
        master.geometry("800x600")

        # Top frame with buttons
        btn_frame = tk.Frame(master)
        btn_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        self.btn_top = tk.Button(
            btn_frame, text="Top view (classic)",
            command=lambda: self.run_script(VISUALIZATION_TOP)
        )
        self.btn_top.pack(side=tk.LEFT, padx=5)

        self.btn_ea = tk.Button(
            btn_frame, text="Top view (GA / 10 generations)",
            command=lambda: self.run_script(VISUALIZATION_EA)
        )
        self.btn_ea.pack(side=tk.LEFT, padx=5)

        self.btn_side = tk.Button(
            btn_frame, text="Side view",
            command=lambda: self.run_script(VISUALIZATION_SIDE)
        )
        self.btn_side.pack(side=tk.LEFT, padx=5)

        self.btn_refresh = tk.Button(
            btn_frame, text="Refresh preview",
            command=self.refresh_preview
        )
        self.btn_refresh.pack(side=tk.RIGHT, padx=5)

        # Frame for preview
        preview_frame = tk.Frame(master, bd=2, relief=tk.SUNKEN)
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.canvas = tk.Label(preview_frame, text="Latest PNG from results/ will appear here")
        self.canvas.pack(expand=True)

        self.current_image = None   # reference to ImageTk to prevent GC

        # Load something if available
        self.refresh_preview()

    # ---------- helper methods ----------

    def _find_latest_png(self) -> str | None:
        """Find the latest PNG in RESULTS_DIR."""
        if not os.path.isdir(RESULTS_DIR):
            return None
        pngs = [
            os.path.join(RESULTS_DIR, f)
            for f in os.listdir(RESULTS_DIR)
            if f.lower().endswith(".png")
        ]
        if not pngs:
            return None
        pngs.sort(key=os.path.getmtime, reverse=True)
        return pngs[0]

    def refresh_preview(self) -> None:
        png_path = self._find_latest_png()
        if not png_path:
            self.canvas.config(text="No PNG in results/ folder")
            self.current_image = None
            return

        try:
            img = Image.open(png_path)
            # resize to fit window
            img.thumbnail((760, 460))
            imgtk = ImageTk.PhotoImage(img)
            self.canvas.config(image=imgtk, text="")
            self.canvas.image = imgtk  # prevent GC
            self.current_image = imgtk
        except Exception as e:
            self.canvas.config(text=f"Failed to load {png_path}\n{e}")
            self.current_image = None

    def run_script(self, script_path: str) -> None:
        if not os.path.exists(script_path):
            messagebox.showerror("Error", f"File not found: {script_path}")
            return
        try:
            print(f"Running: {sys.executable} {script_path}")
            subprocess.Popen([sys.executable, script_path])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to run {script_path}\n{e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = GraphMenu(root)
    root.mainloop()
