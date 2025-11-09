# document_parser.py
import PyPDF2
import pandas as pd
from docx import Document
import re

class DocumentParser:
    def parse_pdf(self, file_path):
        """Парсинг PDF документов"""
        text = ""
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text()
        return text
    
    def parse_docx(self, file_path):
        """Парсинг DOCX документов"""
        doc = Document(file_path)
        text = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
        return text
    
    def extract_order_data(self, text):
        """Извлечение данных из текста приказа"""
        data = {
            'order_type': self.detect_order_type(text),
            'order_number': self.extract_order_number(text),
            'date': self.extract_date(text),
            'personnel': self.extract_personnel(text)
        }
        return data
    
    def detect_order_type(self, text):
        """Определение типа приказа"""
        if 'особовому складу' in text.lower():
            return 'personnel'
        elif 'стройовій частині' in text.lower():
            return 'service'
        else:
            return 'other'