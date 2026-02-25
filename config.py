"""
Конфигурация приложения ThaiAnkiConverter
"""

import os

# Базовая директория проекта
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Пути к папкам
JSON_DIR = os.path.join(BASE_DIR, "json")
CSV_DIR = os.path.join(BASE_DIR, "csv")

# Убеждаемся, что папки существуют
os.makedirs(JSON_DIR, exist_ok=True)
os.makedirs(CSV_DIR, exist_ok=True)