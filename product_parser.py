"""
Универсальный парсер товаров с динамических сайтов
Поддерживает JavaScript-контент через Playwright
"""

import asyncio
import re
from typing import List, Dict, Optional, Any
from playwright.async_api import async_playwright, Browser, Page
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProductParser:
    """
    Универсальный парсер товаров с динамических сайтов
    
    Использует Playwright для загрузки JavaScript-контента
    и извлечения информации о товарах с публичных страниц
    """
    
    def __init__(self, headless: bool = True, timeout: int = 30000):
        """
        Инициализация парсера
        
        Args:
            headless: Запускать браузер в фоновом режиме
            timeout: Таймаут загрузки страницы в миллисекундах
        """
        self.headless = headless
        self.timeout = timeout
        self.browser: Optional[Browser] = None
        
    async def __aenter__(self):
        """Асинхронный контекстный менеджер - вход"""
        await self._init_browser()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Асинхронный контекстный менеджер - выход"""
        await self._close_browser()
    
    async def _init_browser(self):
        """Инициализация браузера Playwright"""
        try:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=self.headless,
                args=['--no-sandbox', '--disable-dev-shm-usage']
            )
            logger.info("Браузер успешно инициализирован")
        except Exception as e:
            logger.error(f"Ошибка инициализации браузера: {e}")
            raise
    
    async def _close_browser(self):
        """Закрытие браузера"""
        try:
            if self.browser:
                await self.browser.close()
            if hasattr(self, 'playwright'):
                await self.playwright.stop()
            logger.info("Браузер закрыт")
        except Exception as e:
            logger.error(f"Ошибка закрытия браузера: {e}")
    
    def _extract_price(self, price_text: str) -> Optional[str]:
        """
        Извлечение и нормализация цены из текста
        
        Args:
            price_text: Сырой текст с ценой
            
        Returns:
            Нормализованная цена или None
        """
        if not price_text:
            return None
            
        # Удаляем все символы кроме цифр, точек, запятых и пробелов
        cleaned = re.sub(r'[^\d.,\s]', '', price_text.strip())
        
        # Ищем числа с разделителями
        price_match = re.search(r'[\d.,]+', cleaned)
        if price_match:
            price = price_match.group()
            # Заменяем запятую на точку для унификации
            price = price.replace(',', '.')
            return price
            
        return None
    
    async def _extract_id(self, element: Any, page: Page) -> Optional[str]:
        """
        Извлечение ID товара из различных атрибутов
        
        Args:
            element: Элемент товара
            page: Страница Playwright
            
        Returns:
            ID товара или None
        """
        # Список возможных атрибутов для ID
        id_attributes = [
            'data-id', 'data-product-id', 'data-item-id', 'id',
            'data-sku', 'data-code', 'data-product-code'
        ]
        
        for attr in id_attributes:
            try:
                id_value = await element.get_attribute(attr)
                if id_value and id_value.strip():
                    return id_value.strip()
            except:
                continue
                
        return None
    
    async def _wait_for_content(self, page: Page) -> bool:
        """
        Ожидание загрузки контента товаров
        
        Args:
            page: Страница Playwright
            
        Returns:
            True если контент загружен, False иначе
        """
        try:
            # Ждем появления хотя бы одного товара
            # Можно настроить под конкретный сайт
            await page.wait_for_selector(
                '[data-testid*="product"], .product, .item, [class*="product"], [class*="item"]',
                timeout=10000
            )
            return True
        except:
            # Если не нашли товары, ждем общую загрузку
            try:
                await page.wait_for_load_state('networkidle', timeout=5000)
                return True
            except:
                return False
    
    async def parse(self, url: str) -> List[Dict[str, str]]:
        """
        Основной метод парсинга товаров
        
        Args:
            url: URL страницы с товарами
            
        Returns:
            Список словарей с информацией о товарах
        """
        if not self.browser:
            await self._init_browser()
            
        products = []
        
        try:
            # Создаем новую страницу
            page = await self.browser.new_page()
            
            # Устанавливаем User-Agent для избежания блокировок
            await page.set_extra_http_headers({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            })
            
            logger.info(f"Загружаем страницу: {url}")
            
            # Переходим на страницу
            await page.goto(url, timeout=self.timeout)
            
            # Ждем загрузки контента
            await self._wait_for_content(page)
            
            # Список возможных селекторов для товаров
            # Можно настроить под конкретный сайт
            product_selectors = [
                '[data-testid*="product"]',
                '.product',
                '.item',
                '[class*="product"]',
                '[class*="item"]',
                '.product-item',
                '.product-card',
                '.goods-item',
                '.catalog-item'
            ]
            
            product_elements = []
            
            # Пробуем найти товары по разным селекторам
            for selector in product_selectors:
                try:
                    elements = await page.query_selector_all(selector)
                    if elements:
                        product_elements = elements
                        logger.info(f"Найдено {len(elements)} товаров по селектору: {selector}")
                        break
                except Exception as e:
                    logger.debug(f"Селектор {selector} не сработал: {e}")
                    continue
            
            if not product_elements:
                logger.warning("Товары не найдены на странице")
                return products
            
            # Извлекаем информацию о каждом товаре
            for i, element in enumerate(product_elements):
                try:
                    product_data = await self._extract_product_data(element, page, i)
                    if product_data:
                        products.append(product_data)
                except Exception as e:
                    logger.error(f"Ошибка извлечения данных товара {i}: {e}")
                    continue
            
            logger.info(f"Успешно извлечено {len(products)} товаров")
            
        except Exception as e:
            logger.error(f"Ошибка парсинга страницы {url}: {e}")
            
        finally:
            if 'page' in locals():
                await page.close()
                
        return products
    
    async def _extract_product_data(self, element: Any, page: Page, index: int) -> Optional[Dict[str, str]]:
        """
        Извлечение данных конкретного товара
        
        Args:
            element: Элемент товара
            page: Страница Playwright
            index: Индекс товара (для fallback ID)
            
        Returns:
            Словарь с данными товара или None
        """
        try:
            # Извлекаем ID товара
            product_id = await self._extract_id(element, page)
            if not product_id:
                product_id = str(index + 1)  # Fallback ID
            
            # Извлекаем название товара
            name = await self._extract_text_by_selectors(element, [
                'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
                '.title', '.name', '.product-name', '.item-name',
                '[class*="title"]', '[class*="name"]',
                'a[title]', '[data-testid*="title"]', '[data-testid*="name"]'
            ])
            
            if not name:
                name = f"Товар {product_id}"
            
            # Извлекаем цену
            price = await self._extract_text_by_selectors(element, [
                '.price', '.cost', '.value', '.amount',
                '[class*="price"]', '[class*="cost"]',
                '[data-testid*="price"]', '[data-testid*="cost"]',
                '.currency', '.money'
            ])
            
            price = self._extract_price(price) if price else None
            
            # Если цена не найдена, пробуем найти в data-атрибутах
            if not price:
                price_attrs = ['data-price', 'data-cost', 'data-value', 'data-amount']
                for attr in price_attrs:
                    try:
                        price_value = await element.get_attribute(attr)
                        if price_value:
                            price = self._extract_price(price_value)
                            if price:
                                break
                    except:
                        continue
            
            return {
                "id": product_id,
                "name": name.strip(),
                "price": price or "Цена не указана"
            }
            
        except Exception as e:
            logger.error(f"Ошибка извлечения данных товара: {e}")
            return None
    
    async def _extract_text_by_selectors(self, element: Any, selectors: List[str]) -> Optional[str]:
        """
        Извлечение текста по списку селекторов
        
        Args:
            element: Родительский элемент
            selectors: Список CSS селекторов
            
        Returns:
            Найденный текст или None
        """
        for selector in selectors:
            try:
                sub_element = await element.query_selector(selector)
                if sub_element:
                    text = await sub_element.inner_text()
                    if text and text.strip():
                        return text.strip()
            except:
                continue
        return None


# Синхронная обертка для удобства использования
def parse_products(url: str, headless: bool = True) -> List[Dict[str, str]]:
    """
    Синхронная функция для парсинга товаров
    
    Args:
        url: URL страницы с товарами
        headless: Запускать браузер в фоновом режиме
        
    Returns:
        Список словарей с информацией о товарах
    """
    async def _parse():
        async with ProductParser(headless=headless) as parser:
            return await parser.parse(url)
    
    return asyncio.run(_parse())


if __name__ == "__main__":
    # Пример использования
    print("=== Универсальный парсер товаров ===")
    print("Введите URL сайта с товарами (или нажмите Enter для тестового URL):")
    
    url = input().strip()
    if not url:
        # Тестовый URL (можно заменить на реальный)
        url = "https://example.com/products"
        print(f"Используем тестовый URL: {url}")
    
    try:
        print(f"\nПарсим товары с: {url}")
        print("Это может занять некоторое время...")
        
        products = parse_products(url, headless=True)
        
        if products:
            print(f"\nНайдено товаров: {len(products)}")
            print("\nРезультат:")
            for i, product in enumerate(products, 1):
                print(f"{i}. ID: {product['id']}")
                print(f"   Название: {product['name']}")
                print(f"   Цена: {product['price']}")
                print()
        else:
            print("Товары не найдены. Возможно, нужно настроить селекторы под конкретный сайт.")
            
    except Exception as e:
        print(f"Ошибка: {e}")
        print("\nУбедитесь, что установлены зависимости:")
        print("pip install playwright")
        print("playwright install")
