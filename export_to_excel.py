"""
Экспорт данных парсера в Excel таблицу
"""

import pandas as pd
from amazon_advanced import AdvancedAmazonParser
import asyncio
import logging
from datetime import datetime
import os

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def parse_and_export_to_excel(url: str, filename: str = None):
    """
    Парсинг товаров и экспорт в Excel
    
    Args:
        url: URL для парсинга
        filename: Имя файла Excel (опционально)
    """
    
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"amazon_products_{timestamp}.xlsx"
    
    print(f"🚀 Парсинг товаров с: {url}")
    print(f"📊 Экспорт в Excel: {filename}")
    print("=" * 60)
    
    try:
        # Парсим товары
        async with AdvancedAmazonParser(headless=True) as parser:
            products = await parser.parse(url)
        
        if not products:
            print("❌ Товары не найдены")
            return None
        
        print(f"✅ Найдено товаров: {len(products)}")
        
        # Создаем DataFrame
        df = pd.DataFrame(products)
        
        # Добавляем дополнительные колонки
        df['Дата парсинга'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        df['URL источника'] = url
        df['Номер'] = range(1, len(df) + 1)
        
        # Переупорядочиваем колонки
        columns_order = ['Номер', 'id', 'name', 'price', 'Дата парсинга', 'URL источника']
        df = df[columns_order]
        
        # Переименовываем колонки для красоты
        df.columns = ['№', 'ID товара', 'Название товара', 'Цена', 'Дата парсинга', 'URL источника']
        
        # Создаем Excel файл с форматированием
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # Основной лист с данными
            df.to_excel(writer, sheet_name='Товары', index=False)
            
            # Получаем объект workbook и worksheet для форматирования
            workbook = writer.book
            worksheet = writer.sheets['Товары']
            
            # Настройка ширины колонок
            column_widths = {
                'A': 8,   # №
                'B': 15,  # ID товара
                'C': 60,  # Название товара
                'D': 15,  # Цена
                'E': 20,  # Дата парсинга
                'F': 30   # URL источника
            }
            
            for col, width in column_widths.items():
                worksheet.column_dimensions[col].width = width
            
            # Создаем лист со статистикой
            stats_data = {
                'Параметр': [
                    'Общее количество товаров',
                    'Товары с указанной ценой',
                    'Товары без цены',
                    'Дата парсинга',
                    'URL источника',
                    'Время выполнения'
                ],
                'Значение': [
                    len(products),
                    len([p for p in products if p['price'] != 'Цена не указана']),
                    len([p for p in products if p['price'] == 'Цена не указана']),
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    url,
                    f"~{len(products) * 2} секунд"
                ]
            }
            
            stats_df = pd.DataFrame(stats_data)
            stats_df.to_excel(writer, sheet_name='Статистика', index=False)
            
            # Форматируем лист статистики
            stats_worksheet = writer.sheets['Статистика']
            stats_worksheet.column_dimensions['A'].width = 30
            stats_worksheet.column_dimensions['B'].width = 40
        
        print(f"✅ Данные успешно экспортированы в: {filename}")
        print(f"📁 Полный путь: {os.path.abspath(filename)}")
        
        # Показываем статистику
        print("\n📊 Статистика:")
        print(f"   • Всего товаров: {len(products)}")
        print(f"   • С ценой: {len([p for p in products if p['price'] != 'Цена не указана'])}")
        print(f"   • Без цены: {len([p for p in products if p['price'] == 'Цена не указана'])}")
        
        # Показываем первые 5 товаров
        print("\n🔍 Первые 5 товаров:")
        for i, product in enumerate(products[:5], 1):
            print(f"   {i}. {product['name'][:50]}{'...' if len(product['name']) > 50 else ''} - {product['price']}")
        
        return filename
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None


async def parse_multiple_urls(urls: list, base_filename: str = None):
    """
    Парсинг нескольких URL и экспорт в один Excel файл
    
    Args:
        urls: Список URL для парсинга
        base_filename: Базовое имя файла
    """
    
    if not base_filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = f"amazon_products_multiple_{timestamp}.xlsx"
    
    print(f"🚀 Парсинг {len(urls)} URL")
    print(f"📊 Экспорт в Excel: {base_filename}")
    print("=" * 60)
    
    all_products = []
    
    try:
        async with AdvancedAmazonParser(headless=True) as parser:
            for i, url in enumerate(urls, 1):
                print(f"\n📦 Парсинг {i}/{len(urls)}: {url}")
                
                try:
                    products = await parser.parse(url)
                    if products:
                        # Добавляем информацию об источнике
                        for product in products:
                            product['URL источника'] = url
                            product['Категория'] = f"Категория {i}"
                        
                        all_products.extend(products)
                        print(f"   ✅ Найдено: {len(products)} товаров")
                    else:
                        print(f"   ❌ Товары не найдены")
                        
                except Exception as e:
                    print(f"   ❌ Ошибка: {e}")
                    continue
        
        if not all_products:
            print("❌ Товары не найдены ни на одном URL")
            return None
        
        # Создаем DataFrame
        df = pd.DataFrame(all_products)
        
        # Добавляем дополнительные колонки
        df['Дата парсинга'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        df['Номер'] = range(1, len(df) + 1)
        
        # Переупорядочиваем колонки
        columns_order = ['Номер', 'id', 'name', 'price', 'Категория', 'URL источника', 'Дата парсинга']
        df = df[columns_order]
        
        # Переименовываем колонки
        df.columns = ['№', 'ID товара', 'Название товара', 'Цена', 'Категория', 'URL источника', 'Дата парсинга']
        
        # Создаем Excel файл
        with pd.ExcelWriter(base_filename, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Все товары', index=False)
            
            # Форматируем
            worksheet = writer.sheets['Все товары']
            worksheet.column_dimensions['A'].width = 8   # №
            worksheet.column_dimensions['B'].width = 15  # ID товара
            worksheet.column_dimensions['C'].width = 60  # Название товара
            worksheet.column_dimensions['D'].width = 15  # Цена
            worksheet.column_dimensions['E'].width = 20  # Категория
            worksheet.column_dimensions['F'].width = 30  # URL источника
            worksheet.column_dimensions['G'].width = 20  # Дата парсинга
        
        print(f"\n✅ Все данные экспортированы в: {base_filename}")
        print(f"📁 Полный путь: {os.path.abspath(base_filename)}")
        print(f"📊 Всего товаров: {len(all_products)}")
        
        return base_filename
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None


def main():
    """Основная функция"""
    print("📊 Экспорт данных парсера в Excel")
    print("=" * 50)
    
    # URL для парсинга
    url = "https://www.amazon.com/s?k=shoes"
    
    print("Выберите режим:")
    print("1. Парсинг одного URL")
    print("2. Парсинг нескольких URL")
    print("3. Парсинг с настройками")
    
    choice = input("\nВведите номер (1-3): ").strip()
    
    if choice == "1":
        # Один URL
        asyncio.run(parse_and_export_to_excel(url))
        
    elif choice == "2":
        # Несколько URL
        urls = [
            "https://www.amazon.com/s?k=shoes",
            "https://www.amazon.com/s?k=sneakers",
            "https://www.amazon.com/s?k=boots"
        ]
        asyncio.run(parse_multiple_urls(urls))
        
    elif choice == "3":
        # Настройки
        custom_url = input("Введите URL: ").strip()
        if not custom_url:
            custom_url = url
        
        filename = input("Введите имя файла (или Enter для автогенерации): ").strip()
        if not filename:
            filename = None
        
        asyncio.run(parse_and_export_to_excel(custom_url, filename))
        
    else:
        print("❌ Неверный выбор")


if __name__ == "__main__":
    main()
