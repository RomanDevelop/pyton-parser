"""
Специализированный парсер для Amazon
Настроен под структуру товаров Amazon
"""

import asyncio
from product_parser import ProductParser
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AmazonProductParser(ProductParser):
    """
    Парсер товаров специально для Amazon
    Настроен под структуру и селекторы Amazon
    """
    
    def __init__(self, headless: bool = True, timeout: int = 30000):
        super().__init__(headless, timeout)
    
    async def _wait_for_content(self, page):
        """Ожидание загрузки товаров Amazon"""
        try:
            # Ждем появления товаров Amazon - пробуем разные селекторы
            selectors = [
                '[data-component-type="s-search-result"]',
                '.s-result-item',
                '[data-asin]',
                '.s-search-result',
                '[cel_widget_id*="MAIN-SEARCH_RESULTS"]'
            ]
            
            for selector in selectors:
                try:
                    await page.wait_for_selector(selector, timeout=5000)
                    logger.info(f"Товары Amazon найдены по селектору: {selector}")
                    return True
                except:
                    continue
            
            # Если ничего не нашли, ждем общую загрузку
            await page.wait_for_load_state('networkidle', timeout=10000)
            logger.info("Страница загружена, ищем товары...")
            return True
            
        except Exception as e:
            logger.warning(f"Не удалось найти товары Amazon: {e}")
            return await super()._wait_for_content(page)
    
    async def _extract_product_data(self, element, page, index):
        """Извлечение данных товара Amazon"""
        try:
            # ID товара из data-asin атрибута
            product_id = await element.get_attribute('data-asin')
            if not product_id:
                # Пробуем найти в ссылке
                link_element = await element.query_selector('h2 a')
                if link_element:
                    href = await link_element.get_attribute('href')
                    if href and '/dp/' in href:
                        product_id = href.split('/dp/')[1].split('/')[0]
            
            if not product_id:
                product_id = f"amazon_{index + 1}"
            
            # Название товара
            name = ""
            name_selectors = [
                'h2 a span',  # Основной селектор названия
                'h2 span',    # Альтернативный
                '[data-cy="title-recipe-title"] span',
                '.s-size-mini .s-link-style .s-color-base'
            ]
            
            for selector in name_selectors:
                try:
                    name_element = await element.query_selector(selector)
                    if name_element:
                        name = await name_element.inner_text()
                        if name and name.strip():
                            break
                except:
                    continue
            
            if not name:
                name = f"Товар Amazon {product_id}"
            
            # Цена товара
            price = ""
            price_selectors = [
                '.a-price-whole',  # Основная цена
                '.a-price .a-offscreen',  # Цена в offscreen
                '.a-price-range',  # Диапазон цен
                '[data-cy="price-recipe"] .a-price .a-offscreen',
                '.a-price-symbol + .a-price-whole',
                '.a-price .a-price-whole'
            ]
            
            for selector in price_selectors:
                try:
                    price_element = await element.query_selector(selector)
                    if price_element:
                        price_text = await price_element.inner_text()
                        if price_text and price_text.strip():
                            price = self._extract_price(price_text)
                            if price:
                                break
                except:
                    continue
            
            # Если не нашли цену, пробуем найти в data-атрибутах
            if not price:
                price_attrs = ['data-price', 'data-asin-price']
                for attr in price_attrs:
                    try:
                        price_value = await element.get_attribute(attr)
                        if price_value:
                            price = self._extract_price(price_value)
                            if price:
                                break
                    except:
                        continue
            
            # Если цена не найдена, пробуем найти текст с ценой
            if not price:
                try:
                    price_container = await element.query_selector('.a-price')
                    if price_container:
                        price_text = await price_container.inner_text()
                        price = self._extract_price(price_text)
                except:
                    pass
            
            return {
                "id": product_id,
                "name": name.strip(),
                "price": price or "Цена не указана"
            }
            
        except Exception as e:
            logger.error(f"Ошибка извлечения данных товара Amazon: {e}")
            return None


async def parse_amazon_products(url: str, headless: bool = True):
    """
    Парсинг товаров с Amazon
    
    Args:
        url: URL страницы Amazon с товарами
        headless: Запускать браузер в фоновом режиме
        
    Returns:
        Список товаров
    """
    async with AmazonProductParser(headless=headless) as parser:
        return await parser.parse(url)


def parse_amazon_sync(url: str, headless: bool = True):
    """
    Синхронная версия парсинга Amazon
    
    Args:
        url: URL страницы Amazon с товарами
        headless: Запускать браузер в фоновом режиме
        
    Returns:
        Список товаров
    """
    return asyncio.run(parse_amazon_products(url, headless))


if __name__ == "__main__":
    # URL для парсинга обуви на Amazon
    amazon_url = "https://www.amazon.com/s?k=shoes"
    
    print("=== Парсер товаров Amazon ===")
    print(f"Парсим: {amazon_url}")
    print("Это может занять некоторое время...")
    
    try:
        products = parse_amazon_sync(amazon_url, headless=True)
        
        if products:
            print(f"\n✅ Найдено товаров: {len(products)}")
            print("\n📦 Результат:")
            print("-" * 80)
            
            for i, product in enumerate(products[:10], 1):  # Показываем первые 10
                print(f"{i:2d}. ID: {product['id']}")
                print(f"    Название: {product['name'][:80]}{'...' if len(product['name']) > 80 else ''}")
                print(f"    Цена: {product['price']}")
                print()
            
            if len(products) > 10:
                print(f"... и еще {len(products) - 10} товаров")
                
        else:
            print("❌ Товары не найдены")
            print("Возможные причины:")
            print("- Amazon заблокировал запрос")
            print("- Изменилась структура страницы")
            print("- Нужно настроить селекторы")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        print("\nВозможные решения:")
        print("1. Проверьте интернет-соединение")
        print("2. Попробуйте другой URL")
        print("3. Запустите с headless=False для отладки")
