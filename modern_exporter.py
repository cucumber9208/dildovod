import json
import csv
import pandas as pd
from datetime import datetime
from typing import List, Dict
import os
from pathlib import Path

class ModernExporter:
    def __init__(self):
        self.styles = {
            'html_css': '''
                <style>
                    body { 
                        font-family: 'Segoe UI', Arial, sans-serif; 
                        margin: 20px; 
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: #333;
                    }
                    .container {
                        max-width: 1200px;
                        margin: 0 auto;
                        background: white;
                        border-radius: 15px;
                        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                        overflow: hidden;
                    }
                    .header {
                        background: linear-gradient(135deg, #2c3e50, #3498db);
                        color: white;
                        padding: 30px;
                        text-align: center;
                    }
                    .header h1 {
                        margin: 0;
                        font-size: 2.5em;
                        font-weight: 300;
                    }
                    .header .subtitle {
                        font-size: 1.2em;
                        opacity: 0.9;
                        margin-top: 10px;
                    }
                    .nav-tabs {
                        display: flex;
                        background: #34495e;
                        padding: 0;
                        margin: 0;
                        list-style: none;
                    }
                    .nav-tabs li {
                        flex: 1;
                    }
                    .nav-tabs a {
                        display: block;
                        padding: 15px;
                        color: white;
                        text-decoration: none;
                        text-align: center;
                        transition: all 0.3s ease;
                        border-bottom: 3px solid transparent;
                    }
                    .nav-tabs a:hover {
                        background: #2c3e50;
                        border-bottom: 3px solid #e74c3c;
                    }
                    .tab-content {
                        padding: 30px;
                    }
                    .section {
                        margin-bottom: 40px;
                        animation: fadeIn 0.5s ease-in;
                    }
                    .section h2 {
                        color: #2c3e50;
                        border-bottom: 2px solid #3498db;
                        padding-bottom: 10px;
                        margin-bottom: 20px;
                    }
                    table {
                        width: 100%;
                        border-collapse: collapse;
                        margin: 20px 0;
                        background: white;
                        border-radius: 10px;
                        overflow: hidden;
                        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
                    }
                    th {
                        background: linear-gradient(135deg, #3498db, #2980b9);
                        color: white;
                        padding: 15px;
                        text-align: left;
                        font-weight: 600;
                    }
                    td {
                        padding: 12px 15px;
                        border-bottom: 1px solid #ecf0f1;
                    }
                    tr:hover {
                        background: #f8f9fa;
                        transform: translateX(5px);
                        transition: all 0.2s ease;
                    }
                    .stats-grid {
                        display: grid;
                        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                        gap: 20px;
                        margin: 20px 0;
                    }
                    .stat-card {
                        background: white;
                        padding: 20px;
                        border-radius: 10px;
                        text-align: center;
                        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
                        border-left: 4px solid #3498db;
                    }
                    .stat-number {
                        font-size: 2em;
                        font-weight: bold;
                        color: #2c3e50;
                    }
                    .stat-label {
                        color: #7f8c8d;
                        margin-top: 5px;
                    }
                    .badge {
                        display: inline-block;
                        padding: 5px 10px;
                        border-radius: 20px;
                        font-size: 0.8em;
                        font-weight: bold;
                    }
                    .badge-success { background: #2ecc71; color: white; }
                    .badge-warning { background: #f39c12; color: white; }
                    .badge-error { background: #e74c3c; color: white; }
                    @keyframes fadeIn {
                        from { opacity: 0; transform: translateY(20px); }
                        to { opacity: 1; transform: translateY(0); }
                    }
                    .export-info {
                        background: #f8f9fa;
                        padding: 20px;
                        border-radius: 10px;
                        margin: 20px 0;
                        border-left: 4px solid #27ae60;
                    }
                </style>
            ''',
            'json_indent': 2
        }

    def export_data(self, orders_data: List[Dict], output_path: str, format_type: str = 'html'):
        """Універсальний експорт даних у різних форматах"""
        try:
            if format_type == 'html':
                self._export_html(orders_data, output_path)
            elif format_type == 'json':
                self._export_json(orders_data, output_path)
            elif format_type == 'csv':
                self._export_csv(orders_data, output_path)
            elif format_type == 'excel':
                self._export_excel(orders_data, output_path)
            else:
                raise ValueError(f"Непідтримуваний формат: {format_type}")
        except Exception as e:
            raise Exception(f"Помилка експорту: {str(e)}")

    def _export_html(self, orders_data: List[Dict], output_path: str):
        """Експорт у стильний HTML з інтерактивним інтерфейсом"""
        html_content = self._generate_html_report(orders_data)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

    def _generate_html_report(self, orders_data: List[Dict]) -> str:
        """Генерація HTML звіту"""
        
        # Статистика
        stats = self._calculate_stats(orders_data)
        
        html = f'''
        <!DOCTYPE html>
        <html lang="uk">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Аналіз наказів ЗСУ</title>
            {self.styles['html_css']}
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📊 Аналіз наказів ЗСУ</h1>
                    <div class="subtitle">
                        Звіт створено {datetime.now().strftime('%d.%m.%Y о %H:%M')}
                    </div>
                </div>

                <ul class="nav-tabs">
                    <li><a href="#stats">Статистика</a></li>
                    <li><a href="#summary">Зведення</a></li>
                    <li><a href="#personnel">Персонал</a></li>
                    <li><a href="#financial">Фінанси</a></li>
                    <li><a href="#documents">Документи</a></li>
                </ul>

                <div class="tab-content">
                    {self._generate_stats_section(stats)}
                    {self._generate_summary_section(orders_data)}
                    {self._generate_personnel_section(orders_data)}
                    {self._generate_financial_section(orders_data)}
                    {self._generate_documents_section(orders_data)}
                </div>
            </div>

            <script>
                // Проста навігація по вкладках
                document.querySelectorAll('.nav-tabs a').forEach(link => {{
                    link.addEventListener('click', function(e) {{
                        e.preventDefault();
                        const targetId = this.getAttribute('href').substring(1);
                        document.querySelectorAll('.section').forEach(section => {{
                            section.style.display = 'none';
                        }});
                        document.getElementById(targetId).style.display = 'block';
                    }});
                }});

                // Показуємо першу вкладку за замовчуванням
                document.getElementById('stats').style.display = 'block';
            </script>
        </body>
        </html>
        '''
        
        return html

    def _calculate_stats(self, orders_data: List[Dict]) -> Dict:
        """Розрахунок статистики"""
        total_orders = len(orders_data)
        successful_orders = len([o for o in orders_data if 'error' not in o])
        total_personnel = sum(len(o.get('personnel', [])) for o in orders_data if 'error' not in o)
        
        order_types = {}
        for order in orders_data:
            if 'error' not in order:
                order_type = order.get('type', 'невідомо')
                order_types[order_type] = order_types.get(order_type, 0) + 1
        
        return {
            'total_orders': total_orders,
            'successful_orders': successful_orders,
            'failed_orders': total_orders - successful_orders,
            'total_personnel': total_personnel,
            'order_types': order_types
        }

    def _generate_stats_section(self, stats: Dict) -> str:
        """Генерація секції статистики"""
        order_types_html = ''.join(
            f'<div class="stat-card"><div class="stat-number">{count}</div><div class="stat-label">{otype}</div></div>'
            for otype, count in stats['order_types'].items()
        )
        
        return f'''
        <div id="stats" class="section">
            <h2>📈 Статистика аналізу</h2>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number">{stats['total_orders']}</div>
                    <div class="stat-label">Всього документів</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{stats['successful_orders']}</div>
                    <div class="stat-label">Успішно оброблено</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{stats['failed_orders']}</div>
                    <div class="stat-label">З помилками</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{stats['total_personnel']}</div>
                    <div class="stat-label">Змін персоналу</div>
                </div>
            </div>

            <h3>Розподіл за типами наказів</h3>
            <div class="stats-grid">
                {order_types_html}
            </div>
        </div>
        '''

    def _generate_summary_section(self, orders_data: List[Dict]) -> str:
        """Генерація секції зведення"""
        rows = []
        for order in orders_data:
            status_badge = '<span class="badge badge-success">OK</span>' if 'error' not in order else '<span class="badge badge-error">Помилка</span>'
            personnel_count = len(order.get('personnel', []))
            
            rows.append(f'''
            <tr>
                <td>{order.get('file_name', 'н/д')}</td>
                <td>{order.get('type', 'невідомо')}</td>
                <td>{order.get('number', 'н/д')}</td>
                <td>{order.get('date', 'н/д')}</td>
                <td>{personnel_count}</td>
                <td>{status_badge}</td>
            </tr>
            ''')
        
        return f'''
        <div id="summary" class="section" style="display: none;">
            <h2>📋 Зведена інформація</h2>
            <table>
                <thead>
                    <tr>
                        <th>Файл</th>
                        <th>Тип</th>
                        <th>Номер</th>
                        <th>Дата</th>
                        <th>Персонал</th>
                        <th>Статус</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join(rows)}
                </tbody>
            </table>
        </div>
        '''

    def _generate_personnel_section(self, orders_data: List[Dict]) -> str:
        """Генерація секції персоналу"""
        rows = []
        for order in orders_data:
            if 'error' not in order:
                for person in order.get('personnel', []):
                    rows.append(f'''
                    <tr>
                        <td>{order.get('number', 'н/д')}</td>
                        <td>{person.get('full_name', 'н/д')}</td>
                        <td>{person.get('rank', 'н/д')}</td>
                        <td>{person.get('position', 'н/д')}</td>
                        <td>{person.get('action', 'н/д')}</td>
                    </tr>
                    ''')
        
        return f'''
        <div id="personnel" class="section" style="display: none;">
            <h2>👥 Зміни персоналу</h2>
            <table>
                <thead>
                    <tr>
                        <th>Номер наказу</th>
                        <th>ПІБ</th>
                        <th>Звання</th>
                        <th>Посада</th>
                        <th>Дія</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join(rows) if rows else '<tr><td colspan="5" style="text-align: center;">Немає даних</td></tr>'}
                </tbody>
            </table>
        </div>
        '''

    def _generate_financial_section(self, orders_data: List[Dict]) -> str:
        """Генерація фінансової секції"""
        rows = []
        for order in orders_data:
            if 'error' not in order and 'advanced_data' in order:
                for op in order['advanced_data'].get('financial_operations', []):
                    rows.append(f'''
                    <tr>
                        <td>{order.get('number', 'н/д')}</td>
                        <td>{op.get('type', 'н/д')}</td>
                        <td>{op.get('description', 'н/д')}</td>
                        <td>{op.get('amount', 'н/д')}</td>
                    </tr>
                    ''')
        
        return f'''
        <div id="financial" class="section" style="display: none;">
            <h2>💰 Фінансові операції</h2>
            <table>
                <thead>
                    <tr>
                        <th>Номер наказу</th>
                        <th>Тип операції</th>
                        <th>Опис</th>
                        <th>Сума/Відсоток</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join(rows) if rows else '<tr><td colspan="4" style="text-align: center;">Немає фінансових операцій</td></tr>'}
                </tbody>
            </table>
        </div>
        '''

    def _generate_documents_section(self, orders_data: List[Dict]) -> str:
        """Генерація секції документів"""
        rows = []
        for order in orders_data:
            if 'error' not in order and 'advanced_data' in order:
                for op in order['advanced_data'].get('document_operations', []):
                    rows.append(f'''
                    <tr>
                        <td>{order.get('number', 'н/д')}</td>
                        <td>{op.get('type', 'н/д')}</td>
                        <td>{op.get('description', 'н/д')}</td>
                        <td>{op.get('duration', 'н/д')}</td>
                    </tr>
                    ''')
        
        return f'''
        <div id="documents" class="section" style="display: none;">
            <h2>📄 Операції з документами</h2>
            <table>
                <thead>
                    <tr>
                        <th>Номер наказу</th>
                        <th>Тип операції</th>
                        <th>Опис</th>
                        <th>Тривалість</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join(rows) if rows else '<tr><td colspan="4" style="text-align: center;">Немає операцій з документами</td></tr>'}
                </tbody>
            </table>
        </div>
        '''

    def _export_json(self, orders_data: List[Dict], output_path: str):
        """Експорт у структурований JSON"""
        export_data = {
            'metadata': {
                'export_date': datetime.now().isoformat(),
                'total_documents': len(orders_data),
                'version': '1.0'
            },
            'orders': orders_data
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=self.styles['json_indent'])

    def _export_csv(self, orders_data: List[Dict], output_path: str):
        """Експорт у CSV з розділенням по типам даних"""
        # Створюємо папку для CSV файлів
        csv_dir = Path(output_path).with_suffix('')
        csv_dir.mkdir(exist_ok=True)
        
        # Експорт зведених даних
        summary_data = []
        for order in orders_data:
            summary_data.append({
                'file_name': order.get('file_name', ''),
                'order_type': order.get('type', ''),
                'order_number': order.get('number', ''),
                'order_date': order.get('date', ''),
                'personnel_count': len(order.get('personnel', [])),
                'status': 'OK' if 'error' not in order else 'ERROR'
            })
        
        self._write_csv(summary_data, csv_dir / 'summary.csv')
        
        # Експорт даних персоналу
        personnel_data = []
        for order in orders_data:
            if 'error' not in order:
                for person in order.get('personnel', []):
                    personnel_data.append({
                        'order_number': order.get('number', ''),
                        'order_date': order.get('date', ''),
                        'full_name': person.get('full_name', ''),
                        'rank': person.get('rank', ''),
                        'position': person.get('position', ''),
                        'action': person.get('action', '')
                    })
        
        self._write_csv(personnel_data, csv_dir / 'personnel.csv')

    def _write_csv(self, data: List[Dict], file_path: Path):
        """Запис даних у CSV файл"""
        if data:
            with open(file_path, 'w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)

    def _export_excel(self, orders_data: List[Dict], output_path: str):
        """Мінімалістичний експорт в Excel (для тих, хто все ще хоче Excel)"""
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # Тільки основні дані
            summary_data = []
            for order in orders_data:
                summary_data.append({
                    'Файл': order.get('file_name', 'н/д'),
                    'Тип': order.get('type', 'невідомо'),
                    'Номер': order.get('number', 'н/д'),
                    'Дата': order.get('date', 'н/д'),
                    'Кількість осіб': len(order.get('personnel', [])),
                    'Статус': 'OK' if 'error' not in order else 'Помилка'
                })
            
            if summary_data:
                df = pd.DataFrame(summary_data)
                df.to_excel(writer, sheet_name='Зведення', index=False)