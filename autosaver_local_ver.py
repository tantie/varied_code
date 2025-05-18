"""
Простое поддерживание локальной версионности проекта с отслеживание изменений файлов с сохранением версий (macOS)

Описание:
    Выбрать папку, следить за изменениями файлов в ней
    и автоматически сохранять до N предыдущих версий каждого изменённого файла.

    Все сохранённые версии хранятся в скрытой подпапке `.versions`.

    Интерфейс позволяет:
    - выбрать папку для отслеживания;
    - просматривать сохранённые версии файлов;
    - откатываться к любой версии двойным кликом.

Запуск:
    python3 autosaver_gui.py

Сборка в .app:
    1. Установите py2app:
        pip3 install py2app
    2. Создайте рядом файл
    
        from setuptools import setup
        
        APP = ['autosaver_gui.py']
        OPTIONS = {'argv_emulation': True}
        
        setup(
            app=APP,
            options={'py2app': OPTIONS},
            setup_requires=['py2app'],
        )

    3.  Приложение:
        python3 setup.py py2app
"""



import os
import shutil
import hashlib
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# Конфигурация
MAX_VERSIONS = 50 # количество версий
CHECK_INTERVAL_MS = 2000  # каждые 2 секунды

class AutoSaverApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AutoSaver")
        self.folder = ""
        self.file_hashes = {}

        self.setup_ui()

    def setup_ui(self):
        self.label = tk.Label(self.root, text="Выбери папку для отслеживания")
        self.label.pack(pady=10)

        self.select_button = tk.Button(self.root, text="Выбрать папку", command=self.select_folder)
        self.select_button.pack(pady=5)

        self.tree = ttk.Treeview(self.root, columns=("versions"), show="headings")
        self.tree.heading("versions", text="Старые версии файлов")
        self.tree.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        self.tree.bind("<Double-1>", self.restore_version)

    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder = folder
            self.versions_folder = os.path.join(self.folder, ".versions")
            os.makedirs(self.versions_folder, exist_ok=True)
            self.label.config(text=f"Следим за: {self.folder}")
            self.root.after(CHECK_INTERVAL_MS, self.check_changes)
            self.populate_versions()

    def get_hash(self, filepath):
        try:
            with open(filepath, "rb") as f:
                return hashlib.md5(f.read()).hexdigest()
        except:
            return None

    def save_version(self, filepath):
        rel_path = os.path.relpath(filepath, self.folder)
        filename = os.path.basename(rel_path)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        version_path = os.path.join(self.versions_folder, f"{filename}__{timestamp}")
        shutil.copy2(filepath, version_path)

        # Очистка старых версий
        versions = sorted([f for f in os.listdir(self.versions_folder) if f.startswith(filename + "__")])
        while len(versions) > MAX_VERSIONS:
            os.remove(os.path.join(self.versions_folder, versions.pop(0)))

    def check_changes(self):
        if not self.folder:
            return

        for root, _, files in os.walk(self.folder):
            if ".versions" in root:
                continue
            for file in files:
                filepath = os.path.join(root, file)
                h = self.get_hash(filepath)
                if h and self.file_hashes.get(filepath) != h:
                    self.file_hashes[filepath] = h
                    self.save_version(filepath)
                    self.populate_versions()
        self.root.after(CHECK_INTERVAL_MS, self.check_changes)

    def populate_versions(self):
        if not hasattr(self, "versions_folder"):
            return
        self.tree.delete(*self.tree.get_children())
        for file in sorted(os.listdir(self.versions_folder), reverse=True):
            self.tree.insert("", tk.END, values=(file,))

    def restore_version(self, event):
        item = self.tree.selection()[0]
        filename = self.tree.item(item, "values")[0]
        original = filename.split("__")[0]
        source = os.path.join(self.versions_folder, filename)
        dest = os.path.join(self.folder, original)
        if messagebox.askyesno("Откат", f"Заменить {original} на выбранную версию?"):
            shutil.copy2(source, dest)
            messagebox.showinfo("Готово", f"Файл {original} восстановлен.")

# Запуск GUI
if __name__ == "__main__":
    root = tk.Tk()
    app = AutoSaverApp(root)
    root.geometry("500x400")
    root.mainloop()
