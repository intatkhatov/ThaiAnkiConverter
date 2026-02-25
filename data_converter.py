"""
Конвертер данных из JSON формата в CSV формат для Anki
"""

def prepare_anki_cards(json_data):
    """
    Преобразует JSON данные в формат для Anki CSV
    
    Вход: список словарей с ключами: number, thai, transliteration, russian
    Выход: список списков [[thai, transliteration, russian], ...]
    """
    if not json_data:
        print("❌ Нет данных для конвертации")
        return []
    
    anki_cards = []
    
    for item in json_data:
        # Проверяем, что есть все необходимые поля
        if all(key in item for key in ['thai', 'transliteration', 'russian']):
            # Создаём карточку в формате [thai, transliteration, russian]
            card = [
                str(item['thai']).strip(),           # тайское слово
                str(item['transliteration']).strip(), # транслитерация
                str(item['russian']).strip()          # перевод
            ]
            anki_cards.append(card)
        else:
            print(f"⚠️ Пропущена запись {item.get('number', 'unknown')}: отсутствуют нужные поля")
            print(f"   Найдены поля: {list(item.keys())}")
    
    print(f"✅ Подготовлено {len(anki_cards)} карточек для Anki")
    return anki_cards

def validate_data(cards):
    """
    Проверяет данные на пустые значения
    Возвращает список предупреждений
    """
    warnings = []
    
    for i, card in enumerate(cards, 1):
        if not card[0]:  # пустое тайское слово
            warnings.append(f"Карточка {i}: пустое тайское слово")
        if not card[1]:  # пустая транслитерация
            warnings.append(f"Карточка {i}: пустая транслитерация")
        if not card[2]:  # пустой перевод
            warnings.append(f"Карточка {i}: пустой перевод")
    
    return warnings

def get_csv_filename(json_filename):
    """
    Генерирует имя CSV файла из имени JSON файла
    Например: data.json -> data.csv
    """
    if json_filename.endswith('.json'):
        return json_filename[:-5] + '.csv'
    return json_filename + '.csv'