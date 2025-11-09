import sys
import subprocess

def install_required_packages():
    """Автоматическая установка необходимых пакетов"""
    required_packages = {
        'streamlit': 'streamlit',
        'pandas': 'pandas', 
        'python-docx': 'python-docx',
        'PyPDF2': 'PyPDF2',
        'openpyxl': 'openpyxl'
    }
    
    missing_packages = []
    for package, pip_name in required_packages.items():
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(pip_name)
    
    if missing_packages:
        print("Встановлення відсутніх бібліотек...")
        for package in missing_packages:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                print(f"✓ Встановлено {package}")
            except subprocess.CalledProcessError:
                print(f"✗ Помилка встановлення {package}")
                return False
    return True

# Проверяем и устанавливаем зависимости
if not install_required_packages():
    print("Не вдалося встановити всі бібліотеки. Будь ласка, встановіть їх вручну:")
    print("pip install streamlit pandas python-docx PyPDF2 openpyxl")
    sys.exit(1)

# Импортируем библиотеки после проверки
import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
import re
import io

# Остальной код приложения остается без изменений...
# [здесь вставляется весь остальной код из предыдущего исправленного варианта]

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