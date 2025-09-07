"""
Рабочий пример парсера с реальным сайтом
"""

from product_parser import parse_products
import asyncio
from product_parser import ProductParser


def test_with_real_site():
    """Тест с реальным сайтом"""
    print("=== Тест с реальным сайтом ===")
    
    # Используем сайт, который не блокирует ботов
    test_url = "https://quotes.toscrape.com/"
    
    print(f"Парсим: {test_url}")
    print("Этот сайт содержит цитаты, которые мы будем парсить как 'товары'")
    
    try:
        products = parse_products(test_url, headless=True)
        print(f"Найдено элементов: {len(products)}")
        
        for i, product in enumerate(products[:5], 1):
            print(f"{i}. ID: {product['id']}")
            print(f"   Название: {product['name'][:100]}{'...' if len(product['name']) > 100 else ''}")
            print(f"   Цена: {product['price']}")
            print()
            
    except Exception as e:
        print(f"Ошибка: {e}")


async def test_amazon_workaround():
    """Обход блокировки Amazon"""
    print("\n=== Обход блокировки Amazon ===")
    
    print("Для работы с Amazon нужно:")
    print("1. Использовать прокси-серверы")
    print("2. Добавить случайные задержки")
    print("3. Имитировать человеческое поведение")
    print("4. Ротировать User-Agent")
    
    # Пример кода для Amazon
    amazon_code = '''
# Пример кода для Amazon с обходом блокировки
import asyncio
import random
from product_parser import ProductParser

class AmazonWorkaroundParser(ProductParser):
    async def _setup_page(self, page):
        # Ротируем User-Agent
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        ]
        
        await page.set_extra_http_headers({
            'User-Agent': random.choice(user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        
        # Добавляем случайные задержки
        await asyncio.sleep(random.uniform(1, 3))
        
        # Имитируем человеческое поведение
        await page.mouse.move(random.randint(100, 500), random.randint(100, 500))
    
    async def parse(self, url):
        if not self.browser:
            await self._init_browser()
            
        page = await self.browser.new_page()
        await self._setup_page(page)
        
        try:
            await page.goto(url, timeout=60000)
            await asyncio.sleep(random.uniform(2, 5))
            
            # Ваша логика парсинга...
            
        finally:
            await page.close()

# Использование
async def main():
    async with AmazonWorkaroundParser(headless=False) as parser:
        products = await parser.parse("https://www.amazon.com/s?k=shoes")
        print(products)

asyncio.run(main())
    '''
    
    print("Пример кода:")
    print(amazon_code)


def show_usage_instructions():
    """Инструкции по использованию"""
    print("\n=== Как использовать парсер ===")
    print("""
1. БАЗОВОЕ ИСПОЛЬЗОВАНИЕ:
   ```python
   from product_parser import parse_products
   
   # Простой способ
   products = parse_products("https://your-site.com/products")
   print(products)
   ```

2. АСИНХРОННОЕ ИСПОЛЬЗОВАНИЕ:
   ```python
   import asyncio
   from product_parser import ProductParser
   
   async def main():
       async with ProductParser() as parser:
           products = await parser.parse("https://your-site.com/products")
           print(products)
   
   asyncio.run(main())
   ```

3. НАСТРОЙКА ПОД КОНКРЕТНЫЙ САЙТ:
   ```python
   from product_parser import ProductParser
   
   class MySiteParser(ProductParser):
       async def _wait_for_content(self, page):
           # Ждем загрузки товаров
           await page.wait_for_selector('.product-item', timeout=10000)
           return True
       
       async def _extract_product_data(self, element, page, index):
           # Извлекаем данные по структуре сайта
           name_el = await element.query_selector('.product-title')
           price_el = await element.query_selector('.product-price')
           
           return {
               "id": str(index + 1),
               "name": await name_el.inner_text() if name_el else "Товар",
               "price": await price_el.inner_text() if price_el else "Цена не указана"
           }
   ```

4. РАБОТА С AMAZON:
   - Используйте прокси-серверы
   - Добавляйте случайные задержки
   - Ротируйте User-Agent
   - Имитируйте человеческое поведение
   - Рассмотрите использование Selenium вместо Playwright

5. УСТАНОВКА И ЗАПУСК:
   ```bash
   # Установка зависимостей
   pip install -r requirements.txt
   
   # Установка браузеров
   playwright install
   
   # Запуск
   python product_parser.py
   ```
    """)


if __name__ == "__main__":
    print("🚀 Рабочий пример парсера товаров")
    print("=" * 50)
    
    # Тест с реальным сайтом
    test_with_real_site()
    
    # Обход блокировки Amazon
    asyncio.run(test_amazon_workaround())
    
    # Инструкции по использованию
    show_usage_instructions()
    
    print("\n✅ Готово! Парсер настроен и готов к использованию.")
    print("\nДля парсинга Amazon используйте обходные методы,")
    print("для других сайтов - стандартное использование.")
