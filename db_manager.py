"""
Менеджер базы данных ThaiAnkiConverter
Очистка, просмотр и управление базой данных уникальных слов
"""

import os
import sys
from database import init_database, get_database_stats, DB_PATH
import sqlite3

def clear_screen():
    """Очищает экран терминала"""
    os.system('clear' if os.name == 'posix' else 'cls')

def print_header():
    """Показывает заголовок программы"""
    print("=" * 60)
    print("   ThaiAnkiConverter - Управление базой данных")
    print("=" * 60)

def show_menu():
    """Показывает меню управления БД"""
    print("\n📋 Меню управления:")
    print("  1. Показать статистику БД")
    print("  2. Показать все слова в БД")
    print("  3. Показать слова из конкретного файла")
    print("  4. Очистить всю БД (удалить все слова)")
    print("  5. Удалить слова из конкретного файла")
    print("  6. Поиск слова по тайскому тексту")
    print("  0. Выход")
    return input("\nВыберите действие: ").strip()

def show_all_words(limit=20):
    """Показывает все слова в БД с пагинацией"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Сначала получим общее количество
    cursor.execute("SELECT COUNT(*) FROM thai_words")
    total = cursor.fetchone()[0]
    
    if total == 0:
        print("\n📭 База данных пуста")
        conn.close()
        return
    
    print(f"\n📖 Всего слов в БД: {total}")
    print("-" * 80)
    
    offset = 0
    while offset < total:
        cursor.execute("""
            SELECT id, thai, transliteration, russian, source_file, date_added 
            FROM thai_words 
            ORDER BY date_added DESC 
            LIMIT ? OFFSET ?
        """, (limit, offset))
        
        words = cursor.fetchall()
        
        for word in words:
            print(f"ID: {word[0]}")
            print(f"   🇹🇭 Тайское: {word[1]}")
            print(f"   📝 Транслит: {word[2]}")
            print(f"   🇷🇺 Перевод: {word[3]}")
            print(f"   📁 Файл: {word[4]}")
            print(f"   📅 Добавлено: {word[5]}")
            print("-" * 80)
        
        offset += limit
        
        if offset < total:
            choice = input(f"\nПоказано {offset} из {total}. Нажмите Enter для продолжения или 'q' для выхода: ")
            if choice.lower() == 'q':
                break
    
    conn.close()

def show_words_from_file():
    """Показывает слова из конкретного файла"""
    # Получим список уникальных файлов
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT DISTINCT source_file FROM thai_words ORDER BY source_file")
    files = cursor.fetchall()
    conn.close()
    
    if not files:
        print("\n📭 В базе нет слов")
        return
    
    print("\n📁 Доступные файлы:")
    for i, file in enumerate(files, 1):
        print(f"  {i}. {file[0]}")
    
    try:
        choice = int(input("\nВыберите номер файла: ")) - 1
        if 0 <= choice < len(files):
            selected_file = files[choice][0]
            
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT thai, transliteration, russian, date_added 
                FROM thai_words 
                WHERE source_file = ?
                ORDER BY date_added DESC
            """, (selected_file,))
            
            words = cursor.fetchall()
            conn.close()
            
            print(f"\n📖 Слова из файла '{selected_file}':")
            print("-" * 60)
            for word in words:
                print(f"   🇹🇭 {word[0]} | 📝 {word[1]} | 🇷🇺 {word[2]} | 📅 {word[3]}")
            print(f"\n✅ Всего слов: {len(words)}")
    except (ValueError, IndexError):
        print("❌ Неправильный выбор")

def clear_entire_database():
    """Полная очистка БД"""
    print("\n⚠️  ВНИМАНИЕ! Это удалит ВСЕ слова из базы данных!")
    print("   Будут удалены все записи без возможности восстановления.")
    
    confirm = input("\nДля подтверждения введите 'DELETE ALL': ")
    
    if confirm == "DELETE ALL":
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM thai_words")
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='thai_words'")  # Сброс счётчика ID
        
        conn.commit()
        conn.close()
        
        print("✅ База данных полностью очищена")
    else:
        print("❌ Операция отменена")

def delete_words_from_file():
    """Удаляет слова из конкретного файла"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT DISTINCT source_file, COUNT(*) FROM thai_words GROUP BY source_file")
    files = cursor.fetchall()
    conn.close()
    
    if not files:
        print("\n📭 В базе нет слов")
        return
    
    print("\n📁 Файлы в базе данных:")
    for i, (file, count) in enumerate(files, 1):
        print(f"  {i}. {file} ({count} слов)")
    
    try:
        choice = int(input("\nВыберите номер файла для удаления: ")) - 1
        if 0 <= choice < len(files):
            selected_file = files[choice][0]
            word_count = files[choice][1]
            
            print(f"\n⚠️  Вы выбрали файл: {selected_file}")
            print(f"   Будет удалено слов: {word_count}")
            
            confirm = input(f"\nВведите 'DELETE {selected_file}' для подтверждения: ")
            
            if confirm == f"DELETE {selected_file}":
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                
                cursor.execute("DELETE FROM thai_words WHERE source_file = ?", (selected_file,))
                deleted = cursor.rowcount
                
                conn.commit()
                conn.close()
                
                print(f"✅ Удалено слов: {deleted}")
            else:
                print("❌ Операция отменена")
    except (ValueError, IndexError):
        print("❌ Неправильный выбор")

def search_word():
    """Поиск слова по тайскому тексту"""
    search_term = input("\n🔍 Введите тайское слово (или часть) для поиска: ").strip()
    
    if not search_term:
        print("❌ Пустой запрос")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT thai, transliteration, russian, source_file, date_added 
        FROM thai_words 
        WHERE thai LIKE ?
        ORDER BY thai
    """, (f'%{search_term}%',))
    
    results = cursor.fetchall()
    conn.close()
    
    if not results:
        print(f"\n❌ Слов, содержащих '{search_term}', не найдено")
        return
    
    print(f"\n🔍 Найдено слов: {len(results)}")
    print("-" * 60)
    for word in results:
        print(f"   🇹🇭 {word[0]}")
        print(f"   📝 {word[1]}")
        print(f"   🇷🇺 {word[2]}")
        print(f"   📁 {word[3]} | 📅 {word[4]}")
        print("-" * 40)

def main():
    """Главная функция менеджера БД"""
    while True:
        clear_screen()
        print_header()
        
        # Показываем статистику
        stats = get_database_stats()
        print(f"\n📊 Текущая статистика:")
        print(f"   Всего уникальных слов: {stats['total_words']}")
        print(f"   Обработано файлов: {stats['source_files']}")
        print(f"   📁 База данных: {stats['db_path']}")
        
        choice = show_menu()
        
        if choice == "1":
            input("\nНажмите Enter для продолжения...")
        
        elif choice == "2":
            show_all_words()
            input("\nНажмите Enter для продолжения...")
        
        elif choice == "3":
            show_words_from_file()
            input("\nНажмите Enter для продолжения...")
        
        elif choice == "4":
            clear_entire_database()
            input("\nНажмите Enter для продолжения...")
        
        elif choice == "5":
            delete_words_from_file()
            input("\nНажмите Enter для продолжения...")
        
        elif choice == "6":
            search_word()
            input("\nНажмите Enter для продолжения...")
        
        elif choice == "0":
            print("\n👋 Выход из менеджера БД")
            break
        
        else:
            print("\n❌ Неправильный выбор")
            input("Нажмите Enter для продолжения...")

if __name__ == "__main__":
    try:
        # Инициализируем БД при запуске
        init_database()
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Программа прервана пользователем")
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")