"""
Итоговый отчет по парсингу Amazon
"""

import pandas as pd
import os
from datetime import datetime

def analyze_excel_files():
    """Анализ созданных Excel файлов"""
    
    print("📊 ИТОГОВЫЙ ОТЧЕТ ПО ПАРСИНГУ AMAZON")
    print("=" * 60)
    
    # Находим все Excel файлы
    excel_files = [f for f in os.listdir('.') if f.endswith('.xlsx')]
    
    if not excel_files:
        print("❌ Excel файлы не найдены")
        return
    
    print(f"📁 Найдено Excel файлов: {len(excel_files)}")
    print()
    
    # Анализируем каждый файл
    for i, filename in enumerate(excel_files, 1):
        print(f"📋 Файл {i}: {filename}")
        print("-" * 40)
        
        try:
            # Читаем Excel файл
            df = pd.read_excel(filename, sheet_name=0)
            
            print(f"   📊 Товаров в файле: {len(df)}")
            print(f"   📅 Дата создания: {os.path.getctime(filename)}")
            print(f"   💾 Размер файла: {os.path.getsize(filename)} байт")
            
            # Показываем первые 3 товара
            if len(df) > 0:
                print("   🔍 Первые товары:")
                for idx, row in df.head(3).iterrows():
                    name = row.get('Название товара', row.get('Название', 'Неизвестно'))
                    price = row.get('Цена', 'Не указана')
                    print(f"      {idx+1}. {name[:50]}{'...' if len(str(name)) > 50 else ''} - {price}")
            
            print()
            
        except Exception as e:
            print(f"   ❌ Ошибка чтения файла: {e}")
            print()
    
    # Создаем сводный отчет
    print("📈 СВОДНЫЙ ОТЧЕТ")
    print("=" * 30)
    
    all_products = []
    for filename in excel_files:
        try:
            df = pd.read_excel(filename, sheet_name=0)
            all_products.extend(df.to_dict('records'))
        except:
            continue
    
    if all_products:
        print(f"📊 Общее количество товаров: {len(all_products)}")
        
        # Статистика по ценам
        prices = [p.get('Цена', p.get('price', '')) for p in all_products]
        valid_prices = [p for p in prices if p and str(p).replace('$', '').replace('.', '').isdigit()]
        
        print(f"💰 Товаров с ценой: {len(valid_prices)}")
        print(f"❌ Товаров без цены: {len(all_products) - len(valid_prices)}")
        
        # Топ брендов
        brands = {}
        for product in all_products:
            name = str(product.get('Название товара', product.get('name', '')))
            if 'adidas' in name.lower():
                brands['adidas'] = brands.get('adidas', 0) + 1
            elif 'nike' in name.lower():
                brands['Nike'] = brands.get('Nike', 0) + 1
            elif 'skechers' in name.lower():
                brands['Skechers'] = brands.get('Skechers', 0) + 1
            elif 'new balance' in name.lower():
                brands['New Balance'] = brands.get('New Balance', 0) + 1
            elif 'under armour' in name.lower():
                brands['Under Armour'] = brands.get('Under Armour', 0) + 1
        
        if brands:
            print("\n🏷️ Топ брендов:")
            for brand, count in sorted(brands.items(), key=lambda x: x[1], reverse=True):
                print(f"   {brand}: {count} товаров")
        
        # Диапазон цен
        if valid_prices:
            price_values = []
            for price in valid_prices:
                try:
                    price_str = str(price).replace('$', '').replace(',', '')
                    if price_str.isdigit():
                        price_values.append(int(price_str))
                except:
                    continue
            
            if price_values:
                print(f"\n💵 Диапазон цен:")
                print(f"   Минимальная: ${min(price_values)}")
                print(f"   Максимальная: ${max(price_values)}")
                print(f"   Средняя: ${sum(price_values) // len(price_values)}")
    
    print("\n✅ Анализ завершен!")
    print(f"📁 Все файлы находятся в: {os.path.abspath('.')}")


def create_summary_excel():
    """Создание сводного Excel файла"""
    
    print("\n📊 Создание сводного Excel файла...")
    
    # Находим все Excel файлы
    excel_files = [f for f in os.listdir('.') if f.endswith('.xlsx')]
    
    if not excel_files:
        print("❌ Excel файлы не найдены")
        return
    
    all_products = []
    for filename in excel_files:
        try:
            df = pd.read_excel(filename, sheet_name=0)
            for _, row in df.iterrows():
                product = row.to_dict()
                product['Источник файла'] = filename
                all_products.append(product)
        except:
            continue
    
    if not all_products:
        print("❌ Данные не найдены")
        return
    
    # Создаем сводный DataFrame
    df = pd.DataFrame(all_products)
    
    # Удаляем дубликаты по ID товара
    if 'ID товара' in df.columns:
        df = df.drop_duplicates(subset=['ID товара'], keep='first')
    
    # Создаем сводный файл
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    summary_filename = f"amazon_summary_{timestamp}.xlsx"
    
    with pd.ExcelWriter(summary_filename, engine='openpyxl') as writer:
        # Основные данные
        df.to_excel(writer, sheet_name='Все товары', index=False)
        
        # Статистика
        stats_data = {
            'Параметр': [
                'Общее количество товаров',
                'Уникальных товаров',
                'Файлов обработано',
                'Дата создания отчета',
                'Источник данных'
            ],
            'Значение': [
                len(all_products),
                len(df),
                len(excel_files),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'https://www.amazon.com/s?k=shoes'
            ]
        }
        
        stats_df = pd.DataFrame(stats_data)
        stats_df.to_excel(writer, sheet_name='Статистика', index=False)
        
        # Форматируем
        for sheet_name in writer.sheets:
            worksheet = writer.sheets[sheet_name]
            worksheet.column_dimensions['A'].width = 30
            worksheet.column_dimensions['B'].width = 40
    
    print(f"✅ Сводный файл создан: {summary_filename}")
    print(f"📁 Путь: {os.path.abspath(summary_filename)}")
    print(f"📊 Товаров в сводном файле: {len(df)}")


if __name__ == "__main__":
    # Анализируем файлы
    analyze_excel_files()
    
    # Создаем сводный файл
    create_summary_excel()
    
    print("\n🎉 ОТЧЕТ ЗАВЕРШЕН!")
    print("📊 Excel файлы готовы к использованию")
    print("💡 Откройте файлы в Excel для детального просмотра")
