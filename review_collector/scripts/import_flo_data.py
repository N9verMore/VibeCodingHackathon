#!/usr/bin/env python3
"""
Скрипт для завантаження даних з flo_db_format.json в DynamoDB таблицю ReviewsTableV2
"""

import json
import os
import sys
from pathlib import Path
import boto3
from botocore.exceptions import ClientError
from datetime import datetime

# Додаємо шлях до shared модулів
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

def load_json_data(json_file_path: str) -> list:
    """Завантажити дані з JSON файлу"""
    with open(json_file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def import_to_dynamodb(data: list, table_name: str = 'ReviewsTableV2', region: str = 'us-east-1', profile: str = None):
    """
    Імпортувати дані в DynamoDB таблицю
    
    Args:
        data: Список записів для імпорту
        table_name: Назва DynamoDB таблиці
        region: AWS регіон
        profile: AWS профіль
    """
    # Ініціалізація DynamoDB клієнта
    session = boto3.Session(profile_name=profile) if profile else boto3.Session()
    dynamodb = session.resource('dynamodb', region_name=region)
    table = dynamodb.Table(table_name)
    
    stats = {
        'total': len(data),
        'success': 0,
        'skipped': 0,
        'errors': 0
    }
    
    print(f"Початок імпорту {stats['total']} записів в таблицю {table_name}...")
    print(f"Регіон: {region}")
    print("-" * 80)
    
    for idx, item in enumerate(data, 1):
        try:
            pk = item.get('pk')
            
            # Перевірка чи існує запис
            try:
                response = table.get_item(Key={'pk': pk})
                if 'Item' in response:
                    # Перевірка content_hash для визначення чи змінилися дані
                    existing_hash = response['Item'].get('content_hash')
                    new_hash = item.get('content_hash')
                    
                    if existing_hash == new_hash:
                        print(f"[{idx}/{stats['total']}] ПРОПУЩЕНО: {pk} (незмінений)")
                        stats['skipped'] += 1
                        continue
                    else:
                        print(f"[{idx}/{stats['total']}] ОНОВЛЕННЯ: {pk} (content_hash змінився)")
            except ClientError as e:
                if e.response['Error']['Code'] != 'ResourceNotFoundException':
                    raise
            
            # Підготовка запису для DynamoDB
            # Всі дані з JSON вже в правильному форматі
            dynamodb_item = item.copy()
            
            # Конвертуємо None в порожні рядки для полів, які не можуть бути null
            for field in ['title', 'country', 'author_hint']:
                if dynamodb_item.get(field) is None:
                    dynamodb_item[field] = ''
            
            # Конвертуємо rating в number якщо він є
            if dynamodb_item.get('rating') is not None:
                dynamodb_item['rating'] = int(dynamodb_item['rating']) if dynamodb_item['rating'] else 0
            else:
                dynamodb_item['rating'] = 0
            
            # Записуємо в таблицю
            table.put_item(Item=dynamodb_item)
            
            brand = item.get('brand', 'N/A')
            source = item.get('source', 'N/A')
            print(f"[{idx}/{stats['total']}] ✓ ЗАПИСАНО: {pk} (brand: {brand}, source: {source})")
            stats['success'] += 1
            
        except Exception as e:
            print(f"[{idx}/{stats['total']}] ✗ ПОМИЛКА: {pk} - {str(e)}")
            stats['errors'] += 1
            continue
    
    # Виводимо статистику
    print("-" * 80)
    print("\n📊 РЕЗУЛЬТАТИ ІМПОРТУ:")
    print(f"  Всього записів:      {stats['total']}")
    print(f"  ✓ Успішно записано:  {stats['success']}")
    print(f"  ⊝ Пропущено:         {stats['skipped']}")
    print(f"  ✗ Помилок:           {stats['errors']}")
    print("-" * 80)
    
    return stats

def main():
    """Головна функція"""
    # Шлях до JSON файлу
    json_file = Path(__file__).parent.parent / 'flo_db_format.json'
    
    if not json_file.exists():
        print(f"❌ Файл не знайдено: {json_file}")
        sys.exit(1)
    
    print("=" * 80)
    print("  ІМПОРТ ДАНИХ FLO В DYNAMODB")
    print("=" * 80)
    print(f"\nФайл даних: {json_file}")
    
    # Параметри (можна змінити)
    table_name = os.environ.get('TABLE_NAME', 'ReviewsTableV2')
    region = os.environ.get('AWS_REGION', 'us-east-1')
    profile = os.environ.get('AWS_PROFILE', 'hackathon')
    
    print(f"Таблиця: {table_name}")
    print(f"Регіон: {region}")
    print(f"Профіль: {profile}")
    
    # Запит підтвердження
    response = input("\n⚠️  Продовжити імпорт? (yes/no): ")
    if response.lower() not in ['yes', 'y']:
        print("Імпорт скасовано.")
        sys.exit(0)
    
    print()
    
    # Завантаження даних
    try:
        data = load_json_data(json_file)
        print(f"✓ Завантажено {len(data)} записів з JSON файлу\n")
    except Exception as e:
        print(f"❌ Помилка читання JSON: {e}")
        sys.exit(1)
    
    # Імпорт в DynamoDB
    try:
        stats = import_to_dynamodb(data, table_name, region, profile)
        
        if stats['errors'] > 0:
            print("\n⚠️  Імпорт завершено з помилками")
            sys.exit(1)
        else:
            print("\n✓ Імпорт успішно завершено!")
            sys.exit(0)
            
    except Exception as e:
        print(f"\n❌ Критична помилка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

