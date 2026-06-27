import os
import sys
import shutil
import tkinter as tk
from tkinter import messagebox, filedialog, ttk, simpledialog
from tkinterdnd2 import DND_FILES, TkinterDnD
from datetime import datetime
import threading
import time
import json
import requests
import re
import subprocess

# ===================================================
# АВТООПРЕДЕЛЕНИЕ ПАПКИ ПРОЕКТА
# ===================================================
def get_project_root():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

PROJECT_ROOT = get_project_root()

# ===================================================
# НАСТРОЙКИ
# ===================================================
VIRTUAL_PATH = os.path.join(PROJECT_ROOT, "NeoSpace_Data")
LOG_FILE = os.path.join(VIRTUAL_PATH, "logs.txt")
AI_LOG_FILE = os.path.join(VIRTUAL_PATH, "ai_logs.txt")

# ===================================================
# ТЕМЫ ОФОРМЛЕНИЯ
# ===================================================
THEMES = {
    "neon": {
        "bg": "#1a1a2e",
        "bg_light": "#2a2a4e",
        "fg": "#ffffff",
        "accent": "#00ffff",
        "name": "🌙 Neon"
    },
    "hack": {
        "bg": "#0a0a0a",
        "bg_light": "#1a1a1a",
        "fg": "#00ff41",
        "accent": "#00ff41",
        "name": "🌿 Hack"
    },
    "ocean": {
        "bg": "#0a1628",
        "bg_light": "#1a2a4a",
        "fg": "#b0d4f1",
        "accent": "#00bfff",
        "name": "🌊 Ocean"
    },
    "cherry": {
        "bg": "#1a0a1a",
        "bg_light": "#3a1a2a",
        "fg": "#f5c0d0",
        "accent": "#ff6b9d",
        "name": "🌸 Cherry"
    },
    "solar": {
        "bg": "#f5e6d3",
        "bg_light": "#fff5e6",
        "fg": "#5a3a2a",
        "accent": "#f39c12",
        "name": "☀️ Solar"
    }
}

# Текущие цвета (по умолчанию Neon)
COLORS = THEMES["neon"].copy()
CURRENT_THEME = "neon"

# ===================================================
# АВТОЗАПУСК OLLAMA
# ===================================================
def start_ollama():
    try:
        requests.get("http://localhost:11434/api/tags", timeout=2)
        print("✅ Ollama уже запущен")
        return True
    except:
        pass
    
    print("⏳ Запускаем Ollama...")
    try:
        if sys.platform == "win32":
            subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL, creationflags=subprocess.CREATE_NO_WINDOW)
        else:
            subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL, start_new_session=True)
        
        for _ in range(10):
            time.sleep(1)
            try:
                requests.get("http://localhost:11434/api/tags", timeout=1)
                print("✅ Ollama успешно запущен!")
                return True
            except:
                pass
        
        print("⚠️ Запустите Ollama вручную: ollama serve")
        return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

# ===================================================
# КЛАСС ActionLogger — логирование и откат
# ===================================================
class ActionLogger:
    def __init__(self):
        self.actions = []
        self.backup_dir = os.path.join(VIRTUAL_PATH, "Backups")
        os.makedirs(self.backup_dir, exist_ok=True)
    
    def log(self, action_type, desc, data=None):
        action_id = len(self.actions) + 1
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.actions.append({
            'id': action_id, 'type': action_type, 'desc': desc,
            'timestamp': timestamp, 'data': data, 'reversed': False
        })
        with open(AI_LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(f"{action_id:3d}  {timestamp}  {desc}\n")
        return action_id
    
    def rollback(self, from_id):
        count = 0
        for action in self.actions[from_id-1:]:
            if not action['reversed']:
                self._undo(action)
                action['reversed'] = True
                count += 1
        return count
    
    def _undo(self, action):
        data = action.get('data')
        if not data:
            return
        if action['type'] in ['create_folder', 'create_file'] and os.path.exists(data):
            os.remove(data) if os.path.isfile(data) else shutil.rmtree(data, ignore_errors=True)
        elif action['type'] == 'delete_file':
            backup = os.path.join(self.backup_dir, os.path.basename(data) + ".backup")
            if os.path.exists(backup):
                shutil.copy2(backup, data)
                os.remove(backup)

# ===================================================
# КЛАСС AIAgent — компаньон + исполнитель
# ===================================================
class AIAgent:
    def __init__(self, main_app):
        self.main_app = main_app
        self.logger = main_app.logger
        self.ollama_url = "http://localhost:11434/api/generate"
        
        # Модели от лёгкой к тяжёлой
        self.models = {
            "qwen2.5:1.5b": {"label": "⚡ Лёгкая (qwen2.5:1.5b)", "desc": "Быстрые ответы"},
            "llama3.2:3b": {"label": "🌿 Средняя (llama3.2:3b)", "desc": "Баланс"},
            "llama3.1:8b": {"label": "🧠 Тяжёлая (llama3.1:8b)", "desc": "Сложные задачи"},
        }
        self.model_keys = list(self.models.keys())
        self.current_model = "llama3.1:8b"
        self.is_available = False
        self._check_ollama()
    
    def get_labels(self):
        return [self.models[k]["label"] for k in self.model_keys]
    
    def set_model(self, key):
        if key in self.models:
            self.current_model = key
            return f"✅ {self.models[key]['label']}"
        return f"❌ Модель не найдена"
    
    def get_current_label(self):
        return self.models.get(self.current_model, {}).get('label', self.current_model)
    
    def _check_ollama(self):
        try:
            r = requests.get("http://localhost:11434/api/tags", timeout=2)
            if r.status_code == 200:
                self.is_available = True
                installed = [m['name'] for m in r.json().get('models', [])]
                for m in self.model_keys:
                    if m in installed:
                        self.current_model = m
                        break
                return True
        except:
            pass
        self.is_available = False
        return False
    
    def execute(self, command):
        cmd = command.strip()
        
        # Спецкоманды
        if cmd.startswith('.taskill'):
            return self._handle_taskill(cmd)
        if cmd.startswith('.help'):
            return self._help()
        if cmd.startswith('.models'):
            return self._show_models()
        if cmd.startswith('.model'):
            parts = cmd.split(maxsplit=1)
            if len(parts) > 1:
                for key in self.model_keys:
                    if parts[1].lower() in key.lower():
                        return self.set_model(key)
                return f"❌ Модель не найдена. Доступны: {', '.join(self.model_keys)}"
            return f"📊 Текущая: {self.get_current_label()}"
        
        # Основной запрос
        if self.is_available:
            return self._ask_ai(cmd)
        return self._local(cmd)
    
    def _ask_ai(self, command):
        prompt = f"""Ты — дружелюбный AI-компаньон в виртуальной файловой системе NeoSpace Pro.
Твоя задача:
1. Общаться с пользователем как друг (отвечать на вопросы, шутить, поддерживать диалог)
2. Выполнять команды с файлами в папке {VIRTUAL_PATH}

Команда пользователя: {command}

Ответь строго в формате JSON:

Если это ОБЫЧНЫЙ ВОПРОС (привет, как дела, шутка, вопрос про жизнь):
{{"action":"chat","response":"твой_дружеский_ответ"}}

Если это КОМАНДА с файлами:
{{"action":"create_folder|create_file|delete_file|open_folder|info","path":"путь","content":"содержимое_если_нужно","response":"ответ"}}

Если вопрос + команда одновременно:
{{"action":"mixed","chat_response":"ответ_на_вопрос","file_action":"create_folder|create_file|delete_file|open_folder","path":"путь","content":"содержимое","response":"отчёт"}}

Примеры:
- "Привет!" → {{"action":"chat","response":"Привет! Рад тебя видеть! Чем могу помочь?"}}
- "Как дела?" → {{"action":"chat","response":"У меня всё отлично! А у тебя?"}}
- "Создай папку Фото" → {{"action":"create_folder","path":"Фото","response":"Папка создана!"}}
- "Расскажи шутку" → {{"action":"chat","response":"Почему программисты не любят природу? Слишком много багов!"}}
- "Как дела? И создай папку План" → {{"action":"mixed","chat_response":"У меня всё супер!","file_action":"create_folder","path":"План","response":"Папка создана!"}}"""
        
        try:
            r = requests.post(self.ollama_url, json={
                "model": self.current_model, "prompt": prompt,
                "stream": False, "temperature": 0.3, "max_tokens": 800
            }, timeout=90)
            return self._parse(r.json().get('response', ''), command)
        except Exception as e:
            return f"❌ Ошибка: {e}"
    
    def _parse(self, json_str, original):
        try:
            match = re.search(r'\{.*\}', json_str, re.DOTALL)
            if match:
                json_str = match.group()
            data = json.loads(json_str)
            action = data.get('action')
            
            # === ОБЫЧНЫЙ ЧАТ ===
            if action == 'chat':
                return f"🧠 {data.get('response', 'Я тебя слышу!')}"
            
            # === СМЕШАННЫЙ ===
            if action == 'mixed':
                chat = data.get('chat_response', '')
                file_action = data.get('file_action')
                path = data.get('path', '').strip()
                content = data.get('content', '')
                resp = data.get('response', '')
                result = f"🧠 {chat}\n" if chat else ""
                
                if file_action and path:
                    full = os.path.join(VIRTUAL_PATH, path)
                    if file_action == 'create_folder':
                        res = self._create_folder(full, path, resp)
                    elif file_action == 'create_file':
                        res = self._create_file(full, content, path, resp)
                    elif file_action == 'open_folder':
                        res = self._open_folder(full, path, resp)
                    elif file_action == 'delete_file':
                        res = self._delete_item(full, path, resp)
                    else:
                        res = f"✅ {resp}"
                    result += f"📁 {res}" if file_action == 'create_folder' else f"📄 {res}" if file_action == 'create_file' else f"📂 {res}" if file_action == 'open_folder' else f"🗑 {res}"
                return result
            
            # === ФАЙЛОВЫЕ КОМАНДЫ ===
            path = data.get('path', '').strip()
            if not path:
                path = self._extract_path(original)
            full = os.path.join(VIRTUAL_PATH, path) if path else None
            
            if action == 'create_folder':
                return self._create_folder(full, path, data.get('response', '✅'))
            if action == 'create_file':
                return self._create_file(full, data.get('content', ''), path, data.get('response', '✅'))
            if action == 'delete_file':
                return self._delete_item(full, path, data.get('response', '✅'))
            if action == 'open_folder':
                return self._open_folder(full, path, data.get('response', '✅'))
            if action == 'info':
                return self._get_info(path, data.get('response', ''))
            
            return f"✅ {data.get('response', 'Выполнено!')}"
            
        except:
            return self._local(original)
    
    # === ФАЙЛОВЫЕ ДЕЙСТВИЯ ===
    def _create_folder(self, full, path, resp):
        if not full:
            return "❌ Укажите путь"
        try:
            os.makedirs(full, exist_ok=True)
            self.logger.log('create_folder', f'Создана папка: {path}', full)
            return f"✅ {resp}\n📁 Создана папка: {path}"
        except Exception as e:
            return f"❌ Ошибка: {e}"
    
    def _create_file(self, full, content, path, resp):
        if not full:
            return "❌ Укажите путь"
        try:
            os.makedirs(os.path.dirname(full), exist_ok=True)
            with open(full, 'w', encoding='utf-8') as f:
                f.write(content)
            self.logger.log('create_file', f'Создан файл: {path}', full)
            return f"✅ {resp}\n📄 Создан файл: {path}"
        except Exception as e:
            return f"❌ Ошибка: {e}"
    
    def _open_folder(self, full, path, resp):
        if not full:
            return "❌ Укажите путь"
        if not os.path.exists(full):
            try:
                os.makedirs(full, exist_ok=True)
                self.logger.log('create_folder', f'Создана папка: {path}', full)
            except Exception as e:
                return f"❌ Ошибка: {e}"
        try:
            os.startfile(full)
            self.logger.log('open_folder', f'Открыта папка: {path}', full)
            return f"✅ {resp}\n📂 Открыта папка: {path}"
        except Exception as e:
            return f"❌ Ошибка: {e}"
    
    def _delete_item(self, full, path, resp):
        if not full:
            return "❌ Укажите путь"
        try:
            if not os.path.exists(full):
                return f"❌ Не найден: {path}"
            backup = os.path.join(self.logger.backup_dir, os.path.basename(full) + ".backup")
            if os.path.isdir(full):
                shutil.copytree(full, backup, dirs_exist_ok=True)
                shutil.rmtree(full)
            else:
                shutil.copy2(full, backup)
                os.remove(full)
            self.logger.log('delete_file', f'Удалён: {path}', full)
            return f"✅ {resp}\n🗑 Удалён: {path}"
        except Exception as e:
            return f"❌ Ошибка: {e}"
    
    def _get_info(self, path, resp):
        if not path:
            return "📊 " + resp
        full = os.path.join(VIRTUAL_PATH, path)
        if os.path.exists(full):
            size = os.path.getsize(full) if os.path.isfile(full) else 0
            modified = datetime.fromtimestamp(os.path.getmtime(full))
            return f"📊 {path}\n📏 {size} байт\n🕐 {modified.strftime('%d.%m.%Y %H:%M')}"
        return f"❌ Не найден: {path}"
    
    def _extract_path(self, text):
        match = re.search(r'["\'«]([^"\'»]+)["\'»]', text)
        if match:
            return match.group(1).strip()
        for kw in ['папку', 'файл', 'удали', 'создай', 'открой']:
            if kw in text.lower():
                parts = text.lower().split(kw, 1)
                if len(parts) > 1:
                    name = parts[1].strip()
                    for p in ['в ', 'с ', 'на ']:
                        if name.startswith(p):
                            name = name[len(p):]
                    for c in [' и ', ', ', '; ']:
                        if c in name:
                            name = name.split(c)[0]
                    return name[:50]
        return None
    
    def _local(self, command):
        cmd = command.lower()
        if 'привет' in cmd or 'здравствуй' in cmd:
            return "🧠 Привет! Рад тебя видеть! Чем могу помочь?"
        if 'как дела' in cmd or 'как ты' in cmd:
            return "🧠 У меня всё отлично! А у тебя? Что нового в мире файлов?"
        if 'шутк' in cmd or 'смешн' in cmd or 'анекдот' in cmd:
            return "🧠 Почему программисты не любят природу? Потому что там слишком много багов!"
        if 'создай папку' in cmd:
            path = self._extract_path(command)
            if path:
                return self._create_folder(os.path.join(VIRTUAL_PATH, path), path, "Создано!")
            return "❌ Укажите имя папки в кавычках"
        if 'создай файл' in cmd:
            path = self._extract_path(command)
            if path:
                return self._create_file(os.path.join(VIRTUAL_PATH, path), "", path, "Создано!")
            return "❌ Укажите имя файла в кавычках"
        if 'открой папку' in cmd:
            path = self._extract_path(command)
            if path:
                return self._open_folder(os.path.join(VIRTUAL_PATH, path), path, "Открыто!")
            return "❌ Укажите имя папки в кавычках"
        if 'удали' in cmd:
            path = self._extract_path(command)
            if path:
                return self._delete_item(os.path.join(VIRTUAL_PATH, path), path, "Удалено!")
            return "❌ Укажите имя в кавычках"
        if '.taskill' in cmd:
            return self._handle_taskill(cmd)
        return f"🧠 Я тебя слышу! Но пока не знаю, как ответить на: {command}\n💡 Попробуй .help для справки"
    
    def _handle_taskill(self, cmd):
        parts = cmd.split()
        if len(parts) == 2:
            try:
                n = int(parts[1])
                if n < 1 or n > len(self.logger.actions):
                    return f"❌ Строка {n} не найдена (всего {len(self.logger.actions)})"
                count = self.logger.rollback(n)
                return f"✅ Откат! Отменено {count} действий со строки {n}"
            except:
                return "❌ Укажите номер строки"
        return "❌ Использование: .taskill <номер>"
    
    def _help(self):
        return """📚 **Команды:**

💬 **Общение:**
  • Привет, как дела, расскажи шутку

📂 **Файлы:**
  • Создай папку "Название"
  • Создай файл "файл.txt" с текстом "текст"
  • Открой папку "Название"
  • Удали "Название"

🔧 **Управление:**
  • .taskill 5 — откатить действия
  • .model qwen2.5:1.5b — сменить модель
  • .models — показать доступные
  • .help — справка

💡 **Примеры:**
  • "Привет! Создай папку Проекты"
  • "Как дела? И открой папку Фото"
  • "Расскажи шутку и создай файл joke.txt"
"""
    
    def _show_models(self):
        try:
            r = requests.get("http://localhost:11434/api/tags", timeout=2)
            if r.status_code == 200:
                models = r.json().get('models', [])
                result = "📦 **Модели:**\n"
                for m in models:
                    name = m.get('name', 'unknown')
                    size = m.get('size', 0) // (1024**3)
                    active = "✅" if name == self.current_model else "  "
                    label = self.models.get(name, {}).get('label', name)
                    result += f"{active} {label} ({size} ГБ)\n"
                return result
            return "❌ Ollama не доступна"
        except:
            return "❌ Ollama не доступна"

# ===================================================
# КЛАСС NeoSpacePro — интерфейс
# ===================================================
class NeoSpacePro:
    def __init__(self, root):
        self.root = root
        self.root.overrideredirect(True)
        self.root.geometry("1200x750")
        self.root.minsize(900, 600)
        self.root.configure(bg=COLORS["bg"])
        
        self.virtual_path = VIRTUAL_PATH
        self._ensure_folders()
        
        self.current_path = tk.StringVar(value=self.virtual_path)
        self.history = []
        self.forward_history = []
        self.search_var = tk.StringVar()
        self.timer_running = False
        self.terminal_visible = False
        self.x = self.y = 0
        
        self.logger = ActionLogger()
        self.ai = AIAgent(self)
        
        # Загружаем сохранённую тему
        self.load_theme()
        
        self.root.drop_target_register(DND_FILES)
        self.root.dnd_bind('<<Drop>>', self.on_drop)
        
        self._build_ui()
        self._refresh()
        self._log("🚀 NeoSpace Pro v2.3 запущена")
        self._log(f"🤖 {self.ai.get_current_label()}")
        self._log(f"🎨 Тема: {THEMES[CURRENT_THEME]['name']}")
        self._log("💡 Просто поговори со мной или дай команду!")
    
    def _ensure_folders(self):
        for f in [self.virtual_path, os.path.join(self.virtual_path, "Экспорт"), 
                 os.path.join(self.virtual_path, "Backups")]:
            os.makedirs(f, exist_ok=True)
        if not os.path.exists(LOG_FILE):
            with open(LOG_FILE, 'w', encoding='utf-8') as f:
                f.write("=== ЛОГИ NeoSpace Pro ===\n")
    
    def _log(self, msg):
        ts = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(f"[{ts}] {msg}\n")
        print(f"[{ts}] {msg}")
        if hasattr(self, 'log_text'):
            self.add_log(f"📌 {msg}")
    
    def _build_ui(self):
        # Заголовок
        title = tk.Frame(self.root, bg=COLORS["bg_light"], height=35)
        title.pack(fill='x', side='top')
        title.pack_propagate(False)
        title.bind('<Button-1>', self.start_move)
        title.bind('<B1-Motion>', self.on_move)
        
        tk.Label(title, text="🧠 NEO SPACE PRO v2.3", font=("Cascadia Code", 12, "bold"),
                fg=COLORS["accent"], bg=COLORS["bg_light"]).pack(side='left', padx=15)
        
        status = "🟢" if self.ai.is_available else "🔴"
        tk.Label(title, text=f"AI: {status} {self.ai.get_current_label()}", 
                font=("Cascadia Code", 9), fg=COLORS["fg"], bg=COLORS["bg_light"]).pack(side='left', padx=10)
        
        btn_frame = tk.Frame(title, bg=COLORS["bg_light"])
        btn_frame.pack(side='right', padx=5)
        for t, cmd, c in [("—", self.minimize, COLORS["fg"]), ("□", self.maximize, COLORS["fg"]), ("✖", self.close, "#ff6b6b")]:
            tk.Button(btn_frame, text=t, command=cmd, bg=COLORS["bg_light"], fg=c, relief='flat', font=("Segoe UI", 12)).pack(side='left', padx=5)
        
        main = tk.Frame(self.root, bg=COLORS["bg"])
        main.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Верхняя панель
        top = tk.Frame(main, bg=COLORS["bg_light"], height=45)
        top.pack(fill="x", side="top")
        top.pack_propagate(False)
        tk.Label(top, text="📁 Виртуальная среда", font=("Cascadia Code", 12, "bold"),
                fg=COLORS["accent"], bg=COLORS["bg_light"]).pack(side="left", padx=15)
        tk.Label(top, text=f"📂 {self.virtual_path}", font=("Cascadia Code", 10),
                fg=COLORS["fg"], bg=COLORS["bg_light"]).pack(side="right", padx=15)
        
        # === ПОИСК ===
        search = tk.Frame(main, bg=COLORS["bg"])
        search.pack(fill="x", padx=20, pady=5)

        tk.Label(search, text="🔍 Поиск:", bg=COLORS["bg"], fg=COLORS["fg"],
                 font=("Cascadia Code", 10)).pack(side="left", padx=(0, 5))

        self.search_entry = tk.Entry(search, textvariable=self.search_var,
                                    font=("Cascadia Code", 10), bg=COLORS["bg_light"],
                                    fg=COLORS["fg"], relief="flat", width=30)
        self.search_entry.pack(side="left", padx=(0, 5), fill="x", expand=True)
        self.search_var.trace_add("write", lambda *a: self._refresh())

        # ✅ ГАЛОЧКА "ЦЕЛЕВОЙ ПОИСК"
        self.deep_search_var = tk.BooleanVar(value=False)
        deep_check = tk.Checkbutton(search, text="🎯 Целевой поиск",
                                    variable=self.deep_search_var,
                                    bg=COLORS["bg"], fg=COLORS["fg"],
                                    selectcolor=COLORS["bg"],
                                    font=("Cascadia Code", 9),
                                    command=self._toggle_deep_search)
        deep_check.pack(side="left", padx=(10, 5))

        # ❓ КНОПКА ПОДСКАЗКИ
        help_btn = tk.Button(search, text="❓", command=self._show_search_help,
                             bg=COLORS["bg"], fg=COLORS["accent"],
                             relief="flat", font=("Segoe UI", 12),
                             cursor="hand2")
        help_btn.pack(side="left", padx=5)

        # === НАСТРОЙКИ ЦЕЛЕВОГО ПОИСКА ===
        self.search_options_frame = tk.Frame(main, bg=COLORS["bg"])
        self.search_options_frame.pack(fill="x", padx=40, pady=2)
        self.search_options_frame.pack_forget()

        # Переменные для режимов
        self.auto_open_var = tk.BooleanVar(value=True)
        self.show_only_var = tk.BooleanVar(value=False)

        # Галочка "Открыть файл"
        auto_open_check = tk.Checkbutton(self.search_options_frame,
                                         text="📂 Открыть файл после поиска",
                                         variable=self.auto_open_var,
                                         bg=COLORS["bg"], fg=COLORS["fg"],
                                         selectcolor=COLORS["bg"],
                                         font=("Cascadia Code", 9),
                                         command=self._on_auto_open_change)
        auto_open_check.pack(side="left", padx=(0, 20))

        # Галочка "Показать файл"
        show_only_check = tk.Checkbutton(self.search_options_frame,
                                         text="👁️ Показать файл (не открывать)",
                                         variable=self.show_only_var,
                                         bg=COLORS["bg"], fg=COLORS["fg"],
                                         selectcolor=COLORS["bg"],
                                         font=("Cascadia Code", 9),
                                         command=self._on_show_only_change)
        show_only_check.pack(side="left")
        
        # === ПРОГРЕСС-БАР ===
        progress_frame = tk.Frame(main, bg=COLORS["bg"])
        progress_frame.pack(fill="x", padx=20, pady=5)
        
        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, 
                                            maximum=100, length=400)
        self.progress_bar.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        self.progress_label = tk.Label(progress_frame, text="0%", 
                                       bg=COLORS["bg"], fg=COLORS["fg"],
                                       font=("Cascadia Code", 9))
        self.progress_label.pack(side="right")
        
        # Кнопки
        btn_row = tk.Frame(main, bg=COLORS["bg"])
        btn_row.pack(fill="x", padx=20, pady=5)
        for t, cmd in [("📋 Копировать рабочий стол", self._copy_desktop), ("📥 Импорт", self._import_folder),
                      ("📤 Экспорт", self._export_folder), ("➕ Создать файл", self._create_file),
                      ("🗑 Удалить", self._delete_file), ("⏱️ Таймер", self._show_timer),
                      ("🧠 Терминал", self.toggle_terminal)]:
            tk.Button(btn_row, text=t, command=cmd, bg=COLORS["bg_light"], fg=COLORS["fg"],
                     font=("Cascadia Code", 9, "bold"), relief="flat", cursor="hand2").pack(side="left", padx=2, pady=3)
        
        # Разделитель
        paned = ttk.PanedWindow(main, orient=tk.HORIZONTAL)
        paned.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.file_frame = tk.Frame(paned, bg=COLORS["bg"])
        paned.add(self.file_frame, weight=3)
        
        self.terminal_frame = tk.Frame(paned, bg=COLORS["bg_light"])
        paned.add(self.terminal_frame, weight=1)
        self.terminal_frame.pack_forget()
        
        # Файловый менеджер
        self.tree = ttk.Treeview(self.file_frame, columns=("size", "modified"), show="tree headings")
        self.tree.heading("#0", text="Имя")
        self.tree.heading("size", text="Размер")
        self.tree.heading("modified", text="Изменён")
        self.tree.column("#0", width=400)
        self.tree.column("size", width=100)
        self.tree.column("modified", width=150)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(self.file_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.bind("<Double-1>", self._open_item)
        
        # Терминал
        self._build_terminal()
        
        # Нижняя панель
        taskbar = tk.Frame(main, bg=COLORS["bg_light"], height=40)
        taskbar.pack(side="bottom", fill="x")
        taskbar.pack_propagate(False)
        
        self.back_btn = tk.Button(taskbar, text="◀ Назад", command=self._go_back,
                                 bg=COLORS["bg_light"], fg=COLORS["fg"], font=("Cascadia Code", 10),
                                 relief="flat", state="disabled")
        self.back_btn.pack(side="left", padx=(10, 5), pady=5)
        
        self.forward_btn = tk.Button(taskbar, text="Вперёд ▶", command=self._go_forward,
                                    bg=COLORS["bg_light"], fg=COLORS["fg"], font=("Cascadia Code", 10),
                                    relief="flat", state="disabled")
        self.forward_btn.pack(side="left", padx=(0, 15), pady=5)
        
        tk.Button(taskbar, text="🔄 Обновить", command=self._refresh,
                 bg=COLORS["bg_light"], fg=COLORS["accent"], font=("Cascadia Code", 10, "bold"),
                 relief="flat", cursor="hand2").pack(side="left", padx=5, pady=5)
        
        tk.Button(taskbar, text="📂 Открыть", command=self._open_folder,
                 bg=COLORS["bg_light"], fg=COLORS["fg"], font=("Cascadia Code", 10),
                 relief="flat", cursor="hand2").pack(side="left", padx=5, pady=5)
        
        self.action_counter = tk.Label(taskbar, text="📊 Действий: 0", bg=COLORS["bg_light"],
                                      fg=COLORS["fg"], font=("Cascadia Code", 9))
        self.action_counter.pack(side="left", padx=15, pady=5)
        
        self.status = tk.Label(taskbar, text="Готов", bg=COLORS["bg_light"],
                              fg=COLORS["fg"], font=("Cascadia Code", 9))
        self.status.pack(side="right", padx=15, pady=5)
    
    def _build_terminal(self):
        header = tk.Frame(self.terminal_frame, bg=COLORS["bg_light"])
        header.pack(fill='x')
        
        tk.Label(header, text="🧠 AI-Терминал", font=("Cascadia Code", 10, "bold"),
                fg=COLORS["accent"], bg=COLORS["bg_light"]).pack(side='left', padx=10, pady=5)
        
        # === ВЫБОР МОДЕЛИ ===
        model_frame = tk.Frame(header, bg=COLORS["bg_light"])
        model_frame.pack(side='left', padx=10)
        tk.Label(model_frame, text="Модель:", font=("Cascadia Code", 8),
                fg=COLORS["fg"], bg=COLORS["bg_light"]).pack(side='left', padx=2)
        
        self.model_var = tk.StringVar(value=self.ai.get_current_label())
        model_menu = ttk.Combobox(model_frame, textvariable=self.model_var,
                                 values=self.ai.get_labels(), state="readonly", width=30)
        model_menu.pack(side='left', padx=2)
        model_menu.bind('<<ComboboxSelected>>', self._change_model)
        
        # === ВЫБОР ТЕМЫ ===
        theme_frame = tk.Frame(header, bg=COLORS["bg_light"])
        theme_frame.pack(side='left', padx=10)
        
        tk.Label(theme_frame, text="Тема:", font=("Cascadia Code", 8),
                 fg=COLORS["fg"], bg=COLORS["bg_light"]).pack(side='left', padx=2)
        
        self.theme_var = tk.StringVar(value=THEMES[CURRENT_THEME]["name"])
        theme_menu = ttk.Combobox(theme_frame, textvariable=self.theme_var,
                                  values=[t["name"] for t in THEMES.values()],
                                  state="readonly", width=18)
        theme_menu.pack(side='left', padx=2)
        theme_menu.bind('<<ComboboxSelected>>', self._change_theme)
        
        tk.Button(header, text="✖", command=self.toggle_terminal,
                 bg=COLORS["bg_light"], fg="#ff6b6b", relief='flat',
                 font=("Segoe UI", 10)).pack(side='right', padx=5)
        
        self.log_text = tk.Text(self.terminal_frame, bg="#0a0a1a", fg="#00ff88", 
                               font=("Consolas", 9), height=8)
        self.log_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        input_frame = tk.Frame(self.terminal_frame, bg=COLORS["bg_light"])
        input_frame.pack(fill='x', padx=5, pady=5)
        
        self.command_entry = tk.Entry(input_frame, bg=COLORS["bg_light"], 
                                     fg=COLORS["fg"], font=("Cascadia Code", 10))
        self.command_entry.pack(side='left', fill='x', expand=True, padx=(0, 5))
        self.command_entry.bind('<Return>', self.execute)
        
        tk.Button(input_frame, text="▶", command=self.execute,
                 bg=COLORS["bg_light"], fg=COLORS["accent"], relief='flat',
                 font=("Cascadia Code", 12)).pack(side='right')
    
    def _change_model(self, e):
        label = self.model_var.get()
        for key, data in self.ai.models.items():
            if data['label'] == label:
                result = self.ai.set_model(key)
                self.add_log(f"🔄 {result}")
                self._refresh_model_display()
                return

    def _change_theme(self, e):
        theme_name = self.theme_var.get()
        for key, theme in THEMES.items():
            if theme["name"] == theme_name:
                self._apply_theme(key)
                return

    def _apply_theme(self, theme_key):
        global COLORS, CURRENT_THEME
        
        theme = THEMES[theme_key]
        CURRENT_THEME = theme_key
        
        COLORS.update(theme)
        self.root.configure(bg=COLORS["bg"])
        
        for widget in self.root.winfo_children():
            widget.destroy()
        
        self._build_ui()
        self._refresh()
        self.add_log(f"🎨 Тема изменена на {theme['name']}")
        
        try:
            with open(os.path.join(VIRTUAL_PATH, "theme.txt"), 'w', encoding='utf-8') as f:
                f.write(theme_key)
        except:
            pass

    def load_theme(self):
        try:
            with open(os.path.join(VIRTUAL_PATH, "theme.txt"), 'r', encoding='utf-8') as f:
                theme = f.read().strip()
                if theme in THEMES:
                    self._apply_theme(theme)
                    return
        except:
            pass
        self._apply_theme("neon")
    
    def _refresh_model_display(self):
        for w in self.root.winfo_children():
            if isinstance(w, tk.Frame):
                for c in w.winfo_children():
                    if isinstance(c, tk.Label) and "AI:" in c.cget('text'):
                        status = "🟢" if self.ai.is_available else "🔴"
                        c.config(text=f"AI: {status} {self.ai.get_current_label()}")
                        return
    
    def _toggle_deep_search(self):
        if self.deep_search_var.get():
            self.search_options_frame.pack(fill="x", padx=40, pady=2)
            self.add_log("🎯 Целевой поиск активирован")
        else:
            self.search_options_frame.pack_forget()
            self.progress_var.set(0)
            self.progress_label.config(text="0%")
            self.add_log("🔍 Обычный поиск")
    
    def _on_auto_open_change(self):
        """Срабатывает при выборе 'Открыть файл'"""
        if self.auto_open_var.get():
            self.show_only_var.set(False)
            self.add_log("📂 Режим: автооткрытие файла")
        else:
            self.show_only_var.set(True)
            self.add_log("👁️ Режим: показать файл")

    def _on_show_only_change(self):
        """Срабатывает при выборе 'Показать файл'"""
        if self.show_only_var.get():
            self.auto_open_var.set(False)
            self.add_log("👁️ Режим: показать файл (без открытия)")
        else:
            self.auto_open_var.set(True)
            self.add_log("📂 Режим: автооткрытие файла")
    
    def _show_search_help(self):
        """Показывает подсказку о поиске с динамическим размером"""
        help_window = tk.Toplevel(self.root)
        help_window.title("❓ О поиске")
        help_window.configure(bg=COLORS["bg"])
        help_window.resizable(False, False)
        
        # Основной фрейм
        main_frame = tk.Frame(help_window, bg=COLORS["bg"])
        main_frame.pack(fill="both", expand=True, padx=20, pady=15)
        
        # Заголовок
        tk.Label(main_frame, text="🔍 Как работает поиск", 
                 font=("Cascadia Code", 14, "bold"),
                 fg=COLORS["accent"], bg=COLORS["bg"]).pack(pady=(0, 15))
        
        # Текст с пояснениями
        text = """
🔹 Обычный поиск (выключен):
   • Ищет только по имени файла
   • Быстрый, поверхностный
   • Подходит для большинства случаев

🔹 Целевой поиск (включён):
   • Ищет ПО ВСЕМУ СОДЕРЖИМОМУ файлов
   • Медленнее, но находит всё
   • Ищет текст внутри файлов

📂 Открыть файл — автоматически открывает
👁️ Показать файл — просто выделяет

💡 Совет:
   Используй целевой поиск, если помнишь слово 
   из файла, но не помнишь название.
"""
        
        # Метка с текстом (без фиксированной ширины)
        text_label = tk.Label(main_frame, text=text, 
                              font=("Cascadia Code", 10),
                              fg=COLORS["fg"], bg=COLORS["bg"],
                              justify="left")
        text_label.pack(pady=5)
        
        # Кнопка закрытия
        btn_frame = tk.Frame(main_frame, bg=COLORS["bg"])
        btn_frame.pack(pady=(15, 0))
        
        tk.Button(btn_frame, text="✖ Закрыть", command=help_window.destroy,
                  bg=COLORS["bg_light"], fg=COLORS["fg"],
                  relief="flat", font=("Cascadia Code", 10),
                  cursor="hand2", padx=20, pady=5).pack()
        
        # Обновляем окно, чтобы вычислить размер
        help_window.update_idletasks()
        
        # Получаем размеры текста
        width = text_label.winfo_reqwidth() + 60
        height = text_label.winfo_reqheight() + 120
        
        # Устанавливаем размер окна
        help_window.geometry(f"{width}x{height}")
        
        # Центрируем окно относительно главного
        help_window.transient(self.root)
        help_window.grab_set()
        help_window.focus_set()
        
        # Центрирование
        help_window.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - width) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - height) // 2
        help_window.geometry(f"+{x}+{y}")
    
    def start_move(self, e):
        self.x, self.y = e.x, e.y
    
    def on_move(self, e):
        x = self.root.winfo_x() + e.x - self.x
        y = self.root.winfo_y() + e.y - self.y
        self.root.geometry(f"+{x}+{y}")
    
    def minimize(self):
        self.root.iconify()
    
    def maximize(self):
        if self.root.attributes('-zoomed'):
            self.root.attributes('-zoomed', False)
        else:
            self.root.attributes('-zoomed', True)
    
    def close(self):
        if messagebox.askyesno("Выход", "Закрыть NeoSpace Pro?"):
            self.root.quit()
    
    def toggle_terminal(self):
        if self.terminal_visible:
            self.terminal_frame.pack_forget()
            self.terminal_visible = False
        else:
            self.terminal_frame.pack(fill='both', expand=True, side='right')
            self.terminal_visible = True
            self.add_log("🧠 Терминал активирован")
    
    def execute(self, e=None):
        cmd = self.command_entry.get().strip()
        if not cmd:
            return
        self.add_log(f"👤 {cmd}")
        response = self.ai.execute(cmd)
        for line in response.split('\n'):
            if line.strip():
                self.add_log(f"🤖 {line}")
        self.action_counter.config(text=f"📊 Действий: {len(self.logger.actions)}")
        self.command_entry.delete(0, tk.END)
        self._refresh()
    
    def add_log(self, msg):
        if not hasattr(self, 'log_text'):
            return
        ts = datetime.now().strftime("%H:%M:%S")
        n = int(self.log_text.index('end-1c').split('.')[0]) or 1
        self.log_text.insert('end', f"{n:3d}  {ts}  {msg}\n")
        self.log_text.see('end')
    
    def _refresh(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        path = self.current_path.get()
        if not os.path.exists(path):
            return

        try:
            items = os.listdir(path)
            q = self.search_var.get().strip().lower()

            if q and self.deep_search_var.get():
                # 🎯 ЦЕЛЕВОЙ ПОИСК С ПРОГРЕССОМ
                total = len(items)
                found_files = []
                self.progress_var.set(0)
                self.progress_label.config(text="0%")
                self.root.update_idletasks()

                for i, name in enumerate(items):
                    full = os.path.join(path, name)
                    percent = int((i + 1) / total * 100) if total > 0 else 0
                    self.progress_var.set(percent)
                    self.progress_label.config(text=f"{percent}%")
                    self.root.update_idletasks()

                    if os.path.isfile(full):
                        try:
                            with open(full, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read().lower()
                                if q in content:
                                    found_files.append((name, full))
                        except:
                            pass

                self.progress_var.set(100)
                self.progress_label.config(text="✅ Готово!")
                self.root.update_idletasks()

                filtered = [f[0] for f in found_files]
                self.status.config(text=f"🎯 Найдено: {len(filtered)} файлов")

                # === АВТООТКРЫТИЕ ИЛИ ВЫДЕЛЕНИЕ ===
                if found_files and len(found_files) == 1:
                    name, full_path = found_files[0]
                    if self.auto_open_var.get():
                        try:
                            os.startfile(full_path)
                            self.add_log(f"📂 Автооткрыт: {name}")
                            self.status.config(text=f"✅ Открыт: {name}")
                        except Exception as e:
                            self.add_log(f"⚠️ Ошибка открытия: {e}")
                    else:
                        self.add_log(f"👁️ Найден: {name}")
                        self.status.config(text=f"👁️ Найден: {name}")

                    # Выделяем в списке
                    for item in self.tree.get_children():
                        if self.tree.item(item)['text'].endswith(name):
                            self.tree.selection_set(item)
                            self.tree.focus(item)
                            self.tree.see(item)
                            break

            elif q:
                # Обычный поиск
                filtered = [i for i in items if q in i.lower()]
                self.progress_var.set(0)
                self.progress_label.config(text="0%")
                self.status.config(text=f"🔍 Найдено: {len(filtered)} элементов")
            else:
                filtered = items
                self.progress_var.set(0)
                self.progress_label.config(text="0%")
                self.status.config(text=f"📁 {path} | {len(filtered)} элементов")

            # Отображаем результаты
            for name in sorted(filtered):
                full = os.path.join(path, name)
                is_dir = os.path.isdir(full)
                icon = "📁" if is_dir else "📄"
                size = "" if is_dir else self._format_size(os.path.getsize(full))
                modified = datetime.fromtimestamp(os.path.getmtime(full)).strftime("%d.%m.%Y %H:%M")
                self.tree.insert("", "end", text=f"{icon} {name}", values=(size, modified))

            self.status.config(text=f"📁 {path} | {len(filtered)} элементов")

        except Exception as e:
            self.status.config(text=f"Ошибка: {e}")
    
    def on_drop(self, e):
        path = self.current_path.get()
        if not os.path.exists(path):
            return
        files = e.data.split()
        if not files or not messagebox.askyesno("Подтверждение", f"Скопировать {len(files)} элементов?"):
            return
        count = 0
        for f in files:
            f = f.strip('{}')
            if os.path.exists(f):
                try:
                    dest = os.path.join(path, os.path.basename(f))
                    if os.path.isdir(f):
                        shutil.copytree(f, dest, dirs_exist_ok=True)
                    else:
                        shutil.copy2(f, dest)
                    count += 1
                except Exception as e:
                    self._log(f"⚠️ Ошибка: {e}")
        self._log(f"📥 Перетащено {count} файлов")
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
            messagebox.showinfo("Успех", "Рабочий стол скопирован!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка: {e}")
    
    def _import_folder(self):
        src = filedialog.askdirectory(title="Выберите папку")
        if not src:
            return
        dest = os.path.join(self.current_path.get(), os.path.basename(src))
        if os.path.exists(dest) and not messagebox.askyesno("Подтверждение", "Заменить?"):
            return
        try:
            shutil.copytree(src, dest, dirs_exist_ok=True)
            self._log(f"📥 Импортирована: {src}")
            self._refresh()
            messagebox.showinfo("Успех", "Импортировано!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка: {e}")
    
    def _export_folder(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите папку!")
            return
        item = self.tree.item(selected[0])
        name = item["text"].split(" ", 1)[1]
        src = os.path.join(self.current_path.get(), name)
        if not os.path.isdir(src):
            messagebox.showwarning("Ошибка", "Выберите папку, а не файл!")
            return
        dest = filedialog.askdirectory(title="Куда экспортировать?")
        if not dest:
            return
        try:
            shutil.copytree(src, os.path.join(dest, name), dirs_exist_ok=True)
            self._log(f"📤 Экспортирована: {src}")
            messagebox.showinfo("Успех", f"Экспортировано в:\n{dest}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка: {e}")
    
    def _create_file(self):
        name = simpledialog.askstring("Создать файл", "Имя файла (без расширения):")
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
                f.write(f"Создано: {datetime.now().strftime('%d.%m.%Y %H:%M')}")
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
                backup = os.path.join(self.virtual_path, "Backups", os.path.basename(path) + ".backup")
                if os.path.isdir(path):
                    shutil.copytree(path, backup, dirs_exist_ok=True)
                    shutil.rmtree(path)
                else:
                    shutil.copy2(path, backup)
                    os.remove(path)
                self._log(f"🗑 Удалён: {name}")
                self._refresh()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка: {e}")
    
    def _show_timer(self):
        tw = tk.Toplevel(self.root)
        tw.title("⏱️ Таймер")
        tw.geometry("350x250")
        tw.configure(bg=COLORS["bg"])
        tw.resizable(False, False)
        tk.Label(tw, text="⏱️ Таймер", font=("Cascadia Code", 14, "bold"),
                fg=COLORS["accent"], bg=COLORS["bg"]).pack(pady=10)
        tk.Label(tw, text="Интервал (сек):", bg=COLORS["bg"], fg=COLORS["fg"],
                font=("Cascadia Code", 10)).pack(pady=5)
        entry = tk.Entry(tw, font=("Cascadia Code", 10), bg=COLORS["bg_light"], fg=COLORS["fg"])
        entry.insert(0, "60")
        entry.pack(pady=5)
        tk.Label(tw, text="Действие:", bg=COLORS["bg"], fg=COLORS["fg"],
                font=("Cascadia Code", 10)).pack(pady=5)
        action = tk.StringVar(value="backup")
        for t, v in [("📦 Бэкап", "backup"), ("🧹 Очистка", "clean")]:
            tk.Radiobutton(tw, text=t, variable=action, value=v, bg=COLORS["bg"],
                          fg=COLORS["fg"], selectcolor=COLORS["bg"]).pack()
        def start():
            try:
                interval = int(entry.get())
                if interval < 1:
                    raise ValueError
                self.timer_running = True
                tw.destroy()
                threading.Thread(target=self._timer_loop, args=(interval, action.get()), daemon=True).start()
                messagebox.showinfo("Таймер", f"Запущен! Интервал: {interval} сек.")
            except:
                messagebox.showerror("Ошибка", "Введите число!")
        tk.Button(tw, text="▶️ Запустить", command=start, bg="#4caf50", fg="#ffffff",
                 font=("Cascadia Code", 10, "bold"), relief="flat", cursor="hand2").pack(pady=10)
        tk.Button(tw, text="⏹️ Остановить", command=self._stop_timer, bg="#f44336",
                 fg="#ffffff", font=("Cascadia Code", 10, "bold"), relief="flat", cursor="hand2").pack(pady=5)
    
    def _stop_timer(self):
        self.timer_running = False
        messagebox.showinfo("Таймер", "Остановлен!")
    
    def _timer_loop(self, interval, action):
        while self.timer_running:
            time.sleep(interval)
            if action == "backup":
                self._auto_backup()
            else:
                self._auto_clean()
    
    def _auto_backup(self):
        path = os.path.join(self.virtual_path, "Экспорт", f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        try:
            shutil.copytree(self.virtual_path, path, ignore=shutil.ignore_patterns("Экспорт", "logs.txt"))
            self._log(f"📦 Бэкап: {path}")
        except Exception as e:
            self._log(f"⚠️ Ошибка бэкапа: {e}")
    
    def _auto_clean(self):
        try:
            count = 0
            for item in os.listdir(self.virtual_path):
                if item not in ["Экспорт", "logs.txt", "Backups", "ai_logs.txt"]:
                    path = os.path.join(self.virtual_path, item)
                    if os.path.isdir(path):
                        shutil.rmtree(path)
                    else:
                        os.remove(path)
                    count += 1
            self._log(f"🧹 Очистка: удалено {count} элементов")
            self.root.after(0, self._refresh)
        except Exception as e:
            self._log(f"⚠️ Ошибка очистки: {e}")
    
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
    
    def _open_item(self, e):
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
            self._log(f"📂 Открыта: {path}")
    
    def _format_size(self, size):
        for unit in ['Б', 'КБ', 'МБ', 'ГБ']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} ТБ"

# ===================================================
# ЗАПУСК
# ===================================================
if __name__ == "__main__":
    print("=" * 50)
    print(f"🧠 NEO SPACE PRO v2.3")
    print(f"📂 {PROJECT_ROOT}")
    print("=" * 50)
    
    if not start_ollama():
        print("❌ Ollama не запущен!")
        input("Нажми Enter для выхода...")
        sys.exit(1)
    
    print("🚀 Запуск...")
    root = TkinterDnD.Tk()
    app = NeoSpacePro(root)
    root.mainloop()