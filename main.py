import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import threading
import webbrowser
from pathlib import Path
from typing import Dict, List  # Додано необхідний імпорт

# Імпорт наших модулів
try:
    from universal_parser import UniversalOrderParser
    from modern_exporter import ModernExporter
except ImportError as e:
    messagebox.showerror("Помилка імпорту", f"Не вдалося завантажити модулі: {e}\n\nПереконайтесь, що всі файли в одній папці:")
    exit()

class ModernOrderAnalyzerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("⚡ ЗРОБЛЕНО В УКРАЇНІ!!! ЧИТАЧ ТЕКСТУ by ОгірОК ")
        self.root.geometry("1400x900")
        self.root.configure(bg='#f5f6fa')
        
        # Центрування вікна
        self.center_window()
        
        # Іконка (якщо є)
        try:
            self.root.iconbitmap("icon.ico")  # Можна додати іконку
        except:
            pass
        
        self.parser = UniversalOrderParser()
        self.exporter = ModernExporter()
        self.orders_data = []
        self.processing = False
        
        self.setup_ui()
    
    def center_window(self):
        """Центрування вікна на екрані"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry('{}x{}+{}+{}'.format(width, height, x, y))
    
    def setup_ui(self):
        """Налаштування сучасного інтерфейсу"""
        # Головний контейнер з тінем
        main_container = tk.Frame(self.root, bg='#f5f6fa', padx=20, pady=20)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Заголовок з градієнтом
        header_frame = tk.Frame(main_container, bg='#f5f6fa')
        header_frame.pack(fill=tk.X, pady=(0, 30))
        
        title_label = tk.Label(header_frame, 
                             text="⚡ АНАЛІЗАТОР НАКАЗІВ ЗСУ",
                             font=('Segoe UI', 28, 'bold'),
                             bg='#f5f6fa',
                             fg='#2d3436')
        title_label.pack(pady=(0, 10))
        
        subtitle_label = tk.Label(header_frame,
                                text="Швидкий, стильний та ефективний аналіз документів",
                                font=('Segoe UI', 14),
                                bg='#f5f6fa',
                                fg='#636e72')
        subtitle_label.pack()
        
        # Картка з кнопками управління
        control_card = tk.Frame(main_container, bg='white', relief='flat', bd=1)
        control_card.pack(fill=tk.X, pady=(0, 20))
        
        # Верхня панель керування
        top_control = tk.Frame(control_card, bg='white', padx=20, pady=15)
        top_control.pack(fill=tk.X)
        
        # Основні кнопки
        actions = [
            ("📁 ОБРАТИ ПАПКУ", self.select_folder, '#0984e3'),
            ("🔍 ПОЧАТИ АНАЛІЗ", self.start_analysis, '#00b894'),
            ("⏹️ ЗУПИНИТИ", self.stop_analysis, '#d63031'),
            ("👁️ ПЕРЕГЛЯНУТИ", self.show_details, '#fd79a8')
        ]
        
        for text, command, color in actions:
            btn = tk.Button(top_control, text=text, command=command,
                          font=('Segoe UI', 11, 'bold'),
                          bg=color, fg='white',
                          relief='flat', bd=0,
                          padx=20, pady=12,
                          cursor='hand2')
            btn.pack(side=tk.LEFT, padx=8)
            btn.bind("<Enter>", lambda e, b=btn: b.configure(bg='#2d3436'))
            btn.bind("<Leave>", lambda e, b=btn, c=color: b.configure(bg=c))
        
        # Нижня панель з експортом
        bottom_control = tk.Frame(control_card, bg='#dfe6e9', padx=20, pady=12)
        bottom_control.pack(fill=tk.X)
        
        tk.Label(bottom_control, text="ЕКСПОРТУВАТИ:", 
                font=('Segoe UI', 11, 'bold'),
                bg='#dfe6e9', fg='#2d3436').pack(side=tk.LEFT, padx=(0, 15))
        
        export_options = [
            ("🌐 HTML ЗВІТ", "html"),
            ("📊 JSON ДАНІ", "json"), 
            ("📋 CSV ФАЙЛИ", "csv"),
            ("💼 EXCEL", "excel")
        ]
        
        for text, format_type in export_options:
            btn = tk.Button(bottom_control, text=text,
                          command=lambda ft=format_type: self.export_data(ft),
                          font=('Segoe UI', 10),
                          bg='#636e72', fg='white',
                          relief='flat', padx=15, pady=8,
                          cursor='hand2')
            btn.pack(side=tk.LEFT, padx=5)
            btn.bind("<Enter>", lambda e, b=btn: b.configure(bg='#2d3436'))
            btn.bind("<Leave>", lambda e, b=btn: b.configure(bg='#636e72'))
        
        # Прогрес-бар
        progress_frame = tk.Frame(main_container, bg='#f5f6fa')
        progress_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.progress = ttk.Progressbar(progress_frame, mode='determinate')
        self.progress.pack(fill=tk.X)
        
        # Статус
        self.status_var = tk.StringVar(value="🟢 Оберіть папку з документами для початку роботи")
        status_label = tk.Label(main_container, textvariable=self.status_var,
                              font=('Segoe UI', 11),
                              bg='#f5f6fa', fg='#2d3436',
                              anchor=tk.W)
        status_label.pack(fill=tk.X)
        
        # Основний вміст
        content_frame = tk.Frame(main_container, bg='#f5f6fa')
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Стилізація Notebook
        style = ttk.Style()
        style.configure('Modern.TNotebook', background='#f5f6fa')
        style.configure('Modern.TNotebook.Tab', 
                       font=('Segoe UI', 11, 'bold'),
                       padding=[20, 10])
        
        self.notebook = ttk.Notebook(content_frame, style='Modern.TNotebook')
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Створюємо вкладки
        self.setup_main_tab()
        self.setup_details_tab()
        self.setup_stats_tab()
    
    def setup_main_tab(self):
        """Налаштування основної вкладки"""
        main_tab = ttk.Frame(self.notebook)
        self.notebook.add(main_tab, text="📋 ОСНОВНІ РЕЗУЛЬТАТИ")
        
        # Створюємо Treeview з сіткою
        columns = ('Файл', 'Тип', 'Номер', 'Дата', 'Осіб', 'Статус')
        
        # Frame для Treeview та scrollbar
        tree_frame = ttk.Frame(main_tab)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Treeview
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=20)
        
        # Налаштування колонок
        column_config = {
            'Файл': 250,
            'Тип': 150, 
            'Номер': 100,
            'Дата': 120,
            'Осіб': 80,
            'Статус': 150
        }
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=column_config[col])
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Подвійне клацання
        self.tree.bind('<Double-1>', self.on_double_click)
    
    def setup_details_tab(self):
        """Налаштування вкладки з детальним аналізом"""
        self.details_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.details_tab, text="🔍 ДЕТАЛЬНИЙ АНАЛІЗ")
        
        # Текстове поле
        self.details_text = tk.Text(self.details_tab, wrap=tk.WORD, 
                                  font=('Consolas', 11),
                                  bg='#2d3436', fg='#dfe6e9',
                                  insertbackground='white',
                                  padx=15, pady=15)
        
        scrollbar = ttk.Scrollbar(self.details_tab, orient=tk.VERTICAL, command=self.details_text.yview)
        self.details_text.configure(yscrollcommand=scrollbar.set)
        
        self.details_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def setup_stats_tab(self):
        """Налаштування вкладки зі статистикою"""
        self.stats_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.stats_tab, text="📈 СТАТИСТИКА")
        
        self.stats_text = tk.Text(self.stats_tab, wrap=tk.WORD,
                                font=('Segoe UI', 12),
                                bg='white', fg='#2d3436',
                                padx=20, pady=20)
        
        scrollbar = ttk.Scrollbar(self.stats_tab, orient=tk.VERTICAL, command=self.stats_text.yview)
        self.stats_text.configure(yscrollcommand=scrollbar.set)
        
        self.stats_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def select_folder(self):
        """Вибір папки з документами"""
        folder_path = filedialog.askdirectory(
            title="📁 Оберіть папку з документами",
            mustexist=True
        )
        if folder_path:
            self.folder_path = folder_path
            self.status_var.set(f"📁 Обрана папка: {os.path.basename(folder_path)}")
            self.update_stats()
    
    def start_analysis(self):
        """Запуск аналізу"""
        if not hasattr(self, 'folder_path'):
            messagebox.showwarning("Увага", "📁 Спочатку оберіть папку з документами")
            return
        
        if self.processing:
            messagebox.showwarning("Увага", "⏳ Аналіз вже виконується")
            return
        
        self.processing = True
        self.orders_data = []
        self.tree.delete(*self.tree.get_children())
        
        # Запуск в окремому потоці
        thread = threading.Thread(target=self.analyze_documents)
        thread.daemon = True
        thread.start()
    
    def stop_analysis(self):
        """Зупинка аналізу"""
        self.processing = False
        self.status_var.set("⏹️ Аналіз зупинено")
        self.progress['value'] = 0
    
    def analyze_documents(self):
        """Аналіз документів"""
        try:
            supported_extensions = ('.txt', '.docx', '.pdf', '.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif')
            files = [f for f in os.listdir(self.folder_path) 
                    if f.lower().endswith(supported_extensions)]
            
            if not files:
                self.status_var.set("❌ В обраній папці не знайдено підтримуваних файлів")
                return
            
            total_files = len(files)
            
            for i, filename in enumerate(files):
                if not self.processing:
                    break
                    
                file_path = os.path.join(self.folder_path, filename)
                self.status_var.set(f"🔍 Аналіз {i+1}/{total_files}: {filename}")
                
                # Парсинг документу
                order_data = self.parser.parse_document(file_path)
                self.orders_data.append(order_data)
                
                # Оновлення прогресу
                progress_percent = ((i + 1) / total_files) * 100
                self.progress['value'] = progress_percent
                
                # Додавання в таблицю
                self.add_to_treeview(order_data)
                self.root.update()
            
            if self.processing:
                success_count = len([o for o in self.orders_data if 'error' not in o])
                self.status_var.set(f"✅ Аналіз завершено! Успішно: {success_count}/{total_files}")
                self.update_stats()
                
                messagebox.showinfo("Готово", 
                                  f"🎉 Аналіз завершено успішно!\n\n"
                                  f"📊 Оброблено документів: {total_files}\n"
                                  f"✅ Успішно: {success_count}\n"
                                  f"❌ З помилками: {total_files - success_count}\n\n"
                                  f"Тепер ви можете експортувати результати!")
            else:
                self.status_var.set(f"⏹️ Аналіз зупинено. Оброблено {len(files)} файлів")
            
        except Exception as e:
            messagebox.showerror("Помилка", f"❌ Помилка під час аналізу: {str(e)}")
        finally:
            self.processing = False
            self.progress['value'] = 0
    
    def add_to_treeview(self, order_data: Dict):
        """Додавання даних до таблиці"""
        status = "✅ Успішно" if 'error' not in order_data else f"❌ {order_data['error'][:30]}..."
        personnel_count = len(order_data.get('personnel', []))
        
        self.tree.insert('', 'end', values=(
            order_data['file_name'],
            order_data.get('type', 'невідомо'),
            order_data.get('number', 'н/д'),
            order_data.get('date', 'н/д'),
            personnel_count,
            status
        ))
    
    def on_double_click(self, event):
        """Обробка подвійного клацання"""
        self.show_details()
    
    def show_details(self):
        """Показати детальну інформацію"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Увага", "👆 Оберіть документ з таблиці")
            return
        
        item = self.tree.selection()[0]
        values = self.tree.item(item, 'values')
        file_name = values[0]
        
        # Знаходимо відповідні дані
        order_data = next((o for o in self.orders_data if o['file_name'] == file_name), None)
        
        if not order_data:
            messagebox.showerror("Помилка", "❌ Дані не знайдено")
            return
        
        # Формуємо детальну інформацію
        details = self.format_detailed_info(order_data)
        
        # Оновлюємо текстове поле
        self.details_text.delete(1.0, tk.END)
        self.details_text.insert(1.0, details)
        
        # Переходимо на вкладку деталей
        self.notebook.select(1)
    
    def format_detailed_info(self, order_data: Dict) -> str:
        """Форматування детальної інформації"""
        details = []
        details.append("=" * 80)
        details.append("🔍 ДЕТАЛЬНИЙ АНАЛІЗ ДОКУМЕНТУ")
        details.append("=" * 80)
        details.append(f"📄 Файл: {order_data.get('file_name', 'н/д')}")
        details.append(f"📁 Тип файлу: {order_data.get('file_type', 'н/д')}")
        details.append(f"🔢 Номер наказу: {order_data.get('number', 'н/д')}")
        details.append(f"📅 Дата наказу: {order_data.get('date', 'н/д')}")
        details.append(f"⏰ Час обробки: {order_data.get('processing_time', 'н/д')}")
        details.append("")
        
        if 'error' in order_data:
            details.append("❌ ПОМИЛКА ОБРОБКИ:")
            details.append("-" * 40)
            details.append(f"   {order_data['error']}")
            details.append("")
        
        if 'advanced_data' in order_data and order_data['advanced_data']:
            adv_data = order_data['advanced_data']
            
            details.append("👥 ЗМІНИ ПЕРСОНАЛУ:")
            details.append("-" * 40)
            for change in adv_data.get('personnel_changes', []):
                details.append(f"   📌 Пункт {change.get('point_number', 'н/д')}: {change.get('type', 'н/д')}")
                for person in change.get('personnel_data', []):
                    details.append(f"      👤 {person.get('full_name', 'н/д')}")
                    details.append(f"         🎖️  Звання: {person.get('rank', 'н/д')}")
                    details.append(f"         💼 Посада: {person.get('position', 'н/д')}")
                    if person.get('enrollment_date'):
                        details.append(f"         📅 Дата зарахування: {person.get('enrollment_date')}")
                    if person.get('salary'):
                        details.append(f"         💰 Оклад: {person.get('salary')} грн")
                details.append("")
            
            details.append("💰 ФІНАНСОВІ ОПЕРАЦІЇ:")
            details.append("-" * 40)
            for op in adv_data.get('financial_operations', []):
                details.append(f"   💰 {op.get('description', 'н/д')}")
            if not adv_data.get('financial_operations'):
                details.append("   📝 Фінансових операцій не виявлено")
            details.append("")
        
        return '\n'.join(details)
    
    def update_stats(self):
        """Оновлення статистики"""
        if not self.orders_data:
            stats_text = [
                "📊 СТАТИСТИКА СИСТЕМИ",
                "=" * 50,
                "📁 Документи: ще не аналізовано",
                "👤 Персонал: дані відсутні", 
                "✅ Готовість: очікування документів",
                "",
                "💡 Порада: оберіть папку з документами та натисніть",
                "   кнопку '🔍 ПОЧАТИ АНАЛІЗ'"
            ]
        else:
            total_files = len(self.orders_data)
            successful_files = len([o for o in self.orders_data if 'error' not in o])
            total_personnel = sum(len(o.get('personnel', [])) for o in self.orders_data if 'error' not in o)
            
            stats_text = [
                "📊 СТАТИСТИКА АНАЛІЗУ",
                "=" * 50,
                f"📁 Загальна кількість файлів: {total_files}",
                f"✅ Успішно оброблено: {successful_files}",
                f"❌ З помилками: {total_files - successful_files}",
                f"👥 Всього змін персоналу: {total_personnel}",
                "",
                "📈 РОЗПОДІЛ ЗА ТИПАМИ:",
                "-" * 30
            ]
            
            # Статистика за типами
            order_types = {}
            for order in self.orders_data:
                if 'error' not in order:
                    order_type = order.get('type', 'невідомо')
                    order_types[order_type] = order_types.get(order_type, 0) + 1
            
            for otype, count in order_types.items():
                stats_text.append(f"   {otype}: {count}")
        
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(1.0, '\n'.join(stats_text))
    
    def export_data(self, format_type: str):
        """Експорт даних"""
        if not self.orders_data:
            messagebox.showwarning("Увага", "📊 Немає даних для експорту")
            return
        
        try:
            # Визначення типів файлів
            file_types = {
                'html': [("HTML файли", "*.html")],
                'json': [("JSON файли", "*.json")],
                'csv': [("CSV файли", "*.csv")],
                'excel': [("Excel файли", "*.xlsx")]
            }
            
            default_ext = {
                'html': '.html',
                'json': '.json', 
                'csv': '.csv',
                'excel': '.xlsx'
            }
            
            # Діалог збереження
            file_path = filedialog.asksaveasfilename(
                defaultextension=default_ext[format_type],
                filetypes=file_types[format_type],
                title=f"💾 Зберегти як {format_type.upper()}"
            )
            
            if file_path:
                self.status_var.set(f"📤 Експорт у {format_type.upper()}...")
                
                # Виконуємо експорт
                self.exporter.export_data(self.orders_data, file_path, format_type)
                
                self.status_var.set(f"✅ Експорт завершено: {os.path.basename(file_path)}")
                
                # Для HTML - пропонуємо відкрити
                if format_type == 'html':
                    if messagebox.askyesno("Відкрити звіт", 
                                         "🌐 Бажаєте відкрити створений HTML звіт у браузері?"):
                        webbrowser.open(f'file://{os.path.abspath(file_path)}')
                
                messagebox.showinfo("Успішно", 
                                  f"✅ Дані успішно експортовані!\n\n"
                                  f"📁 Формат: {format_type.upper()}\n"
                                  f"📊 Файл: {os.path.basename(file_path)}\n"
                                  f"📍 Шлях: {file_path}")
                
        except Exception as e:
            messagebox.showerror("Помилка експорту", f"❌ Не вдалося експортувати дані:\n{str(e)}")

def main():
    """Головна функція"""
    try:
        root = tk.Tk()
        app = ModernOrderAnalyzerApp(root)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("Критична помилка", 
                           f"Не вдалося запустити програму:\n{str(e)}\n\n"
                           f"Переконайтесь, що всі необхідні файли знаходяться в одній папці.")

if __name__ == "__main__":
    main()
