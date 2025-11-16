# visualization_menu.py
import os
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import subprocess
import sys

# ---- Шляхи ----
BASE_DIR = os.path.dirname(__file__)
# ! ВИПРАВЛЕННЯ ШЛЯХУ: Тепер 'results' шукається у тій самій директорії, що й BASE_DIR
RESULTS_DIR = os.path.abspath(os.path.join(BASE_DIR, "results"))


VISUALIZATION_TOP = os.path.join(BASE_DIR, "visualization.py")
VISUALIZATION_SIDE = os.path.join(BASE_DIR, "visualization_side.py")


class GraphMenu:
    def __init__(self, root):
        self.root = root
        self.root.title("📊 Меню візуалізацій")
        self.root.geometry("480x520")

        tk.Label(root, text="Результати збережені в:", font=("Arial", 11, "bold")).pack(pady=(10, 0))
        tk.Label(root, text=RESULTS_DIR, fg="gray").pack(pady=(0, 5))

        self.listbox = tk.Listbox(root, width=60, height=15)
        self.listbox.pack(padx=10, pady=10)

        tk.Button(root, text="🔄 Оновити список", command=self.refresh_list).pack(pady=5)
        tk.Button(root, text="🔍 Відкрити вибраний файл", command=self.open_selected).pack(pady=5)

        tk.Label(root, text="Запустити візуалізацію:", font=("Arial", 11, "bold")).pack(pady=(15, 0))
        tk.Button(root, text="📈 Top View (РОЗРАХУНОК)", command=lambda: self.open_script(VISUALIZATION_TOP)).pack(pady=2)
        tk.Button(root, text="🏠 Side View (Демо)", command=lambda: self.open_script(VISUALIZATION_SIDE)).pack(pady=2)

        tk.Button(root, text="❌ Закрити меню", command=self.root.destroy).pack(pady=15)

        self.refresh_list()

    def refresh_list(self):
        """Оновлює список результатів"""
        self.listbox.delete(0, tk.END)
        os.makedirs(RESULTS_DIR, exist_ok=True)
        files = [f for f in os.listdir(RESULTS_DIR) if f.lower().endswith((".png", ".csv", ".txt"))]
        if not files:
            self.listbox.insert(tk.END, "❗ Немає збережених результатів")
        else:
            for f in sorted(files):
                self.listbox.insert(tk.END, f)

    def open_selected(self):
        """Відкрити вибраний файл"""
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showwarning("Увага", "Виберіть файл зі списку.")
            return

        filename = self.listbox.get(selection[0])
        if "❗" in filename:
            return

        path = os.path.join(RESULTS_DIR, filename)
        self.show_file(path)

    def show_file(self, path):
        """Відображає вибраний файл (зображення або текст)"""
        if path.lower().endswith(".png"):
            self.show_image(path)
        elif path.lower().endswith((".csv", ".txt")):
            self.show_text(path)
        else:
            messagebox.showinfo("Файл", f"Тип файлу не підтримується: {path}")

    def show_image(self, path):
        top = tk.Toplevel(self.root)
        top.title(os.path.basename(path))
        try:
            img = Image.open(path)
            img.thumbnail((900, 700))
            photo = ImageTk.PhotoImage(img)
            label = tk.Label(top, image=photo)
            label.image = photo
            label.pack()
            tk.Button(top, text="Закрити", command=top.destroy).pack(pady=10)
        except Exception as e:
            messagebox.showerror("Помилка зображення", f"Не вдалося відкрити зображення:\n{e}")

    def show_text(self, path):
        top = tk.Toplevel(self.root)
        top.title(os.path.basename(path))
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            content = f"Помилка читання файлу: {e}"
            
        text = tk.Text(top, wrap="word", width=100, height=30)
        text.insert("1.0", content)
        text.config(state="disabled")
        text.pack(padx=10, pady=10)
        tk.Button(top, text="Закрити", command=top.destroy).pack(pady=10)

    def open_script(self, script_path):
        """Запускає окремий файл візуалізації"""
        if not os.path.exists(script_path):
            messagebox.showerror("Помилка", f"Не знайдено файл: {script_path}")
            return
        try:
            print(f"Запуск скрипту: {sys.executable} {script_path}")
            # subprocess.Popen запускає скрипт і дозволяє меню працювати далі
            subprocess.Popen([sys.executable, script_path])
        except Exception as e:
            messagebox.showerror("Помилка", f"Не вдалося відкрити {script_path}\n{e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = GraphMenu(root)
    root.mainloop()