"""
ThaiAnkiConverter - главный файл-дирижёр
Конвертирует JSON файлы в CSV формат для Anki с проверкой дубликатов
"""

import os
import sys
from config import JSON_DIR, CSV_DIR
from file_utils import get_json_files, read_json_file, write_csv_file, preview_data
from data_converter import prepare_anki_cards, validate_data, get_csv_filename
from database import init_database, remove_duplicates, filter_new_words, add_new_words, get_database_stats

def clear_screen():
    """Очищает экран терминала"""
    os.system('clear' if os.name == 'posix' else 'cls')

def print_header():
    """Показывает заголовок программы"""
    print("=" * 60)
    print("   ThaiAnkiConverter - JSON → CSV для Anki (с защитой от дубликатов)")
    print("=" * 60)

def show_stats():
    """Показывает статистику базы данных"""
    stats = get_database_stats()
    print(f"\n📊 Статистика базы данных:")
    print(f"   Всего уникальных слов: {stats['total_words']}")
    print(f"   Обработано файлов: {stats['source_files']}")

def select_json_file():
    """
    Показывает список JSON файлов и даёт выбрать
    Возвращает имя выбранного файла или None
    """
    files = get_json_files()
    
    if not files:
        print("\n❌ В папке 'json' нет файлов с расширением .json")
        print(f"📁 Положите JSON файлы сюда: {JSON_DIR}")
        return None
    
    print("\n📁 Доступные JSON файлы:")
    for i, file in enumerate(files, 1):
        print(f"  {i}. {file}")
    
    while True:
        try:
            choice = input("\nВыберите номер файла (или 'q' для выхода): ").strip()
            
            if choice.lower() == 'q':
                return None
            
            idx = int(choice) - 1
            if 0 <= idx < len(files):
                return files[idx]
            else:
                print(f"⚠️ Введите число от 1 до {len(files)}")
        except ValueError:
            print("⚠️ Пожалуйста, введите номер файла")

def main():
    """Главная функция программы"""
    clear_screen()
    print_header()
    
    # Инициализируем базу данных при каждом запуске
    init_database()
    show_stats()
    
    # Шаг 1: Выбираем JSON файл
    json_file = select_json_file()
    if not json_file:
        print("\n👋 Выход из программы")
        return
    
    # Шаг 2: Читаем JSON файл
    print(f"\n📖 Чтение файла: {json_file}")
    json_data = read_json_file(json_file)
    
    if json_data is None:
        print("❌ Не удалось прочитать файл")
        return
    
    # Шаг 3: Предпросмотр данных
    preview_data(json_data)
    
    # Шаг 4: Конвертируем в формат Anki
    print("\n🔄 Конвертация данных...")
    anki_cards = prepare_anki_cards(json_data)
    
    if not anki_cards:
        print("❌ Нет данных для сохранения")
        return
    
    # Шаг 5: Удаляем дубликаты внутри файла
    unique_cards, duplicates_in_file = remove_duplicates(anki_cards)
    if duplicates_in_file > 0:
        print(f"\n🔍 Найдено дубликатов внутри файла: {duplicates_in_file}")
    
    # Шаг 6: Проверяем, каких слов ещё нет в базе данных
    new_cards, existing_cards = filter_new_words(unique_cards)
    
    print(f"\n📊 Анализ:")
    print(f"   Всего карточек в файле: {len(anki_cards)}")
    print(f"   Уникальных карточек: {len(unique_cards)}")
    print(f"   Уже есть в базе данных: {len(existing_cards)}")
    print(f"   Новых слов для добавления: {len(new_cards)}")
    
    # Показываем существующие слова, если есть
    if existing_cards:
        print("\n⚠️ Слова, которые уже есть в базе (будут пропущены):")
        for card in existing_cards[:5]:  # Показываем первые 5
            print(f"   • {card[0]} - {card[2]}")
        if len(existing_cards) > 5:
            print(f"   ... и ещё {len(existing_cards) - 5}")
    
    if not new_cards:
        print("\n❌ Все слова уже есть в базе данных. CSV файл не создан.")
        return
    
    # Шаг 7: Проверяем данные на пустые значения
    warnings = validate_data(new_cards)
    if warnings:
        print("\n⚠️ Найдены предупреждения в новых карточках:")
        for w in warnings:
            print(f"  {w}")
        
        confirm = input("\nПродолжить сохранение? (y/n): ").strip().lower()
        if confirm != 'y':
            print("❌ Сохранение отменено")
            return
    
    # Шаг 8: Сохраняем новые слова в CSV
    if new_cards:
        csv_filename = f"unique_{get_csv_filename(json_file)}"
        success = write_csv_file(csv_filename, new_cards)
        
        if success:
            print(f"\n✅ CSV файл с уникальными словами сохранён:")
            print(f"   {CSV_DIR}/{csv_filename}")
            
            # Шаг 9: Добавляем новые слова в базу данных
            added = add_new_words(new_cards, json_file)
            print(f"\n💾 Добавлено в базу данных: {added} новых слов")
            
            print("\n📱 Теперь этот CSV можно импортировать в Anki")
            print("   (дубликаты автоматически исключены)")
        else:
            print("\n❌ Не удалось сохранить CSV файл")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Программа прервана пользователем")
    except Exception as e:
        print(f"\n❌ Неожиданная ошибка: {e}")
        print("Пожалуйста, сообщите об этой ошибке")