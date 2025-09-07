"""
Быстрый экспорт данных парсера в Excel
"""

import pandas as pd
from amazon_advanced import AdvancedAmazonParser
import asyncio
from datetime import datetime
import os


async def quick_export(url: str = "https://www.amazon.com/s?k=shoes"):
    """
    Быстрый экспорт в Excel
    """
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"amazon_products_{timestamp}.xlsx"
    
    print(f"🚀 Быстрый экспорт: {url}")
    print(f"📊 Файл: {filename}")
    print("=" * 50)
    
    try:
        # Парсим товары
        async with AdvancedAmazonParser(headless=True) as parser:
            products = await parser.parse(url)
        
        if not products:
            print("❌ Товары не найдены")
            return None
        
        # Создаем DataFrame
        df = pd.DataFrame(products)
        df['Дата'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        df['№'] = range(1, len(df) + 1)
        
        # Переупорядочиваем колонки
        df = df[['№', 'id', 'name', 'price', 'Дата']]
        df.columns = ['№', 'ID товара', 'Название', 'Цена', 'Дата парсинга']
        
        # Экспортируем в Excel
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Товары', index=False)
            
            # Настраиваем ширину колонок
            worksheet = writer.sheets['Товары']
            worksheet.column_dimensions['A'].width = 8   # №
            worksheet.column_dimensions['B'].width = 15  # ID
            worksheet.column_dimensions['C'].width = 80  # Название
            worksheet.column_dimensions['D'].width = 20  # Цена
            worksheet.column_dimensions['E'].width = 20  # Дата
        
        print(f"✅ Готово! Файл: {filename}")
        print(f"📁 Путь: {os.path.abspath(filename)}")
        print(f"📊 Товаров: {len(products)}")
        
        # Показываем товары
        print("\n🔍 Товары:")
        for i, product in enumerate(products, 1):
            print(f"   {i:2d}. {product['name'][:50]}{'...' if len(product['name']) > 50 else ''} - ${product['price']}")
        
        return filename
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None


if __name__ == "__main__":
    print("📊 Быстрый экспорт в Excel")
    print("=" * 30)
    
    # Можно изменить URL
    url = input("Введите URL (или Enter для Amazon shoes): ").strip()
    if not url:
        url = "https://www.amazon.com/s?k=shoes"
    
    result = asyncio.run(quick_export(url))
    
    if result:
        print(f"\n🎉 Excel файл создан: {result}")
        print("💡 Откройте файл в Excel для просмотра")
    else:
        print("\n❌ Ошибка создания файла")
