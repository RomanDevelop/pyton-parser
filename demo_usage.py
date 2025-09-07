"""
Демонстрация использования парсера товаров
"""

from product_parser import parse_products
import asyncio
from product_parser import ProductParser


def demo_simple_usage():
    """Простое использование парсера"""
    print("=== Простое использование ===")
    
    # Пример с тестовым сайтом
    test_urls = [
        "https://httpbin.org/html",  # Тестовая страница
        "https://example.com",       # Простая страница
    ]
    
    for url in test_urls:
        print(f"\nПарсим: {url}")
        try:
            products = parse_products(url, headless=True)
            print(f"Найдено товаров: {len(products)}")
            
            for i, product in enumerate(products[:3], 1):
                print(f"  {i}. {product['name']} - {product['price']}")
                
        except Exception as e:
            print(f"Ошибка: {e}")


async def demo_async_usage():
    """Асинхронное использование"""
    print("\n=== Асинхронное использование ===")
    
    test_url = "https://httpbin.org/html"
    
    async with ProductParser(headless=True) as parser:
        print(f"Парсим: {test_url}")
        try:
            products = await parser.parse(test_url)
            print(f"Найдено товаров: {len(products)}")
            
            for i, product in enumerate(products[:3], 1):
                print(f"  {i}. {product['name']} - {product['price']}")
                
        except Exception as e:
            print(f"Ошибка: {e}")


def demo_amazon_instructions():
    """Инструкции для Amazon"""
    print("\n=== Как использовать с Amazon ===")
    print("""
Amazon блокирует автоматизированные запросы, но вы можете:

1. Использовать прокси-серверы:
   ```python
   from product_parser import ProductParser
   
   async with ProductParser(headless=True) as parser:
       # Настройка прокси
       page = await parser.browser.new_page()
       await page.route("**/*", lambda route: route.continue_())
       await page.goto("https://www.amazon.com/s?k=shoes")
   ```

2. Добавить задержки и случайные действия:
   ```python
   import random
   import asyncio
   
   # Случайная задержка
   await asyncio.sleep(random.uniform(1, 3))
   
   # Имитация человеческого поведения
   await page.mouse.move(100, 100)
   await page.mouse.click(100, 100)
   ```

3. Использовать ротацию User-Agent:
   ```python
   user_agents = [
       'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
       'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
       'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
   ]
   ```

4. Настроить селекторы под конкретный сайт:
   ```python
   class CustomAmazonParser(ProductParser):
       async def _wait_for_content(self, page):
           # Ждем конкретные элементы Amazon
           await page.wait_for_selector('[data-asin]', timeout=15000)
           return True
   ```
    """)


def demo_other_sites():
    """Примеры для других сайтов"""
    print("\n=== Примеры для других сайтов ===")
    print("""
Парсер работает с любыми сайтами. Вот примеры:

1. Интернет-магазины:
   - https://example-shop.com/products
   - https://store.example.com/catalog

2. Маркетплейсы:
   - https://marketplace.com/search?q=shoes
   - https://shop.example.com/category/shoes

3. Каталоги товаров:
   - https://catalog.example.com/items
   - https://products.example.com/list

Использование:
```python
from product_parser import parse_products

# Простое использование
products = parse_products("https://your-site.com/products")

# С настройками
products = parse_products("https://your-site.com/products", headless=False)
```

Настройка под конкретный сайт:
```python
from product_parser import ProductParser

class MySiteParser(ProductParser):
    async def _wait_for_content(self, page):
        # Ждем загрузки товаров вашего сайта
        await page.wait_for_selector('.product-item', timeout=10000)
        return True
    
    async def _extract_product_data(self, element, page, index):
        # Извлекаем данные по структуре вашего сайта
        name = await element.query_selector('.product-title')
        price = await element.query_selector('.product-price')
        
        return {
            "id": str(index + 1),
            "name": await name.inner_text() if name else "Товар",
            "price": await price.inner_text() if price else "Цена не указана"
        }
```
    """)


if __name__ == "__main__":
    print("🚀 Демонстрация парсера товаров")
    print("=" * 50)
    
    # Простое использование
    demo_simple_usage()
    
    # Асинхронное использование
    asyncio.run(demo_async_usage())
    
    # Инструкции для Amazon
    demo_amazon_instructions()
    
    # Примеры для других сайтов
    demo_other_sites()
    
    print("\n✅ Демонстрация завершена!")
    print("\nДля использования с реальными сайтами:")
    print("1. Установите зависимости: pip install -r requirements.txt")
    print("2. Установите браузеры: playwright install")
    print("3. Запустите: python product_parser.py")
