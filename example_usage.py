"""
Примеры использования парсера товаров
"""

from product_parser import ProductParser, parse_products
import asyncio


async def example_async_usage():
    """Пример асинхронного использования"""
    print("=== Асинхронный пример ===")
    
    # URL для тестирования (замените на реальный)
    test_urls = [
        "https://example.com/products",
        "https://httpbin.org/html",  # Тестовая страница
    ]
    
    async with ProductParser(headless=True) as parser:
        for url in test_urls:
            print(f"\nПарсим: {url}")
            try:
                products = await parser.parse(url)
                print(f"Найдено товаров: {len(products)}")
                for product in products[:3]:  # Показываем первые 3
                    print(f"  - {product['name']} ({product['price']})")
            except Exception as e:
                print(f"Ошибка: {e}")


def example_sync_usage():
    """Пример синхронного использования"""
    print("=== Синхронный пример ===")
    
    url = "https://example.com/products"
    print(f"Парсим: {url}")
    
    try:
        products = parse_products(url, headless=True)
        print(f"Найдено товаров: {len(products)}")
        
        for i, product in enumerate(products, 1):
            print(f"{i}. {product['name']} - {product['price']}")
            
    except Exception as e:
        print(f"Ошибка: {e}")


def example_custom_selectors():
    """Пример настройки под конкретный сайт"""
    print("=== Пример настройки селекторов ===")
    
    class CustomProductParser(ProductParser):
        """Парсер с настройками под конкретный сайт"""
        
        async def _wait_for_content(self, page):
            """Переопределяем ожидание контента для конкретного сайта"""
            try:
                # Ждем конкретные элементы сайта
                await page.wait_for_selector('.product-item', timeout=10000)
                return True
            except:
                return await super()._wait_for_content(page)
        
        async def _extract_product_data(self, element, page, index):
            """Переопределяем извлечение данных под конкретный сайт"""
            try:
                # Получаем ID из конкретного атрибута
                product_id = await element.get_attribute('data-product-id')
                if not product_id:
                    product_id = str(index + 1)
                
                # Получаем название из конкретного селектора
                name_element = await element.query_selector('.product-title')
                name = await name_element.inner_text() if name_element else f"Товар {product_id}"
                
                # Получаем цену из конкретного селектора
                price_element = await element.query_selector('.product-price')
                price_text = await price_element.inner_text() if price_element else ""
                price = self._extract_price(price_text) if price_text else "Цена не указана"
                
                return {
                    "id": product_id,
                    "name": name.strip(),
                    "price": price
                }
                
            except Exception as e:
                print(f"Ошибка извлечения данных: {e}")
                return None
    
    # Использование кастомного парсера
    print("Используйте CustomProductParser для настройки под конкретный сайт")


if __name__ == "__main__":
    print("Выберите пример:")
    print("1. Синхронное использование")
    print("2. Асинхронное использование") 
    print("3. Настройка под конкретный сайт")
    
    choice = input("Введите номер (1-3): ").strip()
    
    if choice == "1":
        example_sync_usage()
    elif choice == "2":
        asyncio.run(example_async_usage())
    elif choice == "3":
        example_custom_selectors()
    else:
        print("Неверный выбор")
