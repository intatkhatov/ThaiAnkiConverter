"""
Работа с базой данных уникальных тайских слов
Храним уже обработанные слова, чтобы избежать дубликатов в Anki
"""

import sqlite3
import os
from config import BASE_DIR

# Путь к файлу базы данных
DB_PATH = os.path.join(BASE_DIR, "thai_words.db")

def init_database():
    """
    Создаёт таблицу в базе данных, если её нет
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Создаём таблицу для уникальных тайских слов
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS thai_words (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            thai TEXT UNIQUE NOT NULL,
            transliteration TEXT,
            russian TEXT,
            source_file TEXT,
            date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print(f"✅ База данных инициализирована: {DB_PATH}")

def get_all_words():
    """
    Возвращает множество всех тайских слов из базы
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT thai FROM thai_words")
    words = {row[0] for row in cursor.fetchall()}
    
    conn.close()
    return words

def add_new_words(words_list, source_file):
    """
    Добавляет новые слова в базу данных
    words_list: список карточек [[thai, transliteration, russian], ...]
    source_file: имя исходного JSON файла (для истории)
    
    Возвращает количество добавленных слов
    """
    if not words_list:
        return 0
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    added_count = 0
    for card in words_list:
        thai, transliteration, russian = card
        
        try:
            cursor.execute('''
                INSERT INTO thai_words (thai, transliteration, russian, source_file)
                VALUES (?, ?, ?, ?)
            ''', (thai, transliteration, russian, source_file))
            added_count += 1
        except sqlite3.IntegrityError:
            # Это слово уже есть в базе - пропускаем
            pass
    
    conn.commit()
    conn.close()
    
    return added_count

def get_database_stats():
    """
    Возвращает статистику по базе данных
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM thai_words")
    total = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(DISTINCT source_file) FROM thai_words")
    files = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        "total_words": total,
        "source_files": files,
        "db_path": DB_PATH
    }

def remove_duplicates(cards):
    """
    Удаляет дубликаты из списка карточек (по тайскому слову)
    Возвращает уникальные карточки и количество удалённых
    """
    seen = set()
    unique_cards = []
    
    for card in cards:
        thai = card[0]  # тайское слово
        if thai not in seen:
            seen.add(thai)
            unique_cards.append(card)
    
    duplicates_removed = len(cards) - len(unique_cards)
    return unique_cards, duplicates_removed

def filter_new_words(cards):
    """
    Оставляет только те карточки, которых ещё нет в базе данных
    Возвращает новые карточки и список существующих
    """
    existing_words = get_all_words()
    
    new_cards = []
    existing_cards = []
    
    for card in cards:
        thai = card[0]
        if thai in existing_words:
            existing_cards.append(card)
        else:
            new_cards.append(card)
    
    return new_cards, existing_cards