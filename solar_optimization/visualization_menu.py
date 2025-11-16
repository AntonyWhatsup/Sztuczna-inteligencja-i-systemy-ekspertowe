# visualization_menu.py
import os
import sys
import subprocess
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

# ---- Шляхи ----
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

        # Верхній фрейм з кнопками
        btn_frame = tk.Frame(master)
        btn_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        self.btn_top = tk.Button(
            btn_frame, text="Top view (класичний)",
            command=lambda: self.run_script(VISUALIZATION_TOP)
        )
        self.btn_top.pack(side=tk.LEFT, padx=5)

        self.btn_ea = tk.Button(
            btn_frame, text="Top view (GA / 10 поколінь)",
            command=lambda: self.run_script(VISUALIZATION_EA)
        )
        self.btn_ea.pack(side=tk.LEFT, padx=5)

        self.btn_side = tk.Button(
            btn_frame, text="Side view",
            command=lambda: self.run_script(VISUALIZATION_SIDE)
        )
        self.btn_side.pack(side=tk.LEFT, padx=5)

        self.btn_refresh = tk.Button(
            btn_frame, text="Оновити превʼю",
            command=self.refresh_preview
        )
        self.btn_refresh.pack(side=tk.RIGHT, padx=5)

        # Поле під превʼю
        preview_frame = tk.Frame(master, bd=2, relief=tk.SUNKEN)
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.canvas = tk.Label(preview_frame, text="Тут буде останній PNG із results/")
        self.canvas.pack(expand=True)

        self.current_image = None   # посилання на ImageTk, щоб не збирав GC

        # Завантажити щось, якщо вже є
        self.refresh_preview()

    # ---------- допоміжні методи ----------

    def _find_latest_png(self) -> str | None:
        """Шукає останній PNG у RESULTS_DIR."""
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
            self.canvas.config(text="Немає PNG у папці results/")
            self.current_image = None
            return

        try:
            img = Image.open(png_path)
            # зменшимо, щоб влізло в вікно
            img.thumbnail((760, 460))
            imgtk = ImageTk.PhotoImage(img)
            self.canvas.config(image=imgtk, text="")
            self.canvas.image = imgtk  # щоб не зібрав GC
            self.current_image = imgtk
        except Exception as e:
            self.canvas.config(text=f"Не вдалося завантажити {png_path}\n{e}")
            self.current_image = None

    def run_script(self, script_path: str) -> None:
        if not os.path.exists(script_path):
            messagebox.showerror("Помилка", f"Не знайдено файл: {script_path}")
            return
        try:
            print(f"Запуск: {sys.executable} {script_path}")
            subprocess.Popen([sys.executable, script_path])
        except Exception as e:
            messagebox.showerror("Помилка", f"Не вдалося запустити {script_path}\n{e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = GraphMenu(root)
    root.mainloop()
