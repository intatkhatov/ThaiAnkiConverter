"""
ThaiAnkiConverter - главный файл-дирижёр
Конвертирует JSON файлы в CSV формат для Anki
"""

import os
import sys
from config import JSON_DIR, CSV_DIR
from file_utils import get_json_files, read_json_file, write_csv_file, preview_data
from data_converter import prepare_anki_cards, validate_data, get_csv_filename

def clear_screen():
    """Очищает экран терминала"""
    os.system('clear' if os.name == 'posix' else 'cls')

def print_header():
    """Показывает заголовок программы"""
    print("=" * 50)
    print("   ThaiAnkiConverter - JSON → CSV для Anki")
    print("=" * 50)

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
    
    # Шаг 5: Проверяем данные
    warnings = validate_data(anki_cards)
    if warnings:
        print("\n⚠️ Найдены предупреждения:")
        for w in warnings:
            print(f"  {w}")
        
        confirm = input("\nПродолжить сохранение? (y/n): ").strip().lower()
        if confirm != 'y':
            print("❌ Сохранение отменено")
            return
    
    # Шаг 6: Сохраняем в CSV
    csv_filename = get_csv_filename(json_file)
    success = write_csv_file(csv_filename, anki_cards)
    
    if success:
        print(f"\n✅ Готово! CSV файл сохранён:")
        print(f"   {CSV_DIR}/{csv_filename}")
        print("\n📱 Теперь его можно импортировать в Anki")
    else:
        print("\n❌ Не удалось сохранить CSV файл")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Программа прервана пользователем")
    except Exception as e:
        print(f"\n❌ Неожиданная ошибка: {e}")
        print("Пожалуйста, сообщите об этой ошибке")