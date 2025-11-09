import re
import os
from datetime import datetime
from typing import Dict, List, Optional, Union
import json
from docx import Document
import PyPDF2
import pandas as pd

# Спроба імпорту бібліотек для OCR
try:
    import pytesseract
    from PIL import Image, ImageEnhance, ImageFilter
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    print("Увага: бібліотеки для OCR не встановлені. Функція розпізнавання текстів з фото буде недоступна.")

class UniversalOrderParser:
    def __init__(self):
        self.load_patterns()
        self.advanced_parser = AdvancedOrderParser()
        
    def load_patterns(self):
        """Завантаження шаблонів для розпізнавання"""
        try:
            with open('patterns.json', 'r', encoding='utf-8') as f:
                self.patterns = json.load(f)
        except FileNotFoundError:
            self.patterns = self.get_default_patterns()
    
    def get_default_patterns(self):
        """Стандартні шаблони для розпізнавання"""
        return {
            "order_types": {
                "personnel": ["по особовому складу", "особовий склад"],
                "service": ["по стройовій частині", "стройова частина"],
                "main": ["з основної діяльності", "основна діяльність"]
            },
            "ranks": [
                "солдат", "рядовий", "єфрейтор", "молодший сержант", "сержант",
                "старший сержант", "головний сержант", "штаб-сержант", "майстер-сержант",
                "молодший лейтенант", "лейтенант", "старший лейтенант", "капітан",
                "майор", "підполковник", "полковник", "бригадний генерал",
                "генерал-майор", "генерал-лейтенант", "генерал",
                "солдат запасу", "рядовий запасу"
            ],
            "actions": {
                "призначення": ["призначити", "призначається", "призначен", "ПРИЗНАЧИТИ"],
                "звільнення": ["звільнити", "звільняється", "звільнен", "ЗВІЛЬНИТИ"],
                "відрядження": ["відрядити", "відряджається", "відряджен", "ВІДРЯДИТИ"],
                "відпустка": ["відпустку", "відпустці", "відпустка", "ВІДПУСТКА"],
                "присвоєння звання": ["присвоїти", "ПРИСВОЇТИ"],
                "виключення": ["виключити", "ВИКЛЮЧИТИ"],
                "зарахування": ["зарахувати", "ЗАРАХУВАТИ"],
                "призов": ["призвати", "призов", "ПРИЗВАТИ"],
                "переведення": ["перевести", "переведення", "ПЕРЕВЕСТИ"]
            },
            "military_units": [
                r'[А-Я]\d{4}',
                r'в/\u0447 \d+',
                r'військова частина \d+'
            ]
        }
    
    def read_file(self, file_path: str) -> str:
        """Універсальне читання файлів всіх підтримуваних форматів"""
        file_ext = os.path.splitext(file_path)[1].lower()
        
        try:
            if file_ext == '.txt':
                return self._read_text_file(file_path)
            elif file_ext == '.docx':
                return self._read_docx_file(file_path)
            elif file_ext == '.pdf':
                return self._read_pdf_file(file_path)
            elif file_ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif']:
                return self._read_image_file(file_path)
            else:
                raise ValueError(f"Непідтримуваний формат файлу: {file_ext}")
        except Exception as e:
            raise Exception(f"Помилка читання файлу {file_path}: {str(e)}")
    
    def _read_text_file(self, file_path: str) -> str:
        """Читання текстових файлів"""
        encodings = ['utf-8', 'windows-1251', 'cp1251', 'iso-8859-1']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue
        
        # Якщо жодна кодування не підійшла, спробуємо latin-1 з заміною помилок
        with open(file_path, 'r', encoding='latin-1', errors='replace') as f:
            return f.read()
    
    def _read_docx_file(self, file_path: str) -> str:
        """Читання DOCX файлів"""
        doc = Document(file_path)
        return '\n'.join([paragraph.text for paragraph in doc.paragraphs])
    
    def _read_pdf_file(self, file_path: str) -> str:
        """Читання PDF файлів"""
        with open(file_path, 'rb') as f:
            pdf_reader = PyPDF2.PdfReader(f)
            text = ''
            for page in pdf_reader.pages:
                text += page.extract_text()
            return text
    
    def _read_image_file(self, file_path: str) -> str:
        """Читання текстів з зображень за допомогою OCR"""
        if not OCR_AVAILABLE:
            raise ImportError("Бібліотеки для OCR не встановлені. Встановіть: pip install pytesseract pillow")
        
        try:
            # Відкриваємо та обробляємо зображення
            image = Image.open(file_path)
            
            # Попередня обробка зображення для покращення розпізнавання
            processed_image = self._preprocess_image(image)
            
            # Конфігурація для української мови
            custom_config = r'--oem 3 --psm 6 -l ukr+eng'
            
            # Виконуємо OCR
            text = pytesseract.image_to_string(processed_image, config=custom_config)
            
            return text
            
        except Exception as e:
            raise Exception(f"Помилка OCR обробки зображення: {str(e)}")
    
    def _preprocess_image(self, image: Image.Image) -> Image.Image:
        """Попередня обробка зображення для покращення якості OCR"""
        # Конвертуємо в сірий
        if image.mode != 'L':
            image = image.convert('L')
        
        # Підвищуємо контраст
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(2.0)
        
        # Підвищуємо різкість
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(2.0)
        
        # Застосовуємо фільтр для покращення тексту
        image = image.filter(ImageFilter.SHARPEN)
        
        return image
    
    def parse_document(self, file_path: str) -> Dict:
        """Універсальний метод парсингу документів"""
        try:
            # Читаємо файл
            text = self.read_file(file_path)
            text = self.clean_text(text)
            
            # Використовуємо розширений парсер для детального аналізу
            advanced_data = self.advanced_parser.parse_advanced_order(text)
            
            # Формуємо результат
            result = {
                'file_name': os.path.basename(file_path),
                'file_type': os.path.splitext(file_path)[1].lower(),
                'file_size': os.path.getsize(file_path),
                'type': self.detect_order_type(text),
                'number': self.extract_order_number(text),
                'date': self.extract_date(text),
                'personnel': [],
                'raw_text': text[:1000],  # Зберігаємо більше тексту для аналізу
                'advanced_data': advanced_data,
                'processing_time': datetime.now().isoformat()
            }
            
            # Конвертуємо розширені дані про персонал
            if 'personnel_changes' in advanced_data:
                for change in advanced_data['personnel_changes']:
                    for person in change.get('personnel_data', []):
                        result['personnel'].append({
                            'action': change.get('type', 'інша дія'),
                            'full_name': person.get('full_name', ''),
                            'rank': person.get('rank', ''),
                            'position': person.get('position', ''),
                            'original_text': change.get('content', '')[:200]
                        })
                
            return result
            
        except Exception as e:
            return {
                'file_name': os.path.basename(file_path),
                'error': str(e),
                'personnel': [],
                'advanced_data': {},
                'processing_time': datetime.now().isoformat()
            }
    
    def clean_text(self, text: str) -> str:
        """Очищення тексту від зайвих пробілів та артефактів"""
        # Заміна multiple пробілів на один
        text = re.sub(r'\s+', ' ', text)
        # Видалення спеціальних символів, що можуть виникнути при OCR
        text = re.sub(r'[^\w\sА-ЯІЇЄа-яіїєґҐ.,;:!?()\-—№\'"]', ' ', text)
        return text.strip()
    
    def detect_order_type(self, text: str) -> str:
        """Визначення типу наказу"""
        text_lower = text.lower()
        for order_type, keywords in self.patterns['order_types'].items():
            for keyword in keywords:
                if keyword in text_lower:
                    return order_type
        return 'невідомо'
    
    def extract_order_number(self, text: str) -> Optional[str]:
        """Витягнення номера наказу"""
        patterns = [
            r'№\s*(\d+)',
            r'Наказ.*?№\s*(\d+)',
            r'НАКАЗ.*?№\s*(\d+)'
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        return None
    
    def extract_date(self, text: str) -> Optional[str]:
        """Витягнення дати"""
        date_patterns = [
            r'\b(\d{1,2}\.\d{1,2}\.\d{4})\b',
            r'\b(\d{1,2}\s+[сС]ічня|[лЛ]ютого|[бБ]ерезня|[кК]вітня|[тТ]равня|[чЧ]ервня|[лЛ]ипня|[сС]ерпня|[вВ]ересня|[жЖ]овтня|[лЛ]истопада|[гГ]рудня)\s+(\d{4})'
        ]
        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match:
                if len(match.groups()) == 1:
                    return match.group(1)
                else:
                    return f"{match.group(1)} {match.group(2)}"
        return None

# Клас AdvancedOrderParser залишається таким самим, як у попередній версії
class AdvancedOrderParser:
    # ... (код з попередньої версії без змін)
    def __init__(self):
        self.patterns = {
            'order_types': {
                'personnel': 'по особовому складу',
                'service': 'по стройовій частині', 
                'main': 'з основної діяльності'
            },
            'actions': {
                'призначення': ['призначити', 'призначається', 'ПРИЗНАЧИТИ'],
                'звільнення': ['звільнити', 'звільняється', 'ЗВІЛЬНИТИ'],
                'відрядження': ['відрядити', 'відряджається', 'ВІДРЯДИТИ'],
                'відпустка': ['відпустку', 'відпустці', 'ВІДПУСТКА'],
                'присвоєння звання': ['присвоїти', 'ПРИСВОЇТИ'],
                'виключення': ['виключити', 'ВИКЛЮЧИТИ'],
                'зарахування': ['зарахувати', 'ЗАРАХУВАТИ'],
                'призов': ['призвати', 'призов', 'ПРИЗВАТИ']
            },
            'ranks': [
                'солдат', 'рядовий', 'єфрейтор', 'молодший сержант', 'сержант',
                'старший сержант', 'головний сержант', 'штаб-сержант', 'майстер-сержант',
                'молодший лейтенант', 'лейтенант', 'старший лейтенант', 'капітан',
                'майор', 'підполковник', 'полковник', 'бригадний генерал',
                'генерал-майор', 'генерал-лейтенант', 'генерал',
                'солдат запасу'
            ]
        }
    
    def parse_advanced_order(self, text: str) -> Dict:
        """Розширений парсинг наказу"""
        result = {
            'order_type': self.detect_order_type(text),
            'order_number': self.extract_order_number(text),
            'order_date': self.extract_date(text),
            'military_unit': self.extract_military_unit(text),
            'personnel_changes': [],
            'financial_operations': [],
            'document_operations': [],
            'structural_changes': [],
            'additional_info': {}
        }
        
        # Спеціальна обробка для витягів з наказів
        if 'В И Т Я Г І З Н А К А З У' in text or 'ВИТЯГ ІЗ НАКАЗУ' in text:
            result['is_extract'] = True
            result['order_type'] = 'service'
        
        # Аналіз різних типів пунктів
        result['personnel_changes'] = self.extract_personnel_changes(text)
        result['financial_operations'] = self.extract_financial_operations(text)
        result['document_operations'] = self.extract_document_operations(text)
        result['structural_changes'] = self.extract_structural_changes(text)
        result['additional_info'] = self.extract_additional_info(text)
        
        return result
    
    def extract_personnel_changes(self, text: str) -> List[Dict]:
        """Витягнення змін особового складу"""
        changes = []
        
        # Спеціальна обробка для документів типу витягу
        if 'В И Т Я Г І З Н А К А З У' in text:
            return self.extract_extract_personnel(text)
        
        # Знаходження призначень за номерованими пунктами
        appointments = re.findall(r'(\d+\.)\s*([А-ЯІЇЄ][а-яіїє]+\s+[А-ЯІЇЄ][а-яіїє]+\s+[А-ЯІЇЄ][а-яіїє]+.*?)(?=\d+\.|Підстава|$)', text, re.DOTALL)
        
        for num, content in appointments:
            change = {
                'type': self.detect_person_action(content),
                'point_number': num.strip('.'),
                'personnel_data': self.extract_personnel_from_text(content),
                'content': content.strip()
            }
            changes.append(change)
        
        return changes
    
    def extract_extract_personnel(self, text: str) -> List[Dict]:
        """Спеціальна обробка для витягів з наказів"""
        changes = []
        
        # Шукаємо пункти у витягах (формат "2. Текст пункту")
        points = re.findall(r'(\d+\.)\s*(.*?)(?=\d+\.|Командир|Підстава|$)', text, re.DOTALL)
        
        for num, content in points:
            if not content.strip():
                continue
                
            change = {
                'type': self.detect_person_action(content),
                'point_number': num.strip('.'),
                'personnel_data': self.extract_personnel_from_text(content),
                'content': content.strip()
            }
            
            # Додаткова обробка для призову на службу
            if 'призвати на військову службу' in content.lower():
                change['type'] = 'призов'
                person_data = self.extract_mobilization_data(content)
                if person_data:
                    change['personnel_data'] = [person_data]
            
            changes.append(change)
        
        return changes
    
    def extract_mobilization_data(self, text: str) -> Dict:
        """Витягнення даних про мобілізацію"""
        # Пошук ПІБ у форматі "звання ПРІЗВИЩЕ Ім'я По-батькові"
        name_match = re.search(r'([А-ЯІЇЄ][а-яіїє]+\s+запасу)\s+([А-ЯІЇЄ]{2,})\s+([А-ЯІЇЄ][а-яіїє]+)\s+([А-ЯІЇЄ][а-яіїє]+)', text)
        
        if name_match:
            rank = name_match.group(1)
            last_name = name_match.group(2)
            first_name = name_match.group(3)
            middle_name = name_match.group(4)
            full_name = f"{last_name} {first_name} {middle_name}"
            
            # Пошук посади
            position_match = re.search(r'призначити на посаду\s*([^\.]+)', text, re.IGNORECASE)
            position = position_match.group(1).strip() if position_match else None
            
            # Пошук дати зарахування
            date_match = re.search(r'З\s*["]?(\d{1,2})["]?\s*([а-яіїє]+)\s*(\d{4})', text, re.IGNORECASE)
            enrollment_date = f"{date_match.group(1)} {date_match.group(2)} {date_match.group(3)}" if date_match else None
            
            # Пошук окладу
            salary_match = re.search(r'посадовий оклад\s*[—\-]\s*(\d+)\s*грн', text, re.IGNORECASE)
            salary = salary_match.group(1) if salary_match else None
            
            return {
                'full_name': full_name,
                'rank': rank,
                'position': position,
                'enrollment_date': enrollment_date,
                'salary': salary,
                'action': 'призов'
            }
        
        return {}
    
    def extract_personnel_from_text(self, text: str) -> List[Dict]:
        """Витягнення даних про персонал з тексту"""
        personnel = []
        
        # Пошук ПІБ у форматі "звання Прізвище Ім'я По-батькові"
        name_pattern = r'([А-ЯІЇЄ][а-яіїє]+\s+[А-ЯІЇЄ][а-яіїє]+\s+[А-ЯІЇЄ][а-яіїє]+\s+[А-ЯІЇЄ][а-яіїє]+)'
        matches = re.findall(name_pattern, text)
        
        for match in matches:
            person_data = {
                'full_name': match,
                'rank': self.extract_rank_from_text(match),
                'position': self.extract_position_from_context(text, match),
                'action': self.detect_person_action(text)
            }
            personnel.append(person_data)
        
        return personnel
    
    def extract_financial_operations(self, text: str) -> List[Dict]:
        """Витягнення фінансових операцій"""
        operations = []
        
        # Патерни для фінансових виплат
        payment_patterns = [
            r'Виплачувати.*?(\d+).*?%',
            r'виплатити.*?(\d+).*?грн',
            r'надбавку.*?(\d+).*?%',
            r'премію.*?(\d+).*?%'
        ]
        
        for pattern in payment_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                operation = {
                    'type': 'фінансова_виплата',
                    'description': match.group(0),
                    'amount': match.group(1) if match.groups() else None
                }
                operations.append(operation)
        
        return operations
    
    def extract_document_operations(self, text: str) -> List[Dict]:
        """Витягнення операцій з документами"""
        operations = []
        
        doc_patterns = {
            'access_termination': r'Припинити доступ.*?таємницю',
            'vacation': r'відпустк[ауі].*?(\d+).*?діб',
            'business_trip': r'відрядженн[яю].*?(\d+).*?діб'
        }
        
        for op_type, pattern in doc_patterns.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                operation = {
                    'type': op_type,
                    'description': match.group(0),
                    'duration': match.group(1) if match.groups() else None
                }
                operations.append(operation)
        
        return operations
    
    def extract_structural_changes(self, text: str) -> List[Dict]:
        """Витягнення структурних змін"""
        changes = []
        
        structure_patterns = [
            r'штат.*?№\s*(\d+[/\d]*)',
            r'військову частину.*?вважати.*?розформованою',
            r'ввести в дію штат'
        ]
        
        for pattern in structure_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                change = {
                    'type': 'структурна_зміна',
                    'description': match.group(0),
                    'details': match.group(1) if match.groups() else None
                }
                changes.append(change)
        
        return changes
    
    def extract_additional_info(self, text: str) -> Dict:
        """Витягнення додаткової інформації"""
        info = {}
        
        # Пошук дати народження
        birth_match = re.search(r'(\d{2}\.\d{2}\.\d{4})\s*р\.н\.', text)
        if birth_match:
            info['birth_date'] = birth_match.group(1)
        
        # Пошук національності
        nationality_match = re.search(r'р\.н\.[^,]*,\s*([^,]+),', text)
        if nationality_match:
            info['nationality'] = nationality_match.group(1).strip()
        
        # Пошук освіти
        education_match = re.search(r'освіта\s*[—\-]\s*([^,\.]+)', text, re.IGNORECASE)
        if education_match:
            info['education'] = education_match.group(1).strip()
        
        # Пошук ідентифікаційного номеру
        id_match = re.search(r'(\d{10})', text)
        if id_match:
            info['identification_number'] = id_match.group(1)
        
        # Пошук підстав
        basis_match = re.search(r'Підстава:\s*(.*?)(?=Командир|$)', text, re.DOTALL | re.IGNORECASE)
        if basis_match:
            info['basis'] = basis_match.group(1).strip()
        
        return info
    
    def detect_order_type(self, text: str) -> str:
        for order_type, pattern in self.patterns['order_types'].items():
            if re.search(pattern, text, re.IGNORECASE):
                return order_type
        return 'невідомо'
    
    def extract_order_number(self, text: str) -> Optional[str]:
        patterns = [r'№\s*(\d+)', r'Наказ.*?№\s*(\d+)']
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        return None
    
    def extract_date(self, text: str) -> Optional[str]:
        date_pattern = r'\d{1,2}\.\d{1,2}\.\d{4}'
        match = re.search(date_pattern, text)
        return match.group(0) if match else None
    
    def extract_military_unit(self, text: str) -> Optional[str]:
        unit_pattern = r'військової частини\s*([А-Я]\d+)'
        match = re.search(unit_pattern, text, re.IGNORECASE)
        return match.group(1) if match else None
    
    def extract_rank_from_text(self, text: str) -> Optional[str]:
        for rank in self.patterns['ranks']:
            if rank in text.lower():
                return rank
        return None
    
    def extract_position_from_context(self, text: str, name: str) -> Optional[str]:
        position_pattern = rf'{re.escape(name)}.*?на посаду\s*([^\.]+)'
        match = re.search(position_pattern, text, re.IGNORECASE)
        return match.group(1).strip() if match else None
    
    def detect_person_action(self, text: str) -> str:
        for action, keywords in self.patterns['actions'].items():
            for keyword in keywords:
                if keyword in text.lower():
                    return action
        return 'інша дія'