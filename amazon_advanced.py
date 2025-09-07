"""
Продвинутый парсер Amazon с обходом блокировки
"""

import asyncio
import random
import time
from product_parser import ProductParser
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AdvancedAmazonParser(ProductParser):
    """
    Продвинутый парсер Amazon с методами обхода блокировки
    """
    
    def __init__(self, headless: bool = False, timeout: int = 60000):
        super().__init__(headless, timeout)
        self.user_agents = [
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0'
        ]
    
    async def _setup_page(self, page):
        """Настройка страницы для обхода блокировки"""
        # Случайный User-Agent
        user_agent = random.choice(self.user_agents)
        
        # Устанавливаем заголовки
        await page.set_extra_http_headers({
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,ru;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0'
        })
        
        # Устанавливаем viewport
        await page.set_viewport_size({"width": 1920, "height": 1080})
        
        # Блокируем ненужные ресурсы для ускорения
        await page.route("**/*.{png,jpg,jpeg,gif,svg,ico,woff,woff2,ttf,eot}", lambda route: route.abort())
        await page.route("**/ads/**", lambda route: route.abort())
        await page.route("**/analytics/**", lambda route: route.abort())
    
    async def _human_like_behavior(self, page):
        """Имитация человеческого поведения"""
        try:
            # Случайные движения мыши
            for _ in range(random.randint(2, 5)):
                x = random.randint(100, 1800)
                y = random.randint(100, 1000)
                await page.mouse.move(x, y)
                await asyncio.sleep(random.uniform(0.1, 0.3))
            
            # Случайный скролл
            await page.mouse.wheel(0, random.randint(100, 500))
            await asyncio.sleep(random.uniform(0.5, 1.5))
            
            # Случайный клик
            if random.random() < 0.3:
                x = random.randint(200, 1600)
                y = random.randint(200, 800)
                await page.mouse.click(x, y)
                await asyncio.sleep(random.uniform(0.5, 1.0))
                
        except Exception as e:
            logger.debug(f"Ошибка имитации поведения: {e}")
    
    async def _wait_for_content(self, page):
        """Ожидание загрузки товаров Amazon с множественными попытками"""
        selectors = [
            '[data-component-type="s-search-result"]',
            '.s-result-item',
            '[data-asin]',
            '.s-search-result',
            '[cel_widget_id*="MAIN-SEARCH_RESULTS"]',
            '.s-widget-container',
            '[data-testid*="product"]'
        ]
        
        for attempt in range(3):
            try:
                logger.info(f"Попытка {attempt + 1} поиска товаров...")
                
                # Имитируем человеческое поведение
                await self._human_like_behavior(page)
                
                # Пробуем разные селекторы
                for selector in selectors:
                    try:
                        await page.wait_for_selector(selector, timeout=5000)
                        logger.info(f"✅ Товары найдены по селектору: {selector}")
                        return True
                    except:
                        continue
                
                # Ждем общую загрузку
                await page.wait_for_load_state('networkidle', timeout=10000)
                
                # Проверяем наличие товаров
                for selector in selectors:
                    elements = await page.query_selector_all(selector)
                    if elements:
                        logger.info(f"✅ Найдено {len(elements)} товаров по селектору: {selector}")
                        return True
                
                # Случайная задержка перед следующей попыткой
                await asyncio.sleep(random.uniform(2, 5))
                
            except Exception as e:
                logger.warning(f"Попытка {attempt + 1} не удалась: {e}")
                if attempt < 2:
                    await asyncio.sleep(random.uniform(3, 7))
        
        logger.warning("Не удалось найти товары после всех попыток")
        return False
    
    async def parse(self, url: str) -> list:
        """Парсинг с обходом блокировки"""
        if not self.browser:
            await self._init_browser()
        
        products = []
        
        try:
            # Создаем страницу
            page = await self.browser.new_page()
            await self._setup_page(page)
            
            logger.info(f"🌐 Загружаем: {url}")
            
            # Переходим на страницу
            await page.goto(url, timeout=self.timeout)
            
            # Случайная задержка
            await asyncio.sleep(random.uniform(2, 4))
            
            # Имитируем человеческое поведение
            await self._human_like_behavior(page)
            
            # Ждем загрузки контента
            if not await self._wait_for_content(page):
                logger.warning("Контент не загружен, но продолжаем...")
            
            # Ищем товары
            product_selectors = [
                '[data-component-type="s-search-result"]',
                '.s-result-item',
                '[data-asin]',
                '.s-search-result'
            ]
            
            product_elements = []
            for selector in product_selectors:
                try:
                    elements = await page.query_selector_all(selector)
                    if elements:
                        product_elements = elements
                        logger.info(f"📦 Найдено {len(elements)} товаров")
                        break
                except:
                    continue
            
            if not product_elements:
                logger.warning("❌ Товары не найдены")
                return products
            
            # Извлекаем данные из первых 10 товаров
            for i, element in enumerate(product_elements[:10]):
                try:
                    product_data = await self._extract_amazon_product_data(element, i)
                    if product_data:
                        products.append(product_data)
                        logger.info(f"✅ Товар {i+1}: {product_data['name'][:50]}...")
                except Exception as e:
                    logger.error(f"❌ Ошибка товара {i+1}: {e}")
                    continue
            
            logger.info(f"🎉 Успешно извлечено {len(products)} товаров")
            
        except Exception as e:
            logger.error(f"❌ Ошибка парсинга: {e}")
            
        finally:
            if 'page' in locals():
                await page.close()
        
        return products
    
    async def _extract_amazon_product_data(self, element, index):
        """Извлечение данных товара Amazon"""
        try:
            # ID товара
            asin = await element.get_attribute('data-asin')
            if not asin:
                # Пробуем найти в ссылке
                link = await element.query_selector('h2 a')
                if link:
                    href = await link.get_attribute('href')
                    if href and '/dp/' in href:
                        asin = href.split('/dp/')[1].split('/')[0]
            
            if not asin:
                asin = f"amazon_{index + 1}"
            
            # Название товара
            name = ""
            name_selectors = [
                'h2 a span',
                'h2 span',
                '[data-cy="title-recipe-title"] span',
                '.s-size-mini .s-link-style .s-color-base',
                'h2 a[title]'
            ]
            
            for selector in name_selectors:
                try:
                    name_el = await element.query_selector(selector)
                    if name_el:
                        name = await name_el.inner_text()
                        if name and name.strip():
                            break
                except:
                    continue
            
            if not name:
                name = f"Товар Amazon {asin}"
            
            # Цена товара
            price = ""
            price_selectors = [
                '.a-price-whole',
                '.a-price .a-offscreen',
                '.a-price-range',
                '[data-cy="price-recipe"] .a-price .a-offscreen',
                '.a-price-symbol + .a-price-whole',
                '.a-price .a-price-whole',
                '.a-price .a-price-symbol'
            ]
            
            for selector in price_selectors:
                try:
                    price_el = await element.query_selector(selector)
                    if price_el:
                        price_text = await price_el.inner_text()
                        if price_text and price_text.strip():
                            price = self._extract_price(price_text)
                            if price:
                                break
                except:
                    continue
            
            # Если цена не найдена, ищем в data-атрибутах
            if not price:
                price_attrs = ['data-price', 'data-asin-price', 'data-price-amount']
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
                "id": asin,
                "name": name.strip(),
                "price": price or "Цена не указана"
            }
            
        except Exception as e:
            logger.error(f"Ошибка извлечения данных товара: {e}")
            return None


async def main():
    """Основная функция"""
    print("🚀 Продвинутый парсер Amazon")
    print("=" * 50)
    
    url = "https://www.amazon.com/s?k=shoes"
    print(f"🎯 Цель: {url}")
    print("🔄 Запускаем браузер в видимом режиме...")
    print("⏳ Это может занять 30-60 секунд...")
    print()
    
    try:
        async with AdvancedAmazonParser(headless=False) as parser:
            products = await parser.parse(url)
            
            if products:
                print(f"\n✅ УСПЕХ! Найдено товаров: {len(products)}")
                print("=" * 50)
                
                for i, product in enumerate(products, 1):
                    print(f"{i:2d}. ID: {product['id']}")
                    print(f"    Название: {product['name'][:80]}{'...' if len(product['name']) > 80 else ''}")
                    print(f"    Цена: {product['price']}")
                    print()
                
                print("🎉 Парсинг завершен успешно!")
                
            else:
                print("\n❌ Товары не найдены")
                print("Возможные причины:")
                print("- Amazon заблокировал запрос")
                print("- Изменилась структура страницы")
                print("- Нужно больше времени для загрузки")
                
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        print("Попробуйте:")
        print("1. Проверить интернет-соединение")
        print("2. Запустить снова")
        print("3. Использовать VPN")


if __name__ == "__main__":
    asyncio.run(main())
