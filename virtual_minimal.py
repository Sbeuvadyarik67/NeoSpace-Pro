import os
import sys
import json
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import shutil
import time
import subprocess
import threading

# ПЫТАЕМСЯ ИМПОРТИРОВАТЬ tkinterweb (если установлен)
try:
    from tkinterweb import HtmlFrame
    TKINTERWEB_AVAILABLE = True
except ImportError:
    TKINTERWEB_AVAILABLE = False

# ===================================================
# ЗАГРУЗКА НАСТРОЕК
# ===================================================
def load_settings():
    try:
        with open("neospace_settings.json", 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {"os": "windows", "hz": 60, "browser_mode": "internal", "theme": "neon"}

SETTINGS = load_settings()
OS_TYPE = SETTINGS.get("os", "windows")
HZ = SETTINGS.get("hz", 60)
BROWSER_MODE = SETTINGS.get("browser_mode", "internal")
THEME = SETTINGS.get("theme", "neon")

VIRTUAL_PATH = os.path.join(os.path.dirname(__file__), "NeoSpace_Data")
os.makedirs(VIRTUAL_PATH, exist_ok=True)

# ===================================================
# ТЕМЫ ОФОРМЛЕНИЯ
# ===================================================
def get_theme_colors(theme_name):
    """Возвращает цвета для выбранной темы"""
    
    themes = {
        # ===== СЕРЬЁЗНЫЕ ТЕМЫ =====
        "classic": {
            "bg": "#0f172a",
            "bg_light": "#1e293b",
            "fg": "#f1f5f9",
            "fg_secondary": "#94a3b8",
            "accent": "#60a5fa",
            "taskbar": "#0f172a",
            "taskbar_hover": "#1e293b",
            "button_close": "#ef4444",
            "button_min": "#f59e0b",
            "button_max": "#22c55e",
            "window_bg": "#0f172a",
            "window_fg": "#f1f5f9",
            "resize_color": "#1e293b",
            "entry_bg": "#1e293b",
            "entry_fg": "#f1f5f9",
            "category": "serious"
        },
        "corporate": {
            "bg": "#1a1a1a",
            "bg_light": "#2d2d2d",
            "fg": "#e8e8e8",
            "fg_secondary": "#aaaaaa",
            "accent": "#4a90d9",
            "taskbar": "#1a1a1a",
            "taskbar_hover": "#2d2d2d",
            "button_close": "#e74c3c",
            "button_min": "#f39c12",
            "button_max": "#2ecc71",
            "window_bg": "#1a1a1a",
            "window_fg": "#e8e8e8",
            "resize_color": "#2d2d2d",
            "entry_bg": "#2d2d2d",
            "entry_fg": "#e8e8e8",
            "category": "serious"
        },
        "minimal": {
            "bg": "#1a1a1a",
            "bg_light": "#2a2a2a",
            "fg": "#f0f0f0",
            "fg_secondary": "#aaaaaa",
            "accent": "#888888",
            "taskbar": "#1a1a1a",
            "taskbar_hover": "#2a2a2a",
            "button_close": "#888888",
            "button_min": "#888888",
            "button_max": "#888888",
            "window_bg": "#1a1a1a",
            "window_fg": "#f0f0f0",
            "resize_color": "#2a2a2a",
            "entry_bg": "#2a2a2a",
            "entry_fg": "#f0f0f0",
            "category": "serious"
        },
        "office": {
            "bg": "#f0f0f0",
            "bg_light": "#e0e0e0",
            "fg": "#1a1a1a",
            "fg_secondary": "#555555",
            "accent": "#2b5797",
            "taskbar": "#e8e8e8",
            "taskbar_hover": "#d0d0d0",
            "button_close": "#e74c3c",
            "button_min": "#f39c12",
            "button_max": "#2ecc71",
            "window_bg": "#f0f0f0",
            "window_fg": "#1a1a1a",
            "resize_color": "#d0d0d0",
            "entry_bg": "#ffffff",
            "entry_fg": "#1a1a1a",
            "category": "serious"
        },
        "dark_pro": {
            "bg": "#0a0a0f",
            "bg_light": "#16161f",
            "fg": "#d4d4e0",
            "fg_secondary": "#8888aa",
            "accent": "#818cf8",
            "taskbar": "#0a0a0f",
            "taskbar_hover": "#16161f",
            "button_close": "#ff4757",
            "button_min": "#ffa502",
            "button_max": "#2ed573",
            "window_bg": "#0a0a0f",
            "window_fg": "#d4d4e0",
            "resize_color": "#16161f",
            "entry_bg": "#16161f",
            "entry_fg": "#d4d4e0",
            "category": "serious"
        },
        
        # ===== КРАСИВЫЕ ТЕМЫ =====
        "neon": {
            "bg": "#0a0e1a",
            "bg_light": "#161f3a",
            "fg": "#e0f0ff",
            "fg_secondary": "#88bbdd",
            "accent": "#00d4ff",
            "taskbar": "#0a0e1a",
            "taskbar_hover": "#161f3a",
            "button_close": "#ff6b6b",
            "button_min": "#ffbd2e",
            "button_max": "#28c840",
            "window_bg": "#0a0e1a",
            "window_fg": "#e0f0ff",
            "resize_color": "#161f3a",
            "entry_bg": "#161f3a",
            "entry_fg": "#e0f0ff",
            "category": "beautiful"
        },
        "cyber": {
            "bg": "#0d0a1a",
            "bg_light": "#1a0a2e",
            "fg": "#f0ccff",
            "fg_secondary": "#cc88ff",
            "accent": "#ff44ff",
            "taskbar": "#0d0a1a",
            "taskbar_hover": "#1a0a2e",
            "button_close": "#ff3366",
            "button_min": "#ffcc00",
            "button_max": "#00ffcc",
            "window_bg": "#0d0a1a",
            "window_fg": "#f0ccff",
            "resize_color": "#1a0a2e",
            "entry_bg": "#1a0a2e",
            "entry_fg": "#f0ccff",
            "category": "beautiful"
        },
        "matrix": {
            "bg": "#0a0f0a",
            "bg_light": "#0f1f0f",
            "fg": "#88ff88",
            "fg_secondary": "#44dd44",
            "accent": "#44ff44",
            "taskbar": "#0a0f0a",
            "taskbar_hover": "#0f1f0f",
            "button_close": "#ff3333",
            "button_min": "#ffff33",
            "button_max": "#33ff33",
            "window_bg": "#0a0f0a",
            "window_fg": "#88ff88",
            "resize_color": "#0f1f0f",
            "entry_bg": "#0f1f0f",
            "entry_fg": "#88ff88",
            "category": "beautiful"
        },
        "ocean": {
            "bg": "#0a1a2a",
            "bg_light": "#0f2a3f",
            "fg": "#bbeeff",
            "fg_secondary": "#66bbdd",
            "accent": "#44ccff",
            "taskbar": "#0a1a2a",
            "taskbar_hover": "#0f2a3f",
            "button_close": "#ff6b6b",
            "button_min": "#ffbd2e",
            "button_max": "#28c840",
            "window_bg": "#0a1a2a",
            "window_fg": "#bbeeff",
            "resize_color": "#0f2a3f",
            "entry_bg": "#0f2a3f",
            "entry_fg": "#bbeeff",
            "category": "beautiful"
        },
        "sunset": {
            "bg": "#1a0a0a",
            "bg_light": "#2a1515",
            "fg": "#ffccaa",
            "fg_secondary": "#ff9966",
            "accent": "#ff7744",
            "taskbar": "#1a0a0a",
            "taskbar_hover": "#2a1515",
            "button_close": "#ff4444",
            "button_min": "#ffaa44",
            "button_max": "#44ff88",
            "window_bg": "#1a0a0a",
            "window_fg": "#ffccaa",
            "resize_color": "#2a1515",
            "entry_bg": "#2a1515",
            "entry_fg": "#ffccaa",
            "category": "beautiful"
        },
        "cosmos": {
            "bg": "#05050f",
            "bg_light": "#0f0f20",
            "fg": "#ddaaff",
            "fg_secondary": "#9955dd",
            "accent": "#aa44ff",
            "taskbar": "#05050f",
            "taskbar_hover": "#0f0f20",
            "button_close": "#ff4488",
            "button_min": "#ffcc44",
            "button_max": "#44ffcc",
            "window_bg": "#05050f",
            "window_fg": "#ddaaff",
            "resize_color": "#0f0f20",
            "entry_bg": "#0f0f20",
            "entry_fg": "#ddaaff",
            "category": "beautiful"
        },
        "lava": {
            "bg": "#1a0a05",
            "bg_light": "#2a150a",
            "fg": "#ffbb99",
            "fg_secondary": "#ff7744",
            "accent": "#ff5533",
            "taskbar": "#1a0a05",
            "taskbar_hover": "#2a150a",
            "button_close": "#ff2222",
            "button_min": "#ff8822",
            "button_max": "#22ff88",
            "window_bg": "#1a0a05",
            "window_fg": "#ffbb99",
            "resize_color": "#2a150a",
            "entry_bg": "#2a150a",
            "entry_fg": "#ffbb99",
            "category": "beautiful"
        },
        "gold": {
            "bg": "#1a1a0a",
            "bg_light": "#2a2a15",
            "fg": "#ffdd99",
            "fg_secondary": "#ddbb66",
            "accent": "#ffcc44",
            "taskbar": "#1a1a0a",
            "taskbar_hover": "#2a2a15",
            "button_close": "#ff4444",
            "button_min": "#ffaa44",
            "button_max": "#44ffaa",
            "window_bg": "#1a1a0a",
            "window_fg": "#ffdd99",
            "resize_color": "#2a2a15",
            "entry_bg": "#2a2a15",
            "entry_fg": "#ffdd99",
            "category": "beautiful"
        },
        "cherry": {
            "bg": "#1a0a12",
            "bg_light": "#2a0a1a",
            "fg": "#ffbbdd",
            "fg_secondary": "#ff7799",
            "accent": "#ff44aa",
            "taskbar": "#1a0a12",
            "taskbar_hover": "#2a0a1a",
            "button_close": "#ff2244",
            "button_min": "#ff8844",
            "button_max": "#44ff88",
            "window_bg": "#1a0a12",
            "window_fg": "#ffbbdd",
            "resize_color": "#2a0a1a",
            "entry_bg": "#2a0a1a",
            "entry_fg": "#ffbbdd",
            "category": "beautiful"
        },
        "emerald": {
            "bg": "#0a1a0a",
            "bg_light": "#0f2a15",
            "fg": "#88ffbb",
            "fg_secondary": "#44dd88",
            "accent": "#44ff88",
            "taskbar": "#0a1a0a",
            "taskbar_hover": "#0f2a15",
            "button_close": "#ff4466",
            "button_min": "#ffcc44",
            "button_max": "#44ffcc",
            "window_bg": "#0a1a0a",
            "window_fg": "#88ffbb",
            "resize_color": "#0f2a15",
            "entry_bg": "#0f2a15",
            "entry_fg": "#88ffbb",
            "category": "beautiful"
        }
    }
    
    return themes.get(theme_name, themes["neon"])

def get_theme_category(theme_name):
    """Возвращает категорию темы: 'serious' или 'beautiful'"""
    theme = get_theme_colors(theme_name)
    return theme.get("category", "beautiful")

def get_serious_themes():
    """Возвращает список серьёзных тем"""
    return ["classic", "corporate", "minimal", "office", "dark_pro"]

def get_beautiful_themes():
    """Возвращает список красивых тем"""
    return ["neon", "cyber", "matrix", "ocean", "sunset", "cosmos", "lava", "gold", "cherry", "emerald"]

def get_theme_display_name(theme_name):
    """Возвращает отображаемое имя темы"""
    names = {
        "classic": "🏛️ Classic",
        "corporate": "💼 Corporate",
        "minimal": "⬜ Minimal",
        "office": "📋 Office",
        "dark_pro": "🖥️ Dark Pro",
        "neon": "💠 Neon",
        "cyber": "🌀 Cyberpunk",
        "matrix": "💚 Matrix",
        "ocean": "🌊 Ocean",
        "sunset": "🌅 Sunset",
        "cosmos": "🌠 Cosmos",
        "lava": "🌋 Lava",
        "gold": "✨ Gold",
        "cherry": "🌸 Cherry",
        "emerald": "💎 Emerald",
    }
    return names.get(theme_name, theme_name)

# ===================================================
# ДИАЛОГ С ПРОГРЕСС-БАРОМ ДЛЯ СМЕНЫ ТЕМЫ
# ===================================================
class ThemeProgressDialog:
    """Диалог с прогресс-баром для смены темы"""
    def __init__(self, parent, theme_name, callback):
        self.parent = parent
        self.theme_name = theme_name
        self.callback = callback
        self.window = tk.Toplevel(parent.root)
        self.window.title("🎨 Смена темы")
        self.window.geometry("400x130")
        self.window.configure(bg=COLORS["window_bg"])
        self.window.resizable(False, False)
        self.window.overrideredirect(True)
        
        # Центрируем
        self.window.update_idletasks()
        x = (parent.root.winfo_width() - 400) // 2
        y = (parent.root.winfo_height() - 130) // 2
        self.window.geometry(f"+{x}+{y}")
        
        # Заголовок
        self.label = tk.Label(self.window, text=f"🔄 Применение темы: {get_theme_display_name(theme_name)}", 
                              font=("Segoe UI", 12),
                              fg=COLORS["fg"], bg=COLORS["window_bg"])
        self.label.pack(pady=10)
        
        # Прогресс-бар
        self.progress = ttk.Progressbar(self.window, length=350, mode='determinate')
        self.progress.pack(pady=10)
        
        # Проценты
        self.percent_label = tk.Label(self.window, text="0%", 
                                      font=("Segoe UI", 10),
                                      fg=COLORS["fg"], bg=COLORS["window_bg"])
        self.percent_label.pack()
        
        self.step = 0
        self.max_steps = 10
        self._update_progress()
    
    def _update_progress(self):
        """Обновляет прогресс-бар"""
        if self.step <= self.max_steps:
            percent = int((self.step / self.max_steps) * 100)
            self.progress['value'] = percent
            self.percent_label.config(text=f"{percent}%")
            self.window.update()
            self.step += 1
            self.window.after(50, self._update_progress)
        else:
            self.window.destroy()
            if self.callback:
                self.callback()

# ===================================================
# ФУНКЦИИ РАБОТЫ С БРАУЗЕРОМ
# ===================================================
def get_browser_path():
    return SETTINGS.get("browser_path", "")

def set_browser_path(path):
    SETTINGS["browser_path"] = path
    try:
        with open("neospace_settings.json", 'w', encoding='utf-8') as f:
            json.dump(SETTINGS, f, indent=2)
        return True
    except:
        return False

def get_browser_mode():
    return SETTINGS.get("browser_mode", "internal")

def set_browser_mode(mode):
    SETTINGS["browser_mode"] = mode
    try:
        with open("neospace_settings.json", 'w', encoding='utf-8') as f:
            json.dump(SETTINGS, f, indent=2)
        return True
    except:
        return False

# ===================================================
# ФУНКЦИИ РАБОТЫ С ТЕМАМИ
# ===================================================
def get_current_theme():
    return SETTINGS.get("theme", "neon")

def set_theme(theme_name):
    SETTINGS["theme"] = theme_name
    try:
        with open("neospace_settings.json", 'w', encoding='utf-8') as f:
            json.dump(SETTINGS, f, indent=2)
        return True
    except:
        return False

# ===================================================
# ФУНКЦИИ ИМПОРТА/ЭКСПОРТА
# ===================================================
def get_file_size(path):
    if os.path.isfile(path):
        return os.path.getsize(path)
    total = 0
    for root, dirs, files in os.walk(path):
        for f in files:
            try:
                total += os.path.getsize(os.path.join(root, f))
            except:
                pass
    return total

def copy_with_progress(src, dst, progress_callback=None):
    if os.path.isfile(src):
        total_size = os.path.getsize(src)
        copied = 0
        with open(src, 'rb') as f_src:
            with open(dst, 'wb') as f_dst:
                while True:
                    chunk = f_src.read(8192)
                    if not chunk:
                        break
                    f_dst.write(chunk)
                    copied += len(chunk)
                    if progress_callback:
                        progress_callback(copied, total_size)
        return True
    else:
        shutil.copytree(src, dst)
        return True

class ProgressDialog:
    def __init__(self, parent, title="Выполняется..."):
        self.parent = parent
        self.window = tk.Toplevel(parent.root if hasattr(parent, 'root') else parent)
        self.window.title(title)
        self.window.geometry("400x120")
        self.window.configure(bg=COLORS["window_bg"])
        self.window.resizable(False, False)
        self.window.overrideredirect(True)
        
        self.window.update_idletasks()
        x = (parent.root.winfo_width() - 400) // 2 if hasattr(parent, 'root') else 200
        y = (parent.root.winfo_height() - 120) // 2 if hasattr(parent, 'root') else 200
        self.window.geometry(f"+{x}+{y}")
        
        self.label = tk.Label(self.window, text="Подготовка...", 
                              font=("Segoe UI", 11),
                              fg=COLORS["fg"], bg=COLORS["window_bg"])
        self.label.pack(pady=10)
        
        self.progress = ttk.Progressbar(self.window, length=350, mode='determinate')
        self.progress.pack(pady=10)
        
        self.percent_label = tk.Label(self.window, text="0%", 
                                      font=("Segoe UI", 10),
                                      fg=COLORS["fg"], bg=COLORS["window_bg"])
        self.percent_label.pack()
        
        self.cancelled = False
        self.window.protocol("WM_DELETE_WINDOW", self.cancel)
    
    def update(self, current, total):
        if total > 0:
            percent = int((current / total) * 100)
            self.progress['value'] = percent
            self.percent_label.config(text=f"{percent}%")
            self.window.update()
    
    def set_text(self, text):
        self.label.config(text=text)
        self.window.update()
    
    def cancel(self):
        self.cancelled = True
        self.window.destroy()
    
    def close(self):
        self.window.destroy()

def import_file(parent, status_callback=None):
    path = filedialog.askopenfilename(
        title="Выберите файл для импорта",
        filetypes=[("Все файлы", "*.*")]
    )
    
    if not path:
        return
    
    filename = os.path.basename(path)
    dst_path = os.path.join(VIRTUAL_PATH, filename)
    if os.path.exists(dst_path):
        if not messagebox.askyesno("Файл существует", 
                                   f"Файл '{filename}' уже существует.\nЗаменить?"):
            return
    
    dialog = ProgressDialog(parent, f"📥 Импорт: {filename}")
    dialog.set_text(f"Копирование: {filename}")
    
    total_size = get_file_size(path)
    
    def copy_thread():
        try:
            if os.path.isfile(path):
                copy_with_progress(path, dst_path, dialog.update)
            else:
                if os.path.exists(dst_path):
                    shutil.rmtree(dst_path)
                shutil.copytree(path, dst_path)
                dialog.update(1, 1)
            
            if not dialog.cancelled:
                dialog.set_text("✅ Готово!")
                dialog.progress['value'] = 100
                dialog.percent_label.config(text="100%")
                dialog.window.update()
                time.sleep(0.5)
                dialog.close()
                messagebox.showinfo("Успех", f"✅ '{filename}' успешно импортирован!")
                if status_callback:
                    status_callback(f"📥 Импортирован: {filename}")
        except Exception as e:
            dialog.close()
            messagebox.showerror("Ошибка", f"Не удалось импортировать:\n{str(e)}")
    
    thread = threading.Thread(target=copy_thread)
    thread.daemon = True
    thread.start()

def export_file(parent, filename, status_callback=None):
    src_path = os.path.join(VIRTUAL_PATH, filename)
    
    if not os.path.exists(src_path):
        messagebox.showerror("Ошибка", f"Файл '{filename}' не найден!")
        return
    
    dst_path = filedialog.asksaveasfilename(
        title=f"Сохранить '{filename}' как...",
        initialfile=filename,
        filetypes=[("Все файлы", "*.*")]
    )
    
    if not dst_path:
        return
    
    dialog = ProgressDialog(parent, f"📤 Экспорт: {filename}")
    dialog.set_text(f"Копирование: {filename}")
    
    total_size = get_file_size(src_path)
    
    def copy_thread():
        try:
            if os.path.isfile(src_path):
                copy_with_progress(src_path, dst_path, dialog.update)
            else:
                if os.path.exists(dst_path):
                    shutil.rmtree(dst_path)
                shutil.copytree(src_path, dst_path)
                dialog.update(1, 1)
            
            if not dialog.cancelled:
                dialog.set_text("✅ Готово!")
                dialog.progress['value'] = 100
                dialog.percent_label.config(text="100%")
                dialog.window.update()
                time.sleep(0.5)
                dialog.close()
                messagebox.showinfo("Успех", f"✅ '{filename}' успешно экспортирован!")
                if status_callback:
                    status_callback(f"📤 Экспортирован: {filename}")
        except Exception as e:
            dialog.close()
            messagebox.showerror("Ошибка", f"Не удалось экспортировать:\n{str(e)}")
    
    thread = threading.Thread(target=copy_thread)
    thread.daemon = True
    thread.start()

# ===================================================
# НАСТРОЙКИ ОС (ЗАВИСЯТ ОТ ТЕМЫ)
# ===================================================
def update_colors(theme_name):
    """Обновляет глобальные цвета в зависимости от темы"""
    global COLORS, BUTTONS_SIDE, START_TEXT, OS_ICON, OS_NAME, FULLSCREEN_EXIT_TEXT
    
    theme_colors = get_theme_colors(theme_name)
    
    COLORS = {
        "bg": theme_colors["bg"],
        "bg_light": theme_colors["bg_light"],
        "fg": theme_colors["fg"],
        "fg_secondary": theme_colors.get("fg_secondary", "#888888"),
        "accent": theme_colors["accent"],
        "taskbar": theme_colors["taskbar"],
        "taskbar_hover": theme_colors["taskbar_hover"],
        "button_close": theme_colors["button_close"],
        "button_min": theme_colors["button_min"],
        "button_max": theme_colors["button_max"],
        "window_bg": theme_colors["window_bg"],
        "window_fg": theme_colors["window_fg"],
        "resize_color": theme_colors["resize_color"],
        "entry_bg": theme_colors.get("entry_bg", theme_colors["bg_light"]),
        "entry_fg": theme_colors.get("entry_fg", theme_colors["fg"]),
    }

# Загружаем начальные цвета
update_colors(THEME)

if OS_TYPE == "windows":
    BUTTONS_SIDE = "right"
    START_TEXT = "🪟 Пуск"
    OS_ICON = "🪟"
    OS_NAME = "Windows"
    FULLSCREEN_EXIT_TEXT = "⬛ Выйти из полноэкранного режима"
else:
    BUTTONS_SIDE = "left"
    START_TEXT = "🍎 Launchpad"
    OS_ICON = "🍎"
    OS_NAME = "macOS"
    FULLSCREEN_EXIT_TEXT = "⛶ Выйти из полноэкранного режима"

# ===================================================
# ВИРТУАЛЬНАЯ ГЕРЦОВКА
# ===================================================
class VirtualHz:
    def __init__(self, hz=60):
        self.hz = hz
        self.delay = int(1000 / hz) if hz > 0 else 16
        self.frame_count = 0
        self.last_time = time.time()
        self.fps = 0
        
    def get_delay(self):
        return self.delay
    
    def update_fps(self):
        self.frame_count += 1
        current_time = time.time()
        if current_time - self.last_time >= 1.0:
            self.fps = self.frame_count
            self.frame_count = 0
            self.last_time = current_time
        return self.fps

# ===================================================
# КЛАСС ДЛЯ РЕСАЙЗА ГЛАВНОГО ОКНА
# ===================================================
class ResizeGrip:
    """Класс для управления ресайзом главного окна"""
    def __init__(self, parent):
        self.parent = parent
        self.root = parent.root
        self._resize_zones = []
        self._create_resize_zones()
    
    def _create_resize_zones(self):
        """Создаёт зоны для ресайза по краям и углам"""
        resize_size = 8
        corner_size = 15
        
        # Края
        for side, cursor, direction in [
            ("bottom", "sb_v_double_arrow", 's'),
            ("top", "sb_v_double_arrow", 'n'),
            ("right", "sb_h_double_arrow", 'e'),
            ("left", "sb_h_double_arrow", 'w')
        ]:
            frame = tk.Frame(
                self.root, 
                bg=COLORS["resize_color"],
                height=resize_size if side in ["bottom", "top"] else None,
                width=resize_size if side in ["right", "left"] else None,
                cursor=cursor
            )
            if side in ["bottom", "top"]:
                frame.pack(side=side, fill="x")
            else:
                frame.pack(side=side, fill="y")
            
            frame.bind("<Button-1>", lambda e, d=direction: self._start_resize(e, d))
            frame.bind("<B1-Motion>", self._on_resize)
            frame.bind("<ButtonRelease-1>", self._stop_resize)
            self._resize_zones.append(frame)
        
        # Углы
        corners = [
            ("se", 1.0, 1.0, "size_nw_se"),
            ("sw", 0.0, 1.0, "size_ne_sw"),
            ("ne", 1.0, 0.0, "size_ne_sw"),
            ("nw", 0.0, 0.0, "size_nw_se")
        ]
        for anchor, relx, rely, cursor in corners:
            corner = tk.Frame(
                self.root, 
                bg=COLORS["resize_color"],
                width=corner_size, 
                height=corner_size, 
                cursor=cursor
            )
            corner.place(relx=relx, rely=rely, anchor=anchor)
            corner.bind("<Button-1>", lambda e, a=anchor: self._start_resize(e, a))
            corner.bind("<B1-Motion>", self._on_resize)
            corner.bind("<ButtonRelease-1>", self._stop_resize)
            self._resize_zones.append(corner)
    
    def _start_resize(self, e, direction):
        self._resize_direction = direction
        self._resize_x = e.x_root
        self._resize_y = e.y_root
        self._resize_width = self.root.winfo_width()
        self._resize_height = self.root.winfo_height()
        self._resize_x_win = self.root.winfo_x()
        self._resize_y_win = self.root.winfo_y()
    
    def _on_resize(self, e):
        if not hasattr(self, '_resize_direction'):
            return
        
        dx = e.x_root - self._resize_x
        dy = e.y_root - self._resize_y
        direction = self._resize_direction
        
        new_x = self._resize_x_win
        new_y = self._resize_y_win
        new_w = self._resize_width
        new_h = self._resize_height
        
        # Минимальные размеры
        min_w = 800
        min_h = 600
        
        if 'e' in direction:
            new_w = max(min_w, self._resize_width + dx)
        if 's' in direction:
            new_h = max(min_h, self._resize_height + dy)
        if 'w' in direction:
            new_w = max(min_w, self._resize_width - dx)
            new_x = self._resize_x_win + dx
        if 'n' in direction:
            new_h = max(min_h, self._resize_height - dy)
            new_y = self._resize_y_win + dy
        
        # Для углов
        if direction in ['ne', 'nw', 'se', 'sw']:
            if 'e' in direction:
                new_w = max(min_w, self._resize_width + dx)
            if 's' in direction:
                new_h = max(min_h, self._resize_height + dy)
            if 'w' in direction:
                new_w = max(min_w, self._resize_width - dx)
                new_x = self._resize_x_win + dx
            if 'n' in direction:
                new_h = max(min_h, self._resize_height - dy)
                new_y = self._resize_y_win + dy
        
        self.root.geometry(f"{new_w}x{new_h}+{new_x}+{new_y}")
        self._on_resize_wallpaper(None)
    
    def _stop_resize(self, e):
        if hasattr(self, '_resize_direction'):
            del self._resize_direction
    
    def _on_resize_wallpaper(self, e):
        """Обновляет обои при ресайзе"""
        if hasattr(self.parent, '_on_resize_wallpaper'):
            self.parent._on_resize_wallpaper(e)

# ===================================================
# ВНУТРЕННЕЕ ОКНО
# ===================================================
class InternalWindow:
    def __init__(self, parent, title, width=600, height=400, resizable=True):
        self.parent = parent
        self.width = width
        self.height = height
        self.resizable = resizable
        self.is_minimized = False
        self.is_maximized = False
        self.normal_geometry = None
        
        self.window = tk.Toplevel(parent.root)
        self.window.title(title)
        self.window.geometry(f"{width}x{height}")
        self.window.minsize(400, 300)
        self.window.configure(bg=COLORS["window_bg"])
        self.window.overrideredirect(True)
        
        self._create_title_bar(title)
        
        self.content_frame = tk.Frame(self.window, bg=COLORS["window_bg"])
        self.content_frame.pack(fill="both", expand=True, padx=2, pady=2)
        
        self.window.update_idletasks()
        x = (parent.root.winfo_width() - width) // 2
        y = (parent.root.winfo_height() - height - 50) // 2
        self.window.geometry(f"+{x}+{y}")
        
        self.window.protocol("WM_DELETE_WINDOW", self.close)
        
        self.title_bar.bind('<Button-1>', self.start_move)
        self.title_bar.bind('<B1-Motion>', self.on_move)
        self.title_bar.bind('<ButtonRelease-1>', self.stop_move)
        
        if resizable:
            self._create_resize_zones()
        
        parent.windows.append(self)
    
    def _create_title_bar(self, title):
        self.title_bar = tk.Frame(self.window, bg=COLORS["taskbar"], height=35)
        self.title_bar.pack(fill="x", side="top")
        self.title_bar.pack_propagate(False)
        
        btn_frame = tk.Frame(self.title_bar, bg=COLORS["taskbar"])
        btn_frame.pack(side=BUTTONS_SIDE, padx=8)
        
        if BUTTONS_SIDE == "left":
            for color, cmd in [(COLORS["button_close"], self.close),
                              (COLORS["button_min"], self.minimize),
                              (COLORS["button_max"], self.maximize)]:
                btn = tk.Button(btn_frame, text="●", command=cmd,
                               bg=COLORS["taskbar"], fg=color, relief="flat",
                               font=("Segoe UI", 14))
                btn.pack(side="left", padx=4)
        else:
            for text, cmd, color in [("—", self.minimize, COLORS["fg"]),
                                    ("□", self.maximize, COLORS["fg"]),
                                    ("✖", self.close, COLORS["button_close"])]:
                btn = tk.Button(btn_frame, text=text, command=cmd,
                               bg=COLORS["taskbar"], fg=color, relief="flat",
                               font=("Segoe UI", 12))
                btn.pack(side="left", padx=5)
        
        tk.Label(self.title_bar, text=title, 
                font=("Segoe UI", 10, "bold"),
                fg=COLORS["fg"], bg=COLORS["taskbar"]).pack(side="left", padx=15)
    
    def _create_resize_zones(self):
        resize_size = 8
        corner_size = 15
        
        for side, cursor, direction in [("bottom", "sb_v_double_arrow", 's'),
                                        ("top", "sb_v_double_arrow", 'n'),
                                        ("right", "sb_h_double_arrow", 'e'),
                                        ("left", "sb_h_double_arrow", 'w')]:
            frame = tk.Frame(self.window, bg=COLORS["resize_color"], 
                           height=resize_size if side in ["bottom", "top"] else None,
                           width=resize_size if side in ["right", "left"] else None,
                           cursor=cursor)
            if side in ["bottom", "top"]:
                frame.pack(side=side, fill="x")
            else:
                frame.pack(side=side, fill="y")
            frame.bind("<Button-1>", lambda e, d=direction: self.start_resize(e, d))
            frame.bind("<B1-Motion>", self.on_resize)
            frame.bind("<ButtonRelease-1>", self.stop_resize)
        
        corners = [
            ("se", 1.0, 1.0, "size_nw_se"),
            ("sw", 0.0, 1.0, "size_ne_sw"),
            ("ne", 1.0, 0.0, "size_ne_sw"),
            ("nw", 0.0, 0.0, "size_nw_se")
        ]
        for anchor, relx, rely, cursor in corners:
            corner = tk.Frame(self.window, bg=COLORS["resize_color"], 
                            width=corner_size, height=corner_size, cursor=cursor)
            corner.place(relx=relx, rely=rely, anchor=anchor)
            corner.bind("<Button-1>", lambda e, a=anchor: self.start_resize(e, a))
            corner.bind("<B1-Motion>", self.on_resize)
            corner.bind("<ButtonRelease-1>", self.stop_resize)
    
    def start_move(self, e):
        self.x, self.y = e.x, e.y
    
    def on_move(self, e):
        x = self.window.winfo_x() + e.x - self.x
        y = self.window.winfo_y() + e.y - self.y
        self.window.geometry(f"+{x}+{y}")
    
    def stop_move(self, e):
        pass
    
    def start_resize(self, e, direction):
        self.resize_direction = direction
        self.resize_x = e.x_root
        self.resize_y = e.y_root
        self.resize_width = self.window.winfo_width()
        self.resize_height = self.window.winfo_height()
        self.resize_x_win = self.window.winfo_x()
        self.resize_y_win = self.window.winfo_y()
    
    def on_resize(self, e):
        if not hasattr(self, 'resize_direction'):
            return
        
        dx = e.x_root - self.resize_x
        dy = e.y_root - self.resize_y
        direction = self.resize_direction
        
        new_x = self.resize_x_win
        new_y = self.resize_y_win
        new_w = self.resize_width
        new_h = self.resize_height
        
        if 'e' in direction:
            new_w = max(400, self.resize_width + dx)
        if 's' in direction:
            new_h = max(300, self.resize_height + dy)
        if 'w' in direction:
            new_w = max(400, self.resize_width - dx)
            new_x = self.resize_x_win + dx
        if 'n' in direction:
            new_h = max(300, self.resize_height - dy)
            new_y = self.resize_y_win + dy
        
        if direction in ['ne', 'nw', 'se', 'sw']:
            if 'e' in direction:
                new_w = max(400, self.resize_width + dx)
            if 's' in direction:
                new_h = max(300, self.resize_height + dy)
            if 'w' in direction:
                new_w = max(400, self.resize_width - dx)
                new_x = self.resize_x_win + dx
            if 'n' in direction:
                new_h = max(300, self.resize_height - dy)
                new_y = self.resize_y_win + dy
        
        self.window.geometry(f"{new_w}x{new_h}+{new_x}+{new_y}")
    
    def stop_resize(self, e):
        if hasattr(self, 'resize_direction'):
            del self.resize_direction
    
    def minimize(self):
        self.window.iconify()
    
    def maximize(self):
        if self.is_maximized:
            self.window.geometry(self.normal_geometry)
            self.is_maximized = False
        else:
            self.normal_geometry = self.window.geometry()
            parent_width = self.parent.root.winfo_width()
            parent_height = self.parent.root.winfo_height() - 50
            self.window.geometry(f"{parent_width}x{parent_height}+0+0")
            self.is_maximized = True
    
    def close(self):
        self.window.destroy()
        if self in self.parent.windows:
            self.parent.windows.remove(self)
    
    def get_content(self):
        return self.content_frame

# ===================================================
# ГЛАВНЫЙ КЛАСС ОС
# ===================================================
class NeoSpaceOS:
    def __init__(self, root):
        self.root = root
        self.root.title(f"🧠 NeoSpace OS — {OS_NAME} {HZ}Гц")
        self.root.geometry("1200x700")
        self.root.minsize(800, 600)
        self.root.configure(bg=COLORS["bg"])
        self.root.overrideredirect(True)
        
        self.vhz = VirtualHz(HZ)
        self.windows = []
        
        self.x = 0
        self.y = 0
        self.fullscreen = False
        self.normal_geometry = "1200x700"
        self.old_title_bar_state = None
        self.old_task_bar_state = None
        
        self.title_bar = None
        self.task_bar = None
        self.status_label = None
        self.fullscreen_btn = None
        self.exit_fullscreen_btn = None
        
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.root.bind("<Alt-F4>", lambda e: self.close())
        self.root.bind("<F11>", lambda e: self.toggle_fullscreen())
        
        self._build_ui()
        self._update_clock()
        
        # СОЗДАЁМ ОБЪЕКТ ДЛЯ РЕСАЙЗА
        self.resize_grip = ResizeGrip(self)
        
        print(f"🧠 NeoSpace OS запущена")
        print(f"🖥️ Режим: {OS_NAME}")
        print(f"⚡ Виртуальная герцовка: {HZ} Гц")
        print(f"📂 Виртуальная папка: {VIRTUAL_PATH}")
        print(f"🌐 Режим браузера: {'Внутренний' if get_browser_mode() == 'internal' else 'Внешний'}")
        print(f"🎨 Тема: {get_theme_display_name(get_current_theme())}")
        print("💡 Нажмите F11 для переключения полноэкранного режима")
        if not TKINTERWEB_AVAILABLE:
            print("⚠️ tkinterweb не установлен. Внутренний браузер недоступен.")
    
    def _build_ui(self):
        # === ЗАГОЛОВОК ===
        self.title_bar = tk.Frame(self.root, bg=COLORS["taskbar"], height=40)
        self.title_bar.pack(fill="x", side="top")
        self.title_bar.pack_propagate(False)
        
        self.title_bar.bind('<Button-1>', self.start_move)
        self.title_bar.bind('<B1-Motion>', self.on_move)
        
        btn_frame = tk.Frame(self.title_bar, bg=COLORS["taskbar"])
        btn_frame.pack(side=BUTTONS_SIDE, padx=8)
        
        if BUTTONS_SIDE == "left":
            for color, cmd in [(COLORS["button_close"], self.close),
                              (COLORS["button_min"], self.minimize),
                              (COLORS["button_max"], self.toggle_fullscreen)]:
                btn = tk.Button(btn_frame, text="●", command=cmd,
                               bg=COLORS["taskbar"], fg=color, relief="flat",
                               font=("Segoe UI", 16))
                btn.pack(side="left", padx=4)
        else:
            btn_data = [
                ("—", self.minimize, COLORS["fg"]),
                ("□", self.toggle_fullscreen, COLORS["fg"]),
                ("✖", self.close, COLORS["button_close"]),
            ]
            for text, cmd, color in btn_data:
                btn = tk.Button(btn_frame, text=text, command=cmd,
                               bg=COLORS["taskbar"], fg=color, relief="flat",
                               font=("Segoe UI", 14))
                btn.pack(side="left", padx=6)
        
        title_text = f"🧠 NeoSpace OS — {OS_ICON} {OS_NAME} {HZ}Гц"
        tk.Label(self.title_bar, text=title_text, 
                font=("Segoe UI", 12, "bold"),
                fg=COLORS["accent"], bg=COLORS["taskbar"]).pack(side="left", padx=20)
        
        self.clock_label = tk.Label(self.title_bar, text="00:00", 
                                    font=("Segoe UI", 11),
                                    fg=COLORS["fg"], bg=COLORS["taskbar"])
        self.clock_label.pack(side="right", padx=20)
        
        # === РАБОЧИЙ СТОЛ ===
        self.desktop = tk.Frame(self.root, bg=COLORS["bg"])
        self.desktop.pack(fill="both", expand=True)
        
        self._create_wallpaper()
        self._create_desktop_icons()
        
        # === ПАНЕЛЬ ЗАДАЧ ===
        self.task_bar = tk.Frame(self.root, bg=COLORS["taskbar"], height=50)
        self.task_bar.pack(side="bottom", fill="x")
        self.task_bar.pack_propagate(False)
        
        start_btn = tk.Button(self.task_bar, text=START_TEXT, 
                             command=self.show_start_menu,
                             bg=COLORS["taskbar"], fg=COLORS["accent"],
                             font=("Segoe UI", 11, "bold"),
                             relief="flat", cursor="hand2")
        start_btn.pack(side="left", padx=15, pady=8)
        
        for text, cmd in [("📁 Файлы", self.open_file_manager),
                         ("🧠 AI", self.open_ai_chat),
                         ("🌐 Интернет", self.open_browser),
                         ("⚙️ Настройки", self.open_settings)]:
            btn = tk.Button(self.task_bar, text=text, command=cmd,
                           bg=COLORS["taskbar"], fg=COLORS["fg"],
                           font=("Segoe UI", 10), relief="flat", cursor="hand2")
            btn.pack(side="left", padx=8, pady=8)
            def on_enter(e, b=btn):
                b.config(bg=COLORS["taskbar_hover"])
            def on_leave(e, b=btn):
                b.config(bg=COLORS["taskbar"])
            btn.bind("<Enter>", on_enter)
            btn.bind("<Leave>", on_leave)
        
        # === КНОПКА ВЫХОДА ИЗ ПОЛНОЭКРАННОГО РЕЖИМА ===
        self.exit_fullscreen_btn = tk.Button(
            self.task_bar, 
            text="⛶ Выйти из полноэкранного режима", 
            command=self.toggle_fullscreen,
            bg=COLORS["button_close"], 
            fg="#fff",
            font=("Segoe UI", 9, "bold"),
            relief="flat", 
            cursor="hand2"
        )
        self.exit_fullscreen_btn.pack(side="left", padx=8, pady=8)
        self.exit_fullscreen_btn.config(state="disabled")
        
        self.task_clock = tk.Label(self.task_bar, text="00:00", 
                                   bg=COLORS["taskbar"], fg=COLORS["fg"],
                                   font=("Segoe UI", 11))
        self.task_clock.pack(side="right", padx=20)
        
        self.status_label = tk.Label(self.task_bar, text=f"✅ {HZ} Гц | FPS: 0", 
                                     bg=COLORS["taskbar"], fg=COLORS["fg"],
                                     font=("Segoe UI", 10))
        self.status_label.pack(side="right", padx=15)
        
        self._update_fps()
    
    def _create_wallpaper(self):
        self.wallpaper = tk.Canvas(self.desktop, bg=COLORS["bg"], highlightthickness=0)
        self.wallpaper.pack(fill="both", expand=True)
        self._on_resize_wallpaper(None)
        self.wallpaper.bind("<Configure>", self._on_resize_wallpaper)
    
    def _on_resize_wallpaper(self, e):
        if hasattr(self, 'wallpaper') and self.wallpaper.winfo_exists():
            self.wallpaper.delete("all")
            width = self.root.winfo_width()
            height = self.root.winfo_height()
            self.wallpaper.create_text(
                width//2, height//2 - 150,
                text=f"🧠 NeoSpace OS", font=("Segoe UI", 52, "bold"),
                fill=COLORS["bg_light"], anchor="center"
            )
            self.wallpaper.create_text(
                width//2, height//2 - 70,
                text=f"{OS_ICON} {OS_NAME} • {HZ} Гц • {get_theme_display_name(get_current_theme())}", 
                font=("Segoe UI", 20),
                fill=COLORS["bg_light"], anchor="center"
            )
    
    def _update_fps(self):
        fps = self.vhz.update_fps()
        if self.status_label:
            self.status_label.config(text=f"✅ {HZ} Гц | FPS: {fps}")
        self.root.after(self.vhz.get_delay(), self._update_fps)
    
    def _update_clock(self):
        now = datetime.now().strftime("%H:%M")
        if self.clock_label:
            self.clock_label.config(text=now)
        if self.task_clock:
            self.task_clock.config(text=now)
        self.root.after(self.vhz.get_delay(), self._update_clock)
    
    def _create_desktop_icons(self):
        icons = [
            ("📁 Мои файлы", self.open_file_manager, 60, 60),
            ("🧠 AI-помощник", self.open_ai_chat, 60, 200),
            ("⚙️ Настройки", self.open_settings, 60, 340),
            ("🌐 Браузер", self.open_browser, 60, 480),
            ("⏻ Выключить", self.close, 60, 620),
        ]
        
        for text, cmd, x, y in icons:
            btn = tk.Button(self.desktop, text=text, command=cmd,
                           bg=COLORS["bg"], fg=COLORS["fg"],
                           font=("Segoe UI", 11), relief="flat",
                           width=14, height=4, cursor="hand2")
            btn.place(x=x, y=y)
            
            def on_enter(e, b=btn):
                b.config(bg=COLORS["bg_light"])
            def on_leave(e, b=btn):
                b.config(bg=COLORS["bg"])
            btn.bind("<Enter>", on_enter)
            btn.bind("<Leave>", on_leave)
    
    # === УПРАВЛЕНИЕ ОКНОМ ===
    def start_move(self, e):
        self.x, self.y = e.x, e.y
    
    def on_move(self, e):
        x = self.root.winfo_x() + e.x - self.x
        y = self.root.winfo_y() + e.y - self.y
        self.root.geometry(f"+{x}+{y}")
    
    def minimize(self):
        self.root.iconify()
    
    def toggle_fullscreen(self):
        """Переключает полноэкранный режим"""
        if self.fullscreen:
            # Выход из полноэкранного режима
            self.root.geometry(self.normal_geometry)
            self.fullscreen = False
            self.title_bar.pack(fill="x", side="top")
            self.task_bar.pack(side="bottom", fill="x")
            self.exit_fullscreen_btn.config(state="disabled")
            self._on_resize_wallpaper(None)
        else:
            # Вход в полноэкранный режим
            self.normal_geometry = self.root.geometry()
            self.fullscreen = True
            self.title_bar.pack_forget()
            self.task_bar.pack_forget()
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            self.root.geometry(f"{screen_width}x{screen_height}+0+0")
            self.exit_fullscreen_btn.config(state="normal")
            self.exit_fullscreen_btn.pack(side="left", padx=8, pady=8)
            self._on_resize_wallpaper(None)
    
    def close(self):
        if messagebox.askyesno("Выключение", "Выключить NeoSpace OS?"):
            self.root.quit()
            self.root.destroy()
            sys.exit(0)
    
    # === МЕТОДЫ ДЛЯ БРАУЗЕРА ===
    def open_browser(self):
        browser_path = get_browser_path()
        
        if not browser_path or not os.path.exists(browser_path):
            answer = messagebox.askyesno(
                "🌐 Выбор браузера",
                "Браузер не найден.\nХотите указать путь к нему?\n\n"
                "Вы можете:\n"
                "1. Нажать 'Обзор' и выбрать файл\n"
                "2. Вставить путь из буфера обмена (Ctrl+V)"
            )
            if answer:
                self.open_settings()
            return
        
        mode = get_browser_mode()
        
        if mode == "internal" and TKINTERWEB_AVAILABLE:
            self.open_browser_internal()
        else:
            self.open_browser_external()

    def open_browser_internal(self):
        if not TKINTERWEB_AVAILABLE:
            messagebox.showerror(
                "Ошибка",
                "Библиотека tkinterweb не установлена.\n"
                "Установите: pip install tkinterweb"
            )
            return
        
        browser_path = get_browser_path()
        if not browser_path or not os.path.exists(browser_path):
            self.choose_browser()
            return
        
        try:
            win = InternalWindow(self, "🌐 Внутренний браузер", 900, 650)
            content = win.get_content()
            
            nav_frame = tk.Frame(content, bg=COLORS["taskbar"], height=40)
            nav_frame.pack(fill="x", side="top")
            nav_frame.pack_propagate(False)
            
            url_entry = tk.Entry(nav_frame, bg=COLORS["bg_light"], fg=COLORS["fg"],
                                 font=("Segoe UI", 11), relief="flat")
            url_entry.pack(side="left", fill="x", expand=True, padx=5, pady=5)
            url_entry.insert(0, "http://example.com")
            
            def load_page():
                url = url_entry.get().strip()
                if not url:
                    return
                if not url.startswith("http://") and not url.startswith("https://"):
                    url = "http://" + url
                try:
                    browser.load_file(url)
                    if self.status_label:
                        self.status_label.config(text=f"🌐 Загружено: {url}")
                except Exception as e:
                    messagebox.showerror("Ошибка", f"Не удалось загрузить страницу:\n{str(e)}")
            
            btn_go = tk.Button(nav_frame, text="➤ Перейти", command=load_page,
                              bg=COLORS["accent"], fg=COLORS["bg"],
                              font=("Segoe UI", 10, "bold"), relief="flat")
            btn_go.pack(side="left", padx=5)
            
            btn_home = tk.Button(nav_frame, text="🏠 Домой", 
                                command=lambda: [url_entry.delete(0, tk.END), 
                                                url_entry.insert(0, "http://example.com"), 
                                                load_page()],
                                bg=COLORS["bg_light"], fg=COLORS["fg"],
                                font=("Segoe UI", 10), relief="flat")
            btn_home.pack(side="left", padx=5)
            
            browser = HtmlFrame(content, messages_enabled=False)
            browser.load_file("http://example.com")
            browser.pack(fill="both", expand=True, padx=5, pady=5)
            
            url_entry.bind("<Return>", lambda e: load_page())
            
            if self.status_label:
                self.status_label.config(text="🌐 Внутренний браузер запущен")
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть внутренний браузер:\n{str(e)}")

    def open_browser_external(self):
        browser_path = get_browser_path()
        
        if not browser_path or not os.path.exists(browser_path):
            self.choose_browser()
            return
        
        try:
            if OS_TYPE == "windows":
                subprocess.Popen([browser_path], shell=True)
            else:
                subprocess.Popen(["open", browser_path])
            
            if self.status_label:
                self.status_label.config(text=f"🌐 Внешний браузер запущен")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось запустить браузер:\n{str(e)}")

    def choose_browser(self):
        if OS_TYPE == "windows":
            filetypes = [("Исполняемые файлы", "*.exe"), ("Все файлы", "*.*")]
        else:
            filetypes = [("Приложения", "*.app"), ("Все файлы", "*.*")]
        
        path = filedialog.askopenfilename(
            title="🌐 Выберите ваш браузер",
            filetypes=filetypes
        )
        
        if path:
            if set_browser_path(path):
                if self.status_label:
                    self.status_label.config(text=f"✅ Браузер сохранён: {os.path.basename(path)}")
                messagebox.showinfo("✅ Успех", f"Браузер сохранён!\n\n{path}")
                if messagebox.askyesno("🚀 Запуск", "Запустить браузер сейчас?"):
                    self.open_browser()
            else:
                messagebox.showerror("Ошибка", "Не удалось сохранить настройки")
    
    # === ПРИЛОЖЕНИЯ ===
    def open_file_manager(self):
        win = InternalWindow(self, "📁 Файловый менеджер", 750, 500)
        content = win.get_content()
        
        main_frame = tk.Frame(content, bg=COLORS["window_bg"])
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        control_frame = tk.Frame(main_frame, bg=COLORS["window_bg"])
        control_frame.pack(fill="x", pady=(0, 10))
        
        btn_export = tk.Button(control_frame, text="📤 Экспорт", 
                              command=lambda: self._export_selected(listbox),
                              bg=COLORS["bg_light"], fg=COLORS["fg"],
                              font=("Segoe UI", 10), relief="flat")
        btn_export.pack(side="left", padx=5)
        
        btn_import = tk.Button(control_frame, text="📥 Импорт", 
                              command=lambda: import_file(self, self.update_status),
                              bg=COLORS["bg_light"], fg=COLORS["fg"],
                              font=("Segoe UI", 10), relief="flat")
        btn_import.pack(side="left", padx=5)
        
        listbox_frame = tk.Frame(main_frame, bg=COLORS["window_bg"])
        listbox_frame.pack(fill="both", expand=True)
        
        listbox = tk.Listbox(listbox_frame, bg=COLORS["bg_light"], fg=COLORS["fg"],
                             font=("Consolas", 11), relief="flat")
        listbox.pack(fill="both", expand=True)
        self._refresh_list(listbox)
        
        btn_frame = tk.Frame(main_frame, bg=COLORS["window_bg"])
        btn_frame.pack(fill="x", pady=(10, 0))
        
        btn_open = tk.Button(btn_frame, text="📋 Открыть", 
                            command=lambda: self._open_selected(listbox),
                            bg=COLORS["bg_light"], fg=COLORS["fg"],
                            font=("Segoe UI", 10), relief="flat")
        btn_open.pack(side="left", padx=5)
        
        btn_delete = tk.Button(btn_frame, text="🗑 Удалить", 
                              command=lambda: self._delete_selected(listbox),
                              bg=COLORS["bg_light"], fg=COLORS["fg"],
                              font=("Segoe UI", 10), relief="flat")
        btn_delete.pack(side="left", padx=5)
        
        btn_refresh = tk.Button(btn_frame, text="🔄 Обновить", 
                               command=lambda: self._refresh_list(listbox),
                               bg=COLORS["bg_light"], fg=COLORS["fg"],
                               font=("Segoe UI", 10), relief="flat")
        btn_refresh.pack(side="left", padx=5)
    
    def _export_selected(self, listbox):
        try:
            selected = listbox.get(listbox.curselection()).split(" ", 1)[1]
            export_file(self, selected, self.update_status)
        except:
            messagebox.showwarning("Внимание", "Выберите файл для экспорта")
    
    def _open_selected(self, listbox):
        try:
            selected = listbox.get(listbox.curselection()).split(" ", 1)[1]
            path = os.path.join(VIRTUAL_PATH, selected)
            if os.path.exists(path):
                os.startfile(path)
        except:
            pass
    
    def _delete_selected(self, listbox):
        try:
            selected = listbox.get(listbox.curselection()).split(" ", 1)[1]
            if messagebox.askyesno("Удалить", f"Удалить {selected}?"):
                path = os.path.join(VIRTUAL_PATH, selected)
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)
                self._refresh_list(listbox)
                self.update_status(f"🗑 Удалён: {selected}")
        except:
            pass
    
    def _refresh_list(self, listbox):
        listbox.delete(0, tk.END)
        try:
            for item in sorted(os.listdir(VIRTUAL_PATH)):
                icon = "📁" if os.path.isdir(os.path.join(VIRTUAL_PATH, item)) else "📄"
                listbox.insert(tk.END, f"{icon} {item}")
        except:
            pass
    
    def update_status(self, text):
        if self.status_label:
            self.status_label.config(text=text)
    
    def open_ai_chat(self):
        win = InternalWindow(self, "🧠 AI-помощник", 550, 450)
        content = win.get_content()
        
        chat_area = tk.Text(content, bg=COLORS["bg_light"], fg=COLORS["fg"],
                           font=("Consolas", 11), wrap=tk.WORD, height=15)
        chat_area.pack(fill="both", expand=True, padx=10, pady=10)
        chat_area.insert(tk.END, "🤖: Привет! Я AI-помощник NeoSpace OS.\n")
        chat_area.config(state="disabled")
        
        input_frame = tk.Frame(content, bg=COLORS["window_bg"])
        input_frame.pack(fill="x", padx=10, pady=5)
        
        entry = tk.Entry(input_frame, bg=COLORS["bg_light"], fg=COLORS["fg"],
                        font=("Segoe UI", 11), relief="flat")
        entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        def send_message():
            text = entry.get().strip()
            if not text:
                return
            chat_area.config(state="normal")
            chat_area.insert(tk.END, f"👤: {text}\n")
            chat_area.insert(tk.END, f"🤖: Я получил: {text}\n\n")
            chat_area.config(state="disabled")
            entry.delete(0, tk.END)
        
        btn = tk.Button(input_frame, text="➤ Отправить", command=send_message,
                       bg=COLORS["accent"], fg=COLORS["bg"],
                       font=("Segoe UI", 11, "bold"), relief="flat")
        btn.pack(side="right")
        entry.bind("<Return>", lambda e: send_message())
    
    def open_settings(self):
        win = InternalWindow(self, "⚙️ Настройки", 650, 700, resizable=True)
        content = win.get_content()
        
        # === КОНТЕЙНЕР С ПРОКРУТКОЙ ===
        canvas = tk.Canvas(content, bg=COLORS["window_bg"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(content, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=COLORS["window_bg"])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # === ПРИВЯЗКА КОЛЁСИКА МЫШИ ===
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
        def _bind_mousewheel(widget):
            widget.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", _on_mousewheel))
            widget.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))
            for child in widget.winfo_children():
                _bind_mousewheel(child)
        
        _bind_mousewheel(scrollable_frame)
        
        # === ЗАГОЛОВОК ===
        tk.Label(scrollable_frame, text="⚙️ Настройки системы", 
                font=("Segoe UI", 16, "bold"),
                fg=COLORS["accent"], bg=COLORS["window_bg"]).pack(pady=15)
        
        # === ИНФОРМАЦИЯ ===
        info_data = [
            f"🖥️ Оболочка: {OS_NAME}",
            f"⚡ Герцовка: {HZ} Гц",
            f"📂 Виртуальная папка: {VIRTUAL_PATH}",
        ]
        
        current_theme = get_current_theme()
        info_data.append(f"🎨 Тема: {get_theme_display_name(current_theme)}")
        
        mode = get_browser_mode()
        mode_text = "Внутренний" if mode == "internal" else "Внешний"
        info_data.append(f"📌 Режим браузера: {mode_text}")
        
        for text in info_data:
            tk.Label(scrollable_frame, text=text, 
                    font=("Segoe UI", 11),
                    fg=COLORS["fg"], bg=COLORS["window_bg"]).pack(pady=4, anchor="w", padx=30)
        
        tk.Frame(scrollable_frame, bg=COLORS["bg_light"], height=2).pack(fill="x", padx=30, pady=10)
        
        # === ПУТЬ К БРАУЗЕРУ ===
        tk.Label(scrollable_frame, text="🌐 Путь к браузеру:", 
                font=("Segoe UI", 12, "bold"),
                fg=COLORS["accent"], bg=COLORS["window_bg"]).pack(pady=5, anchor="w", padx=30)
        
        # Поле для ввода пути
        path_frame = tk.Frame(scrollable_frame, bg=COLORS["window_bg"])
        path_frame.pack(fill="x", padx=30, pady=5)
        
        browser_path_var = tk.StringVar(value=get_browser_path())
        
        path_entry = tk.Entry(path_frame, textvariable=browser_path_var,
                              bg=COLORS["entry_bg"], fg=COLORS["entry_fg"],
                              font=("Consolas", 10), relief="flat",
                              insertbackground=COLORS["fg"])
        path_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        # Кнопка вставки из буфера обмена
        def paste_path():
            try:
                clipboard_text = self.root.clipboard_get()
                if clipboard_text:
                    browser_path_var.set(clipboard_text)
                    if self.status_label:
                        self.status_label.config(text="📋 Путь вставлен из буфера обмена")
            except:
                messagebox.showwarning("Внимание", "Не удалось получить данные из буфера обмена")
        
        btn_paste = tk.Button(path_frame, text="📋 Вставить", 
                             command=paste_path,
                             bg=COLORS["bg_light"], fg=COLORS["fg"],
                             font=("Segoe UI", 10), relief="flat")
        btn_paste.pack(side="left", padx=5)
        
        # Кнопка обзора
        def browse_path():
            if OS_TYPE == "windows":
                filetypes = [("Исполняемые файлы", "*.exe"), ("Все файлы", "*.*")]
            else:
                filetypes = [("Приложения", "*.app"), ("Все файлы", "*.*")]
            
            path = filedialog.askopenfilename(
                title="🌐 Выберите ваш браузер",
                filetypes=filetypes
            )
            
            if path:
                browser_path_var.set(path)
                if self.status_label:
                    self.status_label.config(text=f"📂 Выбран: {os.path.basename(path)}")
        
        btn_browse = tk.Button(path_frame, text="📂 Обзор", 
                              command=browse_path,
                              bg=COLORS["bg_light"], fg=COLORS["fg"],
                              font=("Segoe UI", 10), relief="flat")
        btn_browse.pack(side="left", padx=5)
        
        # Кнопка сохранения пути
        def save_path():
            path = browser_path_var.get().strip()
            if path:
                if set_browser_path(path):
                    if self.status_label:
                        self.status_label.config(text=f"✅ Путь сохранён: {os.path.basename(path)}")
                    messagebox.showinfo("✅ Успех", f"Путь к браузеру сохранён!\n\n{path}")
                else:
                    messagebox.showerror("Ошибка", "Не удалось сохранить путь")
            else:
                messagebox.showwarning("Внимание", "Введите путь к браузеру")
        
        btn_save = tk.Button(path_frame, text="💾 Сохранить", 
                            command=save_path,
                            bg=COLORS["accent"], fg=COLORS["bg"],
                            font=("Segoe UI", 10, "bold"), relief="flat")
        btn_save.pack(side="left", padx=5)
        
        # Информация о текущем пути
        current_path = get_browser_path()
        if current_path:
            tk.Label(scrollable_frame, text=f"📌 Текущий путь: {current_path}", 
                    font=("Consolas", 9),
                    fg=COLORS["fg_secondary"], bg=COLORS["window_bg"]).pack(pady=2, anchor="w", padx=30)
        
        tk.Frame(scrollable_frame, bg=COLORS["bg_light"], height=2).pack(fill="x", padx=30, pady=10)
        
        # === НАСТРОЙКИ БРАУЗЕРА ===
        btn_frame = tk.Frame(scrollable_frame, bg=COLORS["window_bg"])
        btn_frame.pack(pady=5)
        
        def toggle_browser_mode():
            current = get_browser_mode()
            new_mode = "external" if current == "internal" else "internal"
            
            if new_mode == "internal" and not TKINTERWEB_AVAILABLE:
                messagebox.showerror("Ошибка", "Внутренний режим недоступен.\nУстановите tkinterweb")
                return
            
            if set_browser_mode(new_mode):
                messagebox.showinfo("✅ Режим изменён", f"Режим браузера: {'Внутренний' if new_mode == 'internal' else 'Внешний'}")
                win.close()
                self.open_settings()
            else:
                messagebox.showerror("Ошибка", "Не удалось сохранить настройки")
        
        mode_btn_text = "🔀 Переключить на внешний" if mode == "internal" else "🔀 Переключить на внутренний"
        if mode == "internal" and not TKINTERWEB_AVAILABLE:
            mode_btn_text = "❌ Внутренний недоступен"
        
        tk.Button(btn_frame, text=mode_btn_text, 
                 command=toggle_browser_mode,
                 bg=COLORS["bg_light"], fg=COLORS["fg"],
                 font=("Segoe UI", 10), relief="flat").pack(side="left", padx=5)
        
        tk.Frame(scrollable_frame, bg=COLORS["bg_light"], height=2).pack(fill="x", padx=30, pady=10)
        
        # === ТЕМЫ ===
        tk.Label(scrollable_frame, text="🎨 Выбор темы", 
                font=("Segoe UI", 14, "bold"),
                fg=COLORS["accent"], bg=COLORS["window_bg"]).pack(pady=5)
        
        # Серьёзные темы
        tk.Label(scrollable_frame, text="━━━ 🏛️ Серьёзный стиль ━━━", 
                font=("Segoe UI", 11),
                fg=COLORS["fg_secondary"], bg=COLORS["window_bg"]).pack(pady=5)
        
        serious_frame = tk.Frame(scrollable_frame, bg=COLORS["window_bg"])
        serious_frame.pack(pady=5)
        
        for theme in get_serious_themes():
            display_name = get_theme_display_name(theme)
            is_active = theme == current_theme
            btn = tk.Button(serious_frame, text=display_name,
                           command=lambda t=theme: self.change_theme(t),
                           bg=COLORS["accent"] if is_active else COLORS["bg_light"],
                           fg=COLORS["bg"] if is_active else COLORS["fg"],
                           font=("Segoe UI", 10), relief="flat")
            btn.pack(side="left", padx=3, pady=2)
        
        # Красивые темы
        tk.Label(scrollable_frame, text="━━━ ✨ Красивый стиль ━━━", 
                font=("Segoe UI", 11),
                fg=COLORS["fg_secondary"], bg=COLORS["window_bg"]).pack(pady=5)
        
        beautiful_frame = tk.Frame(scrollable_frame, bg=COLORS["window_bg"])
        beautiful_frame.pack(pady=5)
        
        for theme in get_beautiful_themes():
            display_name = get_theme_display_name(theme)
            is_active = theme == current_theme
            btn = tk.Button(beautiful_frame, text=display_name,
                           command=lambda t=theme: self.change_theme(t),
                           bg=COLORS["accent"] if is_active else COLORS["bg_light"],
                           fg=COLORS["bg"] if is_active else COLORS["fg"],
                           font=("Segoe UI", 10), relief="flat")
            btn.pack(side="left", padx=3, pady=2)
        
        tk.Frame(scrollable_frame, bg=COLORS["bg_light"], height=2).pack(fill="x", padx=30, pady=10)
        
        # === ГЕРЦОВКА ===
        tk.Label(scrollable_frame, text="⚡ Изменить герцовку:", 
                font=("Segoe UI", 11),
                fg=COLORS["fg"], bg=COLORS["window_bg"]).pack(pady=5)
        
        hz_frame = tk.Frame(scrollable_frame, bg=COLORS["window_bg"])
        hz_frame.pack(pady=5)
        
        for hz in [60, 90, 120]:
            btn = tk.Button(hz_frame, text=f"{hz} Гц", 
                           command=lambda h=hz: self.change_hz(h),
                           bg=COLORS["bg_light"], fg=COLORS["fg"],
                           font=("Segoe UI", 10), relief="flat")
            btn.pack(side="left", padx=5)
        
        tk.Frame(scrollable_frame, bg=COLORS["bg_light"], height=2).pack(fill="x", padx=30, pady=10)
        
        # === ПОДСКАЗКИ ===
        tk.Label(scrollable_frame, text="💡 Изменить ОС можно перезапустив launcher.py", 
                font=("Segoe UI", 10),
                fg=COLORS["fg_secondary"], bg=COLORS["window_bg"]).pack(pady=5)
        
        tk.Label(scrollable_frame, text="💡 F11 — переключить полноэкранный режим", 
                font=("Segoe UI", 10),
                fg=COLORS["fg_secondary"], bg=COLORS["window_bg"]).pack(pady=5)
        
        tk.Label(scrollable_frame, text="🖱️ Тяните за края и углы окна для изменения размера", 
                font=("Segoe UI", 10),
                fg=COLORS["fg_secondary"], bg=COLORS["window_bg"]).pack(pady=5)
    
    def change_theme(self, theme_name):
        """Меняет тему оформления с прогресс-баром"""
        global COLORS
        
        # Проверяем, не та же ли тема
        if get_current_theme() == theme_name:
            messagebox.showinfo("Информация", f"Тема '{get_theme_display_name(theme_name)}' уже активна")
            return
        
        def apply_theme():
            # Сохраняем тему в настройки
            if set_theme(theme_name):
                # Обновляем цвета
                update_colors(theme_name)
                
                # Обновляем все элементы интерфейса
                self.root.configure(bg=COLORS["bg"])
                self.desktop.configure(bg=COLORS["bg"])
                self.task_bar.configure(bg=COLORS["taskbar"])
                self.title_bar.configure(bg=COLORS["taskbar"])
                
                # Обновляем обои
                self._on_resize_wallpaper(None)
                
                # Обновляем заголовок
                for child in self.title_bar.winfo_children():
                    if isinstance(child, tk.Label) and "NeoSpace OS" in child.cget('text'):
                        child.config(fg=COLORS["accent"])
                    elif isinstance(child, tk.Frame):
                        for subchild in child.winfo_children():
                            if isinstance(subchild, tk.Button):
                                subchild.config(bg=COLORS["taskbar"])
                
                # Обновляем кнопки на панели задач
                for child in self.task_bar.winfo_children():
                    if isinstance(child, tk.Button):
                        if "Выйти из полноэкранного" in child.cget('text'):
                            child.config(bg=COLORS["button_close"])
                        else:
                            child.config(bg=COLORS["taskbar"], fg=COLORS["fg"])
                
                # Обновляем часы и статус
                self.clock_label.config(fg=COLORS["fg"], bg=COLORS["taskbar"])
                self.task_clock.config(fg=COLORS["fg"], bg=COLORS["taskbar"])
                if self.status_label:
                    self.status_label.config(fg=COLORS["fg"], bg=COLORS["taskbar"])
                
                # Обновляем все открытые окна
                for window in self.windows:
                    try:
                        window.window.configure(bg=COLORS["window_bg"])
                        window.title_bar.configure(bg=COLORS["taskbar"])
                        window.content_frame.configure(bg=COLORS["window_bg"])
                        # Обновляем кнопки в окне
                        for child in window.title_bar.winfo_children():
                            if isinstance(child, tk.Frame):
                                for subchild in child.winfo_children():
                                    if isinstance(subchild, tk.Button):
                                        subchild.config(bg=COLORS["taskbar"])
                            elif isinstance(child, tk.Label):
                                child.config(fg=COLORS["fg"], bg=COLORS["taskbar"])
                    except:
                        pass
                
                # Обновляем кнопки на рабочем столе
                for child in self.desktop.winfo_children():
                    if isinstance(child, tk.Button):
                        child.config(bg=COLORS["bg"], fg=COLORS["fg"])
                        child.bind("<Enter>", lambda e, b=child: b.config(bg=COLORS["bg_light"]))
                        child.bind("<Leave>", lambda e, b=child: b.config(bg=COLORS["bg"]))
                
                # Обновляем статус
                if self.status_label:
                    self.status_label.config(text=f"🎨 Тема: {get_theme_display_name(theme_name)}")
                
                # Обновляем resize зоны
                for zone in self.resize_grip._resize_zones:
                    try:
                        zone.configure(bg=COLORS["resize_color"])
                    except:
                        pass
                
                # Закрываем настройки и открываем заново
                for window in self.windows[:]:
                    if "Настройки" in window.window.title():
                        window.close()
                self.open_settings()
                
                messagebox.showinfo("✅ Тема изменена", 
                                   f"Тема: {get_theme_display_name(theme_name)}\n\n"
                                   "Все элементы обновлены!")
            else:
                messagebox.showerror("Ошибка", "Не удалось сохранить тему")
        
        # Показываем прогресс-бар
        ThemeProgressDialog(self, theme_name, apply_theme)
    
    def change_hz(self, new_hz):
        global HZ
        HZ = new_hz
        self.vhz = VirtualHz(HZ)
        self.status_label.config(text=f"✅ {HZ} Гц | FPS: 0")
        for child in self.title_bar.winfo_children():
            if isinstance(child, tk.Label) and "Гц" in child.cget('text'):
                child.config(text=f"🧠 NeoSpace OS — {OS_ICON} {OS_NAME} {HZ}Гц")
        self._on_resize_wallpaper(None)
        print(f"⚡ Герцовка изменена на {HZ} Гц")
    
    def show_start_menu(self):
        menu_window = tk.Toplevel(self.root)
        menu_window.title("🧠 Пуск")
        menu_window.geometry("320x450")
        menu_window.configure(bg=COLORS["bg"])
        menu_window.overrideredirect(True)
        
        x = self.root.winfo_x() + 15
        y = self.root.winfo_y() + self.root.winfo_height() - 500
        menu_window.geometry(f"+{x}+{y}")
        
        tk.Label(menu_window, text=f"{OS_ICON} NeoSpace OS", 
                font=("Segoe UI", 16, "bold"),
                fg=COLORS["accent"], bg=COLORS["bg"]).pack(pady=15)
        
        tk.Frame(menu_window, bg=COLORS["bg_light"], height=2).pack(fill="x", padx=10)
        
        apps = [
            ("📁 Файловый менеджер", self.open_file_manager),
            ("🧠 AI-помощник", self.open_ai_chat),
            ("🌐 Браузер", self.open_browser),
            ("⚙️ Настройки", self.open_settings),
            ("📊 Статистика", self.show_stats),
            ("🧹 Очистить", self.clear_desktop),
            ("⛶ Полноэкранный режим", self.toggle_fullscreen),
            ("⏻ Выключить", self.close),
        ]
        
        for text, cmd in apps:
            btn = tk.Button(menu_window, text=text, 
                           command=lambda c=cmd: [c(), menu_window.destroy()],
                           bg=COLORS["bg"], fg=COLORS["fg"],
                           font=("Segoe UI", 11), relief="flat",
                           cursor="hand2", width=30, anchor="w")
            btn.pack(pady=4, padx=15, fill="x")
            
            def on_enter(e, b=btn):
                b.config(bg=COLORS["bg_light"])
            def on_leave(e, b=btn):
                b.config(bg=COLORS["bg"])
            btn.bind("<Enter>", on_enter)
            btn.bind("<Leave>", on_leave)
        
        tk.Button(menu_window, text="✖ Закрыть", command=menu_window.destroy,
                 bg=COLORS["bg"], fg=COLORS["button_close"],
                 font=("Segoe UI", 10), relief="flat",
                 cursor="hand2").pack(pady=15)
    
    def show_stats(self):
        win = InternalWindow(self, "📊 Статистика", 420, 350, resizable=False)
        content = win.get_content()
        
        tk.Label(content, text="📊 Статистика", 
                font=("Segoe UI", 16, "bold"),
                fg=COLORS["accent"], bg=COLORS["window_bg"]).pack(pady=15)
        
        total_files = 0
        total_folders = 0
        total_size = 0
        try:
            for root, dirs, files in os.walk(VIRTUAL_PATH):
                total_folders += len(dirs)
                total_files += len(files)
                for f in files:
                    try:
                        total_size += os.path.getsize(os.path.join(root, f))
                    except:
                        pass
        except:
            pass
        
        stats = [
            f"📁 Файлов: {total_files}",
            f"📂 Папок: {total_folders}",
            f"💾 Размер: {total_size // 1024} КБ",
            f"🖥️ ОС: {OS_NAME}",
            f"⚡ Герцовка: {HZ} Гц",
            f"🎨 Тема: {get_theme_display_name(get_current_theme())}",
        ]
        
        for stat in stats:
            tk.Label(content, text=stat, 
                    font=("Segoe UI", 11),
                    fg=COLORS["fg"], bg=COLORS["window_bg"]).pack(pady=6, anchor="w", padx=30)
    
    def clear_desktop(self):
        if messagebox.askyesno("Очистка", "Удалить все файлы из виртуальной папки?"):
            for item in os.listdir(VIRTUAL_PATH):
                path = os.path.join(VIRTUAL_PATH, item)
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)
            if self.status_label:
                self.status_label.config(text="🧹 Очищено!")

# ===================================================
# ЗАПУСК
# ===================================================
if __name__ == "__main__":
    print("=" * 55)
    print("🧠 NeoSpace OS")
    print(f"🖥️ Режим: {OS_NAME}")
    print(f"⚡ Виртуальная герцовка: {HZ} Гц")
    print(f"🌐 Режим браузера: {'Внутренний' if get_browser_mode() == 'internal' else 'Внешний'}")
    print(f"🎨 Тема: {get_theme_display_name(get_current_theme())}")
    print("💡 F11 — переключить полноэкранный режим")
    print("🖱️ Тяните за края и углы окна для изменения размера")
    if not TKINTERWEB_AVAILABLE:
        print("⚠️ tkinterweb не установлен. Внутренний браузер недоступен.")
    print("=" * 55)
    
    root = tk.Tk()
    app = NeoSpaceOS(root)
    root.mainloop()