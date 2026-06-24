import os
import shutil
import tkinter as tk
from tkinter import messagebox, filedialog, ttk, simpledialog
from tkinterdnd2 import DND_FILES, TkinterDnD
from datetime import datetime
import threading
import time

# ===== НАСТРОЙКИ =====
VIRTUAL_PATH = "C:\\NeoSpace_Pro"
LOG_FILE = os.path.join(VIRTUAL_PATH, "logs.txt")
COLORS = {"bg": "#1a1a2e", "bg_light": "#2a2a4e", "fg": "#ffffff", "accent": "#00ffff"}

class NeoSpacePro:
    def __init__(self, root):
        self.root = root
        self.root.title("NeoSpace Pro — Виртуальная среда")
        self.root.geometry("900x650")
        self.root.minsize(700, 500)
        self.root.configure(bg=COLORS["bg"])

        self.root.drop_target_register(DND_FILES)
        self.root.dnd_bind('<<Drop>>', self.on_drop)

        self.virtual_path = VIRTUAL_PATH
        self._ensure_folders()

        self.current_path = tk.StringVar(value=self.virtual_path)
        self.history = []
        self.forward_history = []
        self.logs = []
        self.search_var = tk.StringVar()
        self.timer_running = False

        self._build_ui()
        self._refresh()
        self._log("🚀 Программа запущена")

    def _ensure_folders(self):
        for folder in [self.virtual_path, os.path.join(self.virtual_path, "Экспорт")]:
            if not os.path.exists(folder):
                os.makedirs(folder)
        if not os.path.exists(LOG_FILE):
            with open(LOG_FILE, 'w', encoding='utf-8') as f:
                f.write("=== ЛОГИ NeoSpace Pro ===\n")

    def _log(self, message):
        timestamp = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.logs.append(log_entry)
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(log_entry + "\n")
        print(log_entry)

    def _build_ui(self):
        top = tk.Frame(self.root, bg=COLORS["bg_light"], height=50)
        top.pack(fill="x", side="top")
        top.pack_propagate(False)
        tk.Label(top, text="🧠 NeoSpace Pro", font=("Cascadia Code", 14, "bold"),
                 fg=COLORS["accent"], bg=COLORS["bg_light"]).pack(side="left", padx=15)
        tk.Label(top, text=f"{self.virtual_path}", font=("Cascadia Code", 10),
                 fg=COLORS["fg"], bg=COLORS["bg_light"]).pack(side="right", padx=15)

        search_frame = tk.Frame(self.root, bg=COLORS["bg"])
        search_frame.pack(fill="x", padx=20, pady=5)

        tk.Label(search_frame, text="🔍 Поиск:", bg=COLORS["bg"], fg=COLORS["fg"],
                 font=("Cascadia Code", 10)).pack(side="left", padx=(0, 5))

        self.search_entry = tk.Entry(search_frame, textvariable=self.search_var,
                                     font=("Cascadia Code", 10), bg=COLORS["bg_light"],
                                     fg=COLORS["fg"], relief="flat", width=30)
        self.search_entry.pack(side="left", padx=(0, 15), fill="x", expand=True)
        self.search_var.trace_add("write", lambda *args: self._refresh())

        btn_frame = tk.Frame(self.root, bg=COLORS["bg"])
        btn_frame.pack(fill="x", padx=20, pady=5)

        buttons = [
            ("📋 Копировать рабочий стол", self._copy_desktop),
            ("📥 Импорт папки", self._import_folder),
            ("📤 Экспорт папки", self._export_folder),
            ("➕ Создать файл", self._create_file),
            ("🗑 Удалить", self._delete_file),
            ("⏱️ Таймер", self._show_timer_settings),
        ]
        for text, cmd in buttons:
            tk.Button(btn_frame, text=text, command=cmd,
                      bg=COLORS["bg_light"], fg=COLORS["fg"],
                      font=("Cascadia Code", 10, "bold"), relief="flat",
                      cursor="hand2").pack(side="left", padx=3, pady=5)

        self.frame = tk.Frame(self.root, bg=COLORS["bg"])
        self.frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.tree = ttk.Treeview(self.frame, columns=("size", "modified"), show="tree headings")
        self.tree.heading("#0", text="Имя")
        self.tree.heading("size", text="Размер")
        self.tree.heading("modified", text="Изменён")
        self.tree.column("#0", width=400)
        self.tree.column("size", width=100)
        self.tree.column("modified", width=150)
        self.tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(self.frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.bind("<Double-1>", self._open_item)

        taskbar = tk.Frame(self.root, bg=COLORS["bg_light"], height=40)
        taskbar.pack(side="bottom", fill="x")
        taskbar.pack_propagate(False)

        self.back_btn = tk.Button(taskbar, text="◀ Назад", command=self._go_back,
                                  bg=COLORS["bg_light"], fg=COLORS["fg"],
                                  font=("Cascadia Code", 10), relief="flat", state="disabled")
        self.back_btn.pack(side="left", padx=(10, 5), pady=5)

        self.forward_btn = tk.Button(taskbar, text="Вперёд ▶", command=self._go_forward,
                                     bg=COLORS["bg_light"], fg=COLORS["fg"],
                                     font=("Cascadia Code", 10), relief="flat", state="disabled")
        self.forward_btn.pack(side="left", padx=(0, 15), pady=5)

        # 🔥 НОВАЯ КНОПКА "ОБНОВИТЬ"
        tk.Button(taskbar, text="🔄 Обновить", command=self._refresh,
                  bg=COLORS["bg_light"], fg=COLORS["accent"],
                  font=("Cascadia Code", 10, "bold"), relief="flat",
                  cursor="hand2").pack(side="left", padx=5, pady=5)

        tk.Button(taskbar, text="📂 Открыть", command=self._open_folder,
                  bg=COLORS["bg_light"], fg=COLORS["fg"],
                  font=("Cascadia Code", 10), relief="flat", cursor="hand2").pack(side="left", padx=5, pady=5)

        self.status = tk.Label(taskbar, text="Готов", bg=COLORS["bg_light"],
                               fg=COLORS["fg"], font=("Cascadia Code", 9))
        self.status.pack(side="right", padx=15, pady=5)

    def _apply_search(self, items):
        query = self.search_var.get().strip().lower()
        if not query:
            return items
        return [item for item in items if query in item.lower()]

    def _refresh(self):
        """Обновляет список файлов в реальном времени."""
        for item in self.tree.get_children():
            self.tree.delete(item)

        path = self.current_path.get()
        if not os.path.exists(path):
            return

        try:
            items = os.listdir(path)
            filtered = self._apply_search(items)

            for name in sorted(filtered):
                full = os.path.join(path, name)
                is_dir = os.path.isdir(full)
                icon = "📁" if is_dir else "📄"
                size = "" if is_dir else self._format_size(os.path.getsize(full))
                modified = datetime.fromtimestamp(os.path.getmtime(full)).strftime("%d.%m.%Y %H:%M")
                self.tree.insert("", "end", text=f"{icon} {name}", values=(size, modified))

            self.status.config(text=f"📁 {path} | Элементов: {len(filtered)}")
        except Exception as e:
            self.status.config(text=f"Ошибка: {e}")

    def on_drop(self, event):
        path = self.current_path.get()
        if not os.path.exists(path):
            return

        files = event.data.split()
        if not files:
            return

        if not messagebox.askyesno("Подтверждение", f"Скопировать {len(files)} элементов в виртуальную папку?"):
            return

        for f in files:
            f = f.strip('{}')
            if os.path.exists(f):
                try:
                    dest = os.path.join(path, os.path.basename(f))
                    if os.path.isdir(f):
                        shutil.copytree(f, dest, dirs_exist_ok=True)
                    else:
                        shutil.copy2(f, dest)
                except Exception as e:
                    self._log(f"⚠️ Ошибка копирования: {e}")
        self._log(f"📥 Перетащено {len(files)} файлов")
        self._refresh()

    def _copy_desktop(self):
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        if not os.path.exists(desktop):
            return

        target = os.path.join(self.virtual_path, "Рабочий стол")
        if os.path.exists(target) and not messagebox.askyesno("Подтверждение", "Заменить папку 'Рабочий стол'?"):
            return

        try:
            if os.path.exists(target):
                shutil.rmtree(target)
            shutil.copytree(desktop, target, ignore_errors=True)
            self._log("📋 Рабочий стол скопирован")
            self._refresh()
            messagebox.showinfo("Успех", "Рабочий стол скопирован в виртуальную папку!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка: {e}")

    def _import_folder(self):
        src = filedialog.askdirectory(title="Выберите папку для импорта")
        if not src:
            return

        dest = os.path.join(self.current_path.get(), os.path.basename(src))
        if os.path.exists(dest) and not messagebox.askyesno("Подтверждение", "Папка уже существует. Заменить?"):
            return

        try:
            shutil.copytree(src, dest, dirs_exist_ok=True)
            self._log(f"📥 Импортирована папка: {src}")
            self._refresh()
            messagebox.showinfo("Успех", "Папка импортирована!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка: {e}")

    def _export_folder(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите папку для экспорта!")
            return

        item = self.tree.item(selected[0])
        name = item["text"].split(" ", 1)[1]
        src = os.path.join(self.current_path.get(), name)

        if not os.path.isdir(src):
            messagebox.showwarning("Ошибка", "Выберите папку, а не файл!")
            return

        dest = filedialog.askdirectory(title="Куда экспортировать папку?")
        if not dest:
            return

        try:
            shutil.copytree(src, os.path.join(dest, name), dirs_exist_ok=True)
            self._log(f"📤 Экспортирована папка: {src} → {dest}")
            messagebox.showinfo("Успех", f"Папка экспортирована в:\n{dest}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка: {e}")

    def _create_file(self):
        name = simpledialog.askstring("Создать файл", "Введите имя файла (без расширения):")
        if not name:
            return
        if not name.endswith('.txt'):
            name += '.txt'

        path = os.path.join(self.current_path.get(), name)
        if os.path.exists(path):
            messagebox.showwarning("Ошибка", "Файл уже существует!")
            return

        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(f"Создано в NeoSpace Pro: {datetime.now().strftime('%d.%m.%Y %H:%M')}")
            self._log(f"➕ Создан файл: {name}")
            self._refresh()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка: {e}")

    def _delete_file(self):
        selected = self.tree.selection()
        if not selected:
            return

        item = self.tree.item(selected[0])
        name = item["text"].split(" ", 1)[1]
        path = os.path.join(self.current_path.get(), name)

        if messagebox.askyesno("Подтверждение", f"Удалить {name}?"):
            try:
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)
                self._log(f"🗑 Удалён: {name}")
                self._refresh()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка: {e}")

    def _show_timer_settings(self):
        timer_window = tk.Toplevel(self.root)
        timer_window.title("⏱️ Таймер NeoSpace Pro")
        timer_window.geometry("350x250")
        timer_window.configure(bg=COLORS["bg"])
        timer_window.resizable(False, False)

        tk.Label(timer_window, text="⏱️ Таймер", font=("Cascadia Code", 14, "bold"),
                 fg=COLORS["accent"], bg=COLORS["bg"]).pack(pady=10)

        tk.Label(timer_window, text="Интервал (секунды):", bg=COLORS["bg"],
                 fg=COLORS["fg"], font=("Cascadia Code", 10)).pack(pady=5)
        interval_entry = tk.Entry(timer_window, font=("Cascadia Code", 10),
                                  bg=COLORS["bg_light"], fg=COLORS["fg"])
        interval_entry.insert(0, "60")
        interval_entry.pack(pady=5)

        tk.Label(timer_window, text="Действие:", bg=COLORS["bg"],
                 fg=COLORS["fg"], font=("Cascadia Code", 10)).pack(pady=5)

        action_var = tk.StringVar(value="backup")
        tk.Radiobutton(timer_window, text="📦 Бэкап папки", variable=action_var,
                       value="backup", bg=COLORS["bg"], fg=COLORS["fg"],
                       selectcolor=COLORS["bg"]).pack()
        tk.Radiobutton(timer_window, text="🧹 Очистка папки", variable=action_var,
                       value="clean", bg=COLORS["bg"], fg=COLORS["fg"],
                       selectcolor=COLORS["bg"]).pack()

        def start_timer():
            try:
                interval = int(interval_entry.get())
                if interval < 1:
                    raise ValueError
                self.timer_running = True
                timer_window.destroy()
                threading.Thread(target=self._timer_loop, args=(interval, action_var.get()), daemon=True).start()
                messagebox.showinfo("Таймер", f"Таймер запущен! Интервал: {interval} сек.")
            except ValueError:
                messagebox.showerror("Ошибка", "Введите корректное число секунд!")

        tk.Button(timer_window, text="▶️ Запустить", command=start_timer,
                  bg="#4caf50", fg="#ffffff", font=("Cascadia Code", 10, "bold"),
                  relief="flat", cursor="hand2").pack(pady=10)

        tk.Button(timer_window, text="⏹️ Остановить", command=self._stop_timer,
                  bg="#f44336", fg="#ffffff", font=("Cascadia Code", 10, "bold"),
                  relief="flat", cursor="hand2").pack(pady=5)

    def _stop_timer(self):
        self.timer_running = False
        messagebox.showinfo("Таймер", "Таймер остановлен!")

    def _timer_loop(self, interval, action):
        while self.timer_running:
            time.sleep(interval)
            if action == "backup":
                self._auto_backup()
            elif action == "clean":
                self._auto_clean()

    def _auto_backup(self):
        backup_path = os.path.join(self.virtual_path, "Экспорт", f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        try:
            shutil.copytree(self.virtual_path, backup_path, ignore=shutil.ignore_patterns("Экспорт", "logs.txt"))
            self._log(f"📦 Автобэкап создан: {backup_path}")
        except Exception as e:
            self._log(f"⚠️ Ошибка автобэкапа: {e}")

    def _auto_clean(self):
        try:
            for item in os.listdir(self.virtual_path):
                if item not in ["Экспорт", "logs.txt"]:
                    path = os.path.join(self.virtual_path, item)
                    if os.path.isdir(path):
                        shutil.rmtree(path)
                    else:
                        os.remove(path)
            self._log("🧹 Автоочистка выполнена")
            self.root.after(0, self._refresh)
        except Exception as e:
            self._log(f"⚠️ Ошибка автоочистки: {e}")

    def _go_back(self):
        if self.history:
            self.forward_history.append(self.current_path.get())
            self.current_path.set(self.history.pop())
            self._update_buttons()
            self._refresh()

    def _go_forward(self):
        if self.forward_history:
            self.history.append(self.current_path.get())
            self.current_path.set(self.forward_history.pop())
            self._update_buttons()
            self._refresh()

    def _update_buttons(self):
        self.back_btn.config(state="normal" if self.history else "disabled")
        self.forward_btn.config(state="normal" if self.forward_history else "disabled")

    def _open_item(self, event):
        selected = self.tree.selection()
        if not selected:
            return

        item = self.tree.item(selected[0])
        name = item["text"].split(" ", 1)[1]
        path = os.path.join(self.current_path.get(), name)

        if os.path.isdir(path):
            self.history.append(self.current_path.get())
            self.forward_history.clear()
            self.current_path.set(path)
            self._update_buttons()
            self._refresh()
        else:
            try:
                os.startfile(path)
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось открыть:\n{e}")

    def _open_folder(self):
        path = self.current_path.get()
        if os.path.exists(path):
            os.startfile(path)
            self._log(f"📂 Открыта папка: {path}")

    def _format_size(self, size):
        for unit in ['Б', 'КБ', 'МБ', 'ГБ']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} ТБ"

if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = NeoSpacePro(root)
    root.mainloop()