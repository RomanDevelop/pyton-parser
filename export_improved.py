"""
Улучшенный экспорт данных парсера в Excel
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


async def parse_and_export_improved(url: str, filename: str = None):
    """
    Улучшенный парсинг и экспорт в Excel
    """
    
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"amazon_products_improved_{timestamp}.xlsx"
    
    print(f"🚀 Улучшенный парсинг: {url}")
    print(f"📊 Экспорт в Excel: {filename}")
    print("=" * 60)
    
    try:
        # Парсим товары с видимым браузером для лучшего извлечения
        async with AdvancedAmazonParser(headless=False) as parser:
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
        
        # Переименовываем колонки
        df.columns = ['№', 'ID товара', 'Название товара', 'Цена', 'Дата парсинга', 'URL источника']
        
        # Создаем Excel файл с форматированием
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # Основной лист с данными
            df.to_excel(writer, sheet_name='Товары Amazon', index=False)
            
            # Получаем объект workbook и worksheet
            workbook = writer.book
            worksheet = writer.sheets['Товары Amazon']
            
            # Настройка ширины колонок
            column_widths = {
                'A': 8,   # №
                'B': 15,  # ID товара
                'C': 80,  # Название товара
                'D': 20,  # Цена
                'E': 20,  # Дата парсинга
                'F': 40   # URL источника
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
                    f"~{len(products) * 3} секунд"
                ]
            }
            
            stats_df = pd.DataFrame(stats_data)
            stats_df.to_excel(writer, sheet_name='Статистика', index=False)
            
            # Форматируем лист статистики
            stats_worksheet = writer.sheets['Статистика']
            stats_worksheet.column_dimensions['A'].width = 30
            stats_worksheet.column_dimensions['B'].width = 40
            
            # Создаем лист с примерами товаров
            if len(products) > 0:
                examples_df = df.head(5).copy()
                examples_df.to_excel(writer, sheet_name='Примеры товаров', index=False)
                
                # Форматируем лист примеров
                examples_worksheet = writer.sheets['Примеры товаров']
                for col, width in column_widths.items():
                    examples_worksheet.column_dimensions[col].width = width
        
        print(f"✅ Данные успешно экспортированы в: {filename}")
        print(f"📁 Полный путь: {os.path.abspath(filename)}")
        
        # Показываем статистику
        print("\n📊 Статистика:")
        print(f"   • Всего товаров: {len(products)}")
        print(f"   • С ценой: {len([p for p in products if p['price'] != 'Цена не указана'])}")
        print(f"   • Без цены: {len([p for p in products if p['price'] == 'Цена не указана'])}")
        
        # Показываем все товары
        print("\n🔍 Все товары:")
        for i, product in enumerate(products, 1):
            print(f"   {i:2d}. {product['name'][:60]}{'...' if len(product['name']) > 60 else ''} - {product['price']}")
        
        return filename
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None


def main():
    """Основная функция"""
    print("📊 Улучшенный экспорт данных в Excel")
    print("=" * 50)
    
    # URL для парсинга
    url = "https://www.amazon.com/s?k=shoes"
    
    print(f"🎯 Парсинг: {url}")
    print("⚠️  Браузер откроется в видимом режиме для лучшего извлечения данных")
    print("⏳ Это займет 30-60 секунд...")
    print()
    
    input("Нажмите Enter для продолжения...")
    
    # Запускаем парсинг
    result = asyncio.run(parse_and_export_improved(url))
    
    if result:
        print(f"\n🎉 Готово! Excel файл создан: {result}")
        print("\n📋 Содержимое файла:")
        print("   • Лист 'Товары Amazon' - все товары")
        print("   • Лист 'Статистика' - статистика парсинга")
        print("   • Лист 'Примеры товаров' - первые 5 товаров")
        print("\n💡 Откройте файл в Excel или LibreOffice для просмотра")
    else:
        print("\n❌ Ошибка создания файла")


if __name__ == "__main__":
    main()
