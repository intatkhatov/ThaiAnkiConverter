"""
Утилиты для работы с файлами: чтение JSON, запись CSV
"""

import json
import csv
import os
from config import JSON_DIR, CSV_DIR

def get_json_files():
    """
    Возвращает список всех JSON файлов в папке json
    """
    try:
        files = [f for f in os.listdir(JSON_DIR) if f.endswith('.json')]
        return sorted(files)  # сортируем для удобства
    except FileNotFoundError:
        print(f"Папка {JSON_DIR} не найдена")
        return []

def read_json_file(filename):
    """
    Читает JSON файл и возвращает данные
    """
    filepath = os.path.join(JSON_DIR, filename)
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            print(f"✅ Прочитан файл: {filename}")
            return data
    except FileNotFoundError:
        print(f"❌ Файл не найден: {filepath}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Ошибка в JSON формате: {e}")
        return None

def write_csv_file(filename, data):
    """
    Записывает данные в CSV файл
    data: список списков [[thai, transliteration, russian], ...]
    """
    # Убеждаемся, что имя файла заканчивается на .csv
    if not filename.endswith('.csv'):
        filename += '.csv'
    
    filepath = os.path.join(CSV_DIR, filename)
    
    try:
        with open(filepath, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
            writer.writerows(data)
            print(f"✅ Создан CSV файл: {filename}")
            return True
    except Exception as e:
        print(f"❌ Ошибка при записи CSV: {e}")
        return False

def preview_data(data, limit=3):
    """
    Показывает первые несколько записей для предпросмотра
    """
    print(f"\n📋 Предпросмотр данных (первые {min(limit, len(data))} из {len(data)}):")
    for i, item in enumerate(data[:limit]):
        print(f"  {i+1}. {item}")