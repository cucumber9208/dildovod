import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
import re
import io

# Конфигурация страницы
st.set_page_config(
    page_title="Діловод ЗСУ - Система обліку наказів",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

class TemplateManager:
    """Менеджер для работы с шаблонами документов"""
    
    def __init__(self):
        self.templates = self._load_templates()
    
    def _load_templates(self):
        """Загрузка шаблонов документов"""
        try:
            templates = {
                "personnel": {
                    "name": "📋 Кадрові накази",
                    "templates": {
                        "3.1": {
                            "name": "Прибуття до частини (з часом для прийому справ)",
                            "template": """НАКАЗ
                            
По особовому складу

{дата} {номер}

ПРИБУТИ ДО ЧАСТИНИ:

1. {звання} {ПІБ} - для прийому справ та обов'язків {посада}.

Час для прийому справ - {кількість} діб.

Підстава: {підстава}

{підпис}

{дата_підпис}"""
                        },
                        "3.2": {
                            "name": "Прибуття до частини (одразу на роботу)", 
                            "template": """НАКАЗ
                            
По особовому складу

{дата} {номер}

ПРИБУТИ ДО ЧАСТИНИ:

1. {звання} {ПІБ} - до розпорядження {посада}.

Приступити до виконання обов'язків одразу.

Підстава: {підстава}

{підпис}

{дата_підпис}"""
                        },
                        "2.2": {
                            "name": "Вибування з частини (переведення)",
                            "template": """НАКАЗ
                            
По особовому складу

{дата} {номер}

ВИБУТИ З ЧАСТИНИ:

1. {звання} {ПІБ} - у зв'язку з переведенням до {нова_частина}.

Посада: {посада}

Підстава: {підстава}

{підпис}

{дата_підпис}"""
                        }
                    }
                },
                "service": {
                    "name": "🎖️ Строкова служба",
                    "templates": {
                        "10": {
                            "name": "Зарахування призваних з ТЦК",
                            "template": """НАКАЗ
                            
По особовому складу

{дата} {номер}

ЗАРАХУВАТИ:

1. {звання} {ПІБ} - до списку особового складу частини.

Призначити на посаду: {посада}.

Підстава: Повідомлення ТЦК {номер_тцк} від {дата_тцк}

{підпис}

{дата_підпис}"""
                        },
                        "7": {
                            "name": "Призначення/звільнення від посади",
                            "template": """НАКАЗ
                            
По особовому складу

{дата} {номер}

ПРИЗНАЧИТИ:

1. {звання} {ПІБ} - на посаду {посада}.

Звільнити від виконання обов'язків за посадою {попередня_посада}.

Підстава: {підстава}

{підпис}

{дата_підпис}"""
                        }
                    }
                },
                "leave": {
                    "name": "✈️ Відрядження та відпустки",
                    "templates": {
                        "24.1": {
                            "name": "Відрядження",
                            "template": """НАКАЗ
                            
По особовому складу

{дата} {номер}

ВІДРЯДИТИ:

1. {звання} {ПІБ} - у службове відрядження до {місце_відрядження}.

Термін: з {дата_початку} по {дата_закінчення}.

Мета відрядження: {мета}.

Підстава: {підстава}

{підпис}

{дата_підпис}"""
                        },
                        "24.3": {
                            "name": "Відпустка",
                            "template": """НАКАЗ
                            
По особовому складу

{дата} {номер}

НАДАТИ ВІДПУСТКУ:

1. {звання} {ПІБ} - {тип_відпустки} відпустку.

Термін: з {дата_початку} по {дата_закінчення}.

Тривалість: {кількість} діб.

Підстава: {підстава}

{підпис}

{дата_підпис}"""
                        }
                    }
                }
            }
            return templates
        except Exception as e:
            st.error(f"Помилка завантаження шаблонів: {e}")
            return {}

class OrderGenerator:
    """Генератор документов на основе шаблонов"""
    
    def __init__(self, template_manager):
        self.tm = template_manager
    
    def search_templates(self, query):
        """Поиск шаблонов по запросу"""
        try:
            results = []
            if not query or not query.strip():
                return results
                
            query = query.lower().strip()
            
            for category, cat_data in self.tm.templates.items():
                for code, template in cat_data["templates"].items():
                    search_text = f"{template['name']} {cat_data['name']} {code}".lower()
                    if query in search_text:
                        results.append({
                            "category": cat_data["name"],
                            "code": code,
                            "name": template["name"],
                            "template": template["template"]
                        })
            return results
        except Exception as e:
            st.error(f"Помилка пошуку: {e}")
            return []
    
    def generate_order(self, template_code, variables):
        """Генерация документа из шаблона"""
        try:
            template_text = None
            template_name = ""
            
            # Поиск шаблона по коду
            for cat_data in self.tm.templates.values():
                if template_code in cat_data["templates"]:
                    template_text = cat_data["templates"][template_code]["template"]
                    template_name = cat_data["templates"][template_code]["name"]
                    break
            
            if not template_text:
                return None, "Шаблон не знайдено"
            
            # Замена переменных в шаблоне
            generated_text = template_text
            for key, value in variables.items():
                if value:  # Заменяем только если значение не пустое
                    placeholder = "{" + key + "}"
                    generated_text = generated_text.replace(placeholder, str(value))
            
            # Удаление оставшихся незаполненных переменных
            generated_text = re.sub(r'\{[^}]+\}', '', generated_text)
            
            return generated_text, template_name
        except Exception as e:
            return None, f"Помилка генерації: {e}"
    
    def extract_variables(self, template_text):
        """Извлечение переменных из шаблона"""
        try:
            # Исправленное регулярное выражение для украинского текста
            variables = re.findall(r'\{([^{}]+)\}', template_text)
            return list(set(variables))  # Убираем дубликаты
        except Exception as e:
            st.error(f"Помилка аналізу шаблону: {e}")
            return []

def initialize_session_state():
    """Инициализация состояния сессии"""
    default_state = {
        'selected_template': None,
        'generated_order': None,
        'form_data': {},
        'last_action': None
    }
    
    for key, value in default_state.items():
        if key not in st.session_state:
            st.session_state[key] = value

def handle_template_selection(template):
    """Обработка выбора шаблона"""
    st.session_state.selected_template = template
    st.session_state.generated_order = None
    st.session_state.form_data = {}
    st.session_state.last_action = "template_selected"

def handle_generation(form_data, order_generator):
    """Обработка генерации документа"""
    if all(form_data.values()):
        generated_text, template_name = order_generator.generate_order(
            st.session_state.selected_template["code"], 
            form_data
        )
        
        if generated_text:
            st.session_state.generated_order = generated_text
            st.session_state.form_data = form_data
            st.session_state.last_action = "document_generated"
            return True
    return False

def handle_form_clear():
    """Очистка формы"""
    st.session_state.form_data = {}
    st.session_state.generated_order = None
    st.session_state.last_action = "form_cleared"

def handle_new_document():
    """Создание нового документа"""
    st.session_state.selected_template = None
    st.session_state.generated_order = None
    st.session_state.form_data = {}
    st.session_state.last_action = "new_document"

def render_sidebar(template_manager, order_generator):
    """Отрисовка боковой панели"""
    with st.sidebar:
        st.header("📋 Навігація")
        
        # Категории документов
        categories = {
            "👥 Кадри (Особовий склад)": "personnel",
            "🎖️ Строкова служба": "service", 
            "✈️ Відрядження та відпустки": "leave",
            "💰 Фінанси та виплати": "finance",
            "👨‍💼 Цивільний персонал": "civilian",
            "📊 Інше важливе": "other"
        }
        
        selected_category = st.selectbox(
            "Оберіть категорію:",
            list(categories.keys())
        )
        
        st.markdown("---")
        st.header("🔍 Пошук шаблонів")
        search_query = st.text_input("Введіть ключові слова:", key="search_input")
        
        # Быстрый поиск по ситуациям
        st.markdown("### 🗂️ Швидкий пошук за ситуаціями")
        quick_actions = [
            "Прибуття до частини",
            "Вибування з частини", 
            "Відрядження",
            "Відпустка",
            "Призначення на посаду",
            "Звільнення"
        ]
        
        for action in quick_actions:
            if st.button(f"🔍 {action}", key=f"quick_{action}"):
                results = order_generator.search_templates(action)
                if results:
                    handle_template_selection(results[0])
        
        st.markdown("---")
        st.info("""
        **Інструкція:**
        1. Оберіть категорію або знайдіть шаблон
        2. Заповніть необхідні поля
        3. Згенеруйте та завантажте документ
        """)
        
        return categories[selected_category]

def render_template_list(category_key, template_manager):
    """Отрисовка списка шаблонов"""
    st.header("📁 Доступні шаблони")
    
    category_data = template_manager.templates.get(category_key, {})
    
    if category_data:
        st.subheader(category_data["name"])
        
        for code, template_info in category_data.get("templates", {}).items():
            with st.expander(f"**{code}**: {template_info['name']}"):
                st.markdown("**Шаблон:**")
                template_preview = template_info["template"]
                if len(template_preview) > 300:
                    template_preview = template_preview[:300] + "..."
                st.text(template_preview)
                
                if st.button("Використати цей шаблон", key=f"use_{code}"):
                    handle_template_selection({
                        "code": code,
                        "name": template_info["name"],
                        "template": template_info["template"]
                    })
    else:
        st.info("Шаблони для обраної категорії ще не додані")

def render_search_results(search_query, order_generator):
    """Отрисовка результатов поиска"""
    if search_query and search_query.strip():
        st.subheader("🔍 Результати пошуку")
        search_results = order_generator.search_templates(search_query)
        
        if search_results:
            for result in search_results:
                with st.expander(f"**{result['code']}**: {result['name']} ({result['category']})"):
                    template_preview = result["template"]
                    if len(template_preview) > 200:
                        template_preview = template_preview[:200] + "..."
                    st.text(template_preview)
                    if st.button("Вибрати", key=f"select_{result['code']}"):
                        handle_template_selection(result)
        elif search_query.strip():
            st.warning("Шаблонів за вашим запитом не знайдено")

def render_generation_section(order_generator):
    """Отрисовка секции генерации документа"""
    st.header("📝 Генерація документа")
    
    if not st.session_state.selected_template:
        st.info("👈 Оберіть шаблон зліва для початку роботи")
        render_quick_start(order_generator)
        return
    
    template = st.session_state.selected_template
    
    st.subheader(f"Шаблон: {template['name']}")
    st.success(f"Код шаблону: {template['code']}")
    
    # Анализ переменных в шаблоне
    variables = order_generator.extract_variables(template["template"])
    
    if not variables:
        st.info("Цей шаблон не містить змінних для заповнення")
        return
    
    st.subheader("Заповніть необхідні дані:")
    
    # Форма для ввода данных
    form_data = {}
    for var in variables:
        placeholder = ""
        if "дата" in var.lower():
            placeholder = "РРРР-ММ-ДД"
        elif "піб" in var.lower():
            placeholder = "Прізвище Ім'я По-батькові"
        
        form_data[var] = st.text_input(
            f"**{var.replace('_', ' ').title()}**:",
            value=st.session_state.form_data.get(var, ""),
            placeholder=placeholder,
            key=f"input_{var}"
        )
    
    # Кнопки действий
    col_btn1, col_btn2 = st.columns(2)
    
    with col_btn1:
        if st.button("🔄 Згенерувати документ", type="primary"):
            if handle_generation(form_data, order_generator):
                st.success("Документ успішно згенеровано!")
    
    with col_btn2:
        if st.button("❌ Очистити форму"):
            handle_form_clear()
    
    # Показ сгенерированного документа
    if st.session_state.generated_order:
        render_generated_document()

def render_generated_document():
    """Отрисовка сгенерированного документа"""
    st.subheader("📄 Згенерований документ:")
    st.text_area(
        "Результат:",
        st.session_state.generated_order,
        height=400,
        key="generated_document_display"
    )
    
    # Кнопки экспорта
    st.subheader("📤 Експорт документа")
    col_exp1, col_exp2, col_exp3 = st.columns(3)
    
    with col_exp1:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        st.download_button(
            "💾 Завантажити TXT",
            st.session_state.generated_order,
            file_name=f"наказ_{timestamp}.txt",
            mime="text/plain"
        )
    
    with col_exp2:
        st.download_button(
            "📋 Завантажити копію",
            st.session_state.generated_order,
            file_name=f"наказ_{timestamp}_copy.txt",
            mime="text/plain"
        )
    
    with col_exp3:
        if st.button("🆕 Новий документ"):
            handle_new_document()

def render_quick_start(order_generator):
    """Отрисовка быстрого старта"""
    st.subheader("🚀 Швидкий старт")
    popular_templates = [
        {"code": "3.1", "name": "Прибуття до частини"},
        {"code": "2.2", "name": "Вибування з частини"},
        {"code": "24.1", "name": "Відрядження"},
        {"code": "10", "name": "Зарахування з ТЦК"}
    ]
    
    for temp in popular_templates:
        if st.button(f"📄 {temp['name']} ({temp['code']})", key=f"pop_{temp['code']}"):
            # Поиск полного шаблона
            for category, cat_data in order_generator.tm.templates.items():
                if temp["code"] in cat_data["templates"]:
                    handle_template_selection({
                        "code": temp["code"],
                        "name": cat_data["templates"][temp["code"]]["name"],
                        "template": cat_data["templates"][temp["code"]]["template"]
                    })
                    break

def main():
    # Инициализация состояния
    initialize_session_state()
    
    # Инициализация менеджеров
    template_manager = TemplateManager()
    order_generator = OrderGenerator(template_manager)
    
    st.title("🎯 Діловод ЗСУ - Система обліку наказів")
    st.markdown("### Швидкий пошук та генерація наказів")
    
    # Боковая панель
    selected_category_key = render_sidebar(template_manager, order_generator)
    
    # Основной контент
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Список шаблонов
        render_template_list(selected_category_key, template_manager)
        
        # Результаты поиска
        search_query = st.session_state.get('search_input', '')
        render_search_results(search_query, order_generator)
    
    with col2:
        # Генерация документа
        render_generation_section(order_generator)

if __name__ == "__main__":
    main()