"""
Простой тест парсера Amazon
"""

import asyncio
from product_parser import ProductParser
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_amazon():
    """Тест парсинга Amazon"""
    
    # URL Amazon
    url = "https://www.amazon.com/s?k=shoes"
    
    print("=== Тест парсера Amazon ===")
    print(f"URL: {url}")
    print("Запускаем браузер в видимом режиме для отладки...")
    
    try:
        # Создаем парсер с видимым браузером
        async with ProductParser(headless=False, timeout=60000) as parser:
            print("Браузер запущен, загружаем страницу...")
            
            # Переходим на страницу
            page = await parser.browser.new_page()
            
            # Устанавливаем User-Agent
            await page.set_extra_http_headers({
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            })
            
            # Переходим на страницу
            await page.goto(url, timeout=60000)
            
            print("Страница загружена, ждем контент...")
            
            # Ждем загрузки
            await page.wait_for_load_state('networkidle', timeout=30000)
            
            print("Ищем товары...")
            
            # Ищем товары по разным селекторам
            selectors_to_try = [
                '[data-component-type="s-search-result"]',
                '.s-result-item',
                '[data-asin]',
                '.s-search-result',
                '[cel_widget_id*="MAIN-SEARCH_RESULTS"]',
                '.s-widget-container',
                '[data-testid*="product"]'
            ]
            
            products_found = []
            
            for selector in selectors_to_try:
                try:
                    elements = await page.query_selector_all(selector)
                    if elements:
                        print(f"✅ Найдено {len(elements)} элементов по селектору: {selector}")
                        products_found = elements
                        break
                    else:
                        print(f"❌ Селектор {selector} не дал результатов")
                except Exception as e:
                    print(f"❌ Ошибка с селектором {selector}: {e}")
            
            if not products_found:
                print("❌ Товары не найдены")
                
                # Показываем HTML для отладки
                print("\nПроверяем содержимое страницы...")
                content = await page.content()
                print(f"Размер HTML: {len(content)} символов")
                
                # Ищем ключевые слова
                if "captcha" in content.lower():
                    print("⚠️  Обнаружена CAPTCHA - Amazon заблокировал запрос")
                elif "robot" in content.lower():
                    print("⚠️  Обнаружена защита от ботов")
                elif "shoes" in content.lower():
                    print("✅ Слово 'shoes' найдено в контенте")
                else:
                    print("❓ Неизвестная проблема")
                
                return []
            
            print(f"\n📦 Извлекаем данные из {len(products_found)} товаров...")
            
            # Извлекаем данные из первых 5 товаров
            products = []
            for i, element in enumerate(products_found[:5]):
                try:
                    # ID
                    asin = await element.get_attribute('data-asin')
                    if not asin:
                        asin = f"item_{i+1}"
                    
                    # Название
                    name = "Товар не найден"
                    name_selectors = ['h2 a span', 'h2 span', '[data-cy="title-recipe-title"] span']
                    for ns in name_selectors:
                        try:
                            name_el = await element.query_selector(ns)
                            if name_el:
                                name = await name_el.inner_text()
                                if name and name.strip():
                                    break
                        except:
                            continue
                    
                    # Цена
                    price = "Цена не найдена"
                    price_selectors = ['.a-price-whole', '.a-price .a-offscreen', '.a-price-range']
                    for ps in price_selectors:
                        try:
                            price_el = await element.query_selector(ps)
                            if price_el:
                                price_text = await price_el.inner_text()
                                if price_text and price_text.strip():
                                    price = price_text.strip()
                                    break
                        except:
                            continue
                    
                    product = {
                        "id": asin,
                        "name": name.strip(),
                        "price": price
                    }
                    products.append(product)
                    
                    print(f"{i+1}. {name[:50]}... - {price}")
                    
                except Exception as e:
                    print(f"Ошибка извлечения товара {i+1}: {e}")
                    continue
            
            await page.close()
            return products
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return []


if __name__ == "__main__":
    print("Запуск теста Amazon...")
    print("Браузер откроется в видимом режиме")
    print("Нажмите Enter для продолжения...")
    input()
    
    products = asyncio.run(test_amazon())
    
    if products:
        print(f"\n✅ Успешно извлечено {len(products)} товаров:")
        for i, product in enumerate(products, 1):
            print(f"{i}. ID: {product['id']}")
            print(f"   Название: {product['name']}")
            print(f"   Цена: {product['price']}")
            print()
    else:
        print("\n❌ Товары не найдены")
