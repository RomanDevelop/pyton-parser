# 🚀 Универсальный парсер товаров с динамических сайтов

Python-скрипт для парсинга товаров с сайтов, использующих JavaScript для динамической загрузки контента. Специально оптимизирован для Amazon с обходом блокировок.

## 📋 Содержание

- [Установка](#-установка)
- [Быстрый старт](#-быстрый-старт)
- [Детальные инструкции](#-детальные-инструкции)
- [Примеры использования](#-примеры-использования)
- [Экспорт в Excel](#-экспорт-в-excel)
- [Настройка под другие сайты](#-настройка-под-другие-сайты)
- [Решение проблем](#-решение-проблем)
- [API Reference](#-api-reference)

## 🛠 Установка

### 1. Клонирование репозитория

```bash
git clone <repository-url>
cd pyton_parser
```

### 2. Создание виртуального окружения

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate     # Windows
```

### 3. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 4. Установка браузеров Playwright

```bash
playwright install
```

## 🚀 Быстрый старт

### Простой парсинг

```bash
python product_parser.py
```

### Парсинг Amazon

```bash
python amazon_advanced.py
```

### Экспорт в Excel

```bash
python quick_export.py
```

## 📖 Детальные инструкции

### 1. Базовое использование

#### Синхронный парсинг

```python
from product_parser import parse_products

# Парсим товары с любого сайта
products = parse_products("https://your-site.com/products")
print(products)
```

#### Асинхронный парсинг

```python
import asyncio
from product_parser import ProductParser

async def main():
    async with ProductParser() as parser:
        products = await parser.parse("https://your-site.com/products")
        print(products)

asyncio.run(main())
```

### 2. Парсинг Amazon

#### Простой способ

```python
from amazon_advanced import AdvancedAmazonParser
import asyncio

async def main():
    async with AdvancedAmazonParser(headless=True) as parser:
        products = await parser.parse("https://www.amazon.com/s?k=shoes")
        print(products)

asyncio.run(main())
```

#### С настройками

```python
from amazon_advanced import AdvancedAmazonParser
import asyncio

async def main():
    # Видимый браузер для отладки
    async with AdvancedAmazonParser(headless=False, timeout=60000) as parser:
        products = await parser.parse("https://www.amazon.com/s?k=sneakers")

        for product in products:
            print(f"ID: {product['id']}")
            print(f"Название: {product['name']}")
            print(f"Цена: {product['price']}")
            print("-" * 50)

asyncio.run(main())
```

### 3. Экспорт в Excel

#### Быстрый экспорт

```python
from export_improved import parse_and_export_improved
import asyncio

async def main():
    filename = await parse_and_export_improved(
        url="https://www.amazon.com/s?k=shoes",
        filename="my_products.xlsx"
    )
    print(f"Создан файл: {filename}")

asyncio.run(main())
```

#### Множественный экспорт

```python
from export_to_excel import parse_multiple_urls
import asyncio

async def main():
    urls = [
        "https://www.amazon.com/s?k=shoes",
        "https://www.amazon.com/s?k=sneakers",
        "https://www.amazon.com/s?k=boots"
    ]

    filename = await parse_multiple_urls(urls, "all_products.xlsx")
    print(f"Создан файл: {filename}")

asyncio.run(main())
```

## 📊 Примеры использования

### 1. Парсинг разных категорий Amazon

```python
import asyncio
from amazon_advanced import AdvancedAmazonParser

async def parse_categories():
    categories = [
        "https://www.amazon.com/s?k=shoes",
        "https://www.amazon.com/s?k=sneakers",
        "https://www.amazon.com/s?k=boots",
        "https://www.amazon.com/s?k=sandals"
    ]

    async with AdvancedAmazonParser(headless=True) as parser:
        for category in categories:
            print(f"Парсим: {category}")
            products = await parser.parse(category)
            print(f"Найдено: {len(products)} товаров")
            print()

asyncio.run(parse_categories())
```

### 2. Настройка под конкретный сайт

```python
from product_parser import ProductParser

class MySiteParser(ProductParser):
    async def _wait_for_content(self, page):
        """Ожидание загрузки товаров для вашего сайта"""
        await page.wait_for_selector('.product-item', timeout=10000)
        return True

    async def _extract_product_data(self, element, page, index):
        """Извлечение данных по структуре вашего сайта"""
        # ID товара
        product_id = await element.get_attribute('data-id')
        if not product_id:
            product_id = str(index + 1)

        # Название товара
        name_element = await element.query_selector('.product-title')
        name = await name_element.inner_text() if name_element else f"Товар {product_id}"

        # Цена товара
        price_element = await element.query_selector('.product-price')
        price = await price_element.inner_text() if price_element else "Цена не указана"

        return {
            "id": product_id,
            "name": name.strip(),
            "price": price.strip()
        }

# Использование
async def main():
    async with MySiteParser() as parser:
        products = await parser.parse("https://your-site.com/products")
        print(products)

asyncio.run(main())
```

### 3. Парсинг с обработкой ошибок

```python
import asyncio
import logging
from product_parser import ProductParser

# Настройка логирования
logging.basicConfig(level=logging.INFO)

async def robust_parsing():
    urls = [
        "https://www.amazon.com/s?k=shoes",
        "https://example-shop.com/products",
        "https://another-site.com/catalog"
    ]

    async with ProductParser(headless=True) as parser:
        for url in urls:
            try:
                print(f"Парсим: {url}")
                products = await parser.parse(url)

                if products:
                    print(f"✅ Успешно: {len(products)} товаров")
                    for product in products[:3]:  # Показываем первые 3
                        print(f"  - {product['name'][:50]}... - {product['price']}")
                else:
                    print("❌ Товары не найдены")

            except Exception as e:
                print(f"❌ Ошибка: {e}")

            print("-" * 50)

asyncio.run(robust_parsing())
```

## 📊 Экспорт в Excel

### 1. Простой экспорт

```bash
python quick_export.py
```

### 2. Улучшенный экспорт с форматированием

```bash
python export_improved.py
```

### 3. Полный экспорт с настройками

```bash
python export_to_excel.py
```

### 4. Создание сводного отчета

```bash
python final_report.py
```

### Структура Excel файлов

#### Листы:

- **"Товары Amazon"** - основная таблица с товарами
- **"Статистика"** - статистика парсинга
- **"Примеры товаров"** - первые 5 товаров

#### Колонки:

- **№** - порядковый номер
- **ID товара** - уникальный идентификатор (ASIN для Amazon)
- **Название товара** - полное название
- **Цена** - цена в долларах
- **Дата парсинга** - когда был выполнен парсинг
- **URL источника** - откуда взяты данные

## 🔧 Настройка под другие сайты

### 1. Определение селекторов

Для настройки под конкретный сайт нужно определить:

#### Селекторы товаров:

```python
product_selectors = [
    '.product-item',      # Основной контейнер товара
    '.product-card',      # Альтернативный контейнер
    '[data-product-id]',  # По data-атрибуту
    '.item'               # Простой класс
]
```

#### Селекторы названий:

```python
name_selectors = [
    '.product-title',     # Основной селектор
    'h2 a',              # Заголовок с ссылкой
    '.item-name',        # Альтернативный
    '[data-title]'       # По data-атрибуту
]
```

#### Селекторы цен:

```python
price_selectors = [
    '.price',            # Основной селектор
    '.cost',             # Альтернативный
    '.amount',           # Еще один вариант
    '[data-price]'       # По data-атрибуту
]
```

### 2. Пример настройки

```python
from product_parser import ProductParser

class CustomSiteParser(ProductParser):
    async def _wait_for_content(self, page):
        """Ожидание загрузки товаров"""
        selectors = [
            '.product-item',      # Ваш селектор товаров
            '.product-card',      # Альтернативный
            '[data-product]'      # По data-атрибуту
        ]

        for selector in selectors:
            try:
                await page.wait_for_selector(selector, timeout=5000)
                return True
            except:
                continue

        return False

    async def _extract_product_data(self, element, page, index):
        """Извлечение данных товара"""
        # ID товара
        product_id = await element.get_attribute('data-id')
        if not product_id:
            product_id = str(index + 1)

        # Название товара
        name = await self._extract_text_by_selectors(element, [
            '.product-title',
            'h2 a',
            '.item-name'
        ])

        # Цена товара
        price = await self._extract_text_by_selectors(element, [
            '.price',
            '.cost',
            '.amount'
        ])

        return {
            "id": product_id,
            "name": name or f"Товар {product_id}",
            "price": self._extract_price(price) if price else "Цена не указана"
        }
```

## 🚨 Решение проблем

### 1. Amazon блокирует запросы

**Проблема**: Amazon возвращает CAPTCHA или блокирует запросы

**Решения**:

```python
# 1. Используйте видимый браузер
async with AdvancedAmazonParser(headless=False) as parser:
    products = await parser.parse(url)

# 2. Добавьте задержки
import asyncio
await asyncio.sleep(random.uniform(2, 5))

# 3. Используйте прокси
# Настройте прокси в AdvancedAmazonParser

# 4. Ротируйте User-Agent
user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
]
```

### 2. Товары не найдены

**Проблема**: Парсер не находит товары на странице

**Решения**:

```python
# 1. Запустите с видимым браузером для отладки
async with ProductParser(headless=False) as parser:
    products = await parser.parse(url)

# 2. Проверьте селекторы
# Откройте DevTools в браузере и найдите правильные селекторы

# 3. Увеличьте таймаут
async with ProductParser(timeout=60000) as parser:
    products = await parser.parse(url)

# 4. Добавьте ожидание загрузки
await page.wait_for_load_state('networkidle')
```

### 3. Ошибки установки

**Проблема**: Ошибки при установке зависимостей

**Решения**:

```bash
# 1. Обновите pip
pip install --upgrade pip

# 2. Используйте виртуальное окружение
python3 -m venv venv
source venv/bin/activate

# 3. Установите браузеры
playwright install

# 4. Для macOS с Homebrew
brew install python3
```

### 4. Медленная работа

**Проблема**: Парсинг работает медленно

**Решения**:

```python
# 1. Блокируйте ненужные ресурсы
await page.route("**/*.{png,jpg,jpeg,gif,svg}", lambda route: route.abort())

# 2. Используйте headless режим
async with ProductParser(headless=True) as parser:
    products = await parser.parse(url)

# 3. Ограничьте количество товаров
products = products[:10]  # Только первые 10
```

## 📚 API Reference

### ProductParser

#### Конструктор

```python
ProductParser(headless: bool = True, timeout: int = 30000)
```

**Параметры**:

- `headless` - Запускать браузер в фоновом режиме
- `timeout` - Таймаут загрузки страницы в миллисекундах

#### Методы

##### parse(url: str) -> List[Dict[str, str]]

Основной метод парсинга товаров

**Параметры**:

- `url` - URL страницы с товарами

**Возвращает**:

- Список словарей с данными товаров

**Пример**:

```python
async with ProductParser() as parser:
    products = await parser.parse("https://example.com/products")
```

### AdvancedAmazonParser

#### Конструктор

```python
AdvancedAmazonParser(headless: bool = False, timeout: int = 60000)
```

**Параметры**:

- `headless` - Запускать браузер в фоновом режиме
- `timeout` - Таймаут загрузки страницы в миллисекундах

#### Методы

##### parse(url: str) -> List[Dict[str, str]]

Парсинг товаров Amazon с обходом блокировки

**Параметры**:

- `url` - URL страницы Amazon с товарами

**Возвращает**:

- Список словарей с данными товаров

**Пример**:

```python
async with AdvancedAmazonParser() as parser:
    products = await parser.parse("https://www.amazon.com/s?k=shoes")
```

### Синхронные функции

#### parse_products(url: str, headless: bool = True) -> List[Dict[str, str]]

Синхронная функция для парсинга товаров

**Параметры**:

- `url` - URL страницы с товарами
- `headless` - Запускать браузер в фоновом режиме

**Возвращает**:

- Список словарей с данными товаров

**Пример**:

```python
from product_parser import parse_products

products = parse_products("https://example.com/products")
```

## 📁 Структура проекта

```
pyton_parser/
├── product_parser.py          # Основной модуль парсера
├── amazon_advanced.py         # Парсер для Amazon
├── export_to_excel.py         # Экспорт в Excel
├── export_improved.py         # Улучшенный экспорт
├── quick_export.py            # Быстрый экспорт
├── final_report.py            # Сводный отчет
├── example_usage.py           # Примеры использования
├── demo_usage.py              # Демонстрация
├── working_example.py         # Рабочие примеры
├── test_amazon.py             # Тесты для Amazon
├── requirements.txt           # Зависимости
├── README.md                  # Документация
└── venv/                      # Виртуальное окружение
```

## 🎯 Готовые скрипты

### 1. product_parser.py

Основной скрипт с интерактивным режимом

```bash
python product_parser.py
```

### 2. amazon_advanced.py

Парсер Amazon с обходом блокировки

```bash
python amazon_advanced.py
```

### 3. quick_export.py

Быстрый экспорт в Excel

```bash
python quick_export.py
```

### 4. export_improved.py

Улучшенный экспорт с форматированием

```bash
python export_improved.py
```

### 5. final_report.py

Создание сводного отчета

```bash
python final_report.py
```

## 🚀 Готово к использованию!

Парсер настроен и готов к работе. Выберите подходящий скрипт и начните парсинг!

### Для начинающих:

1. `python quick_export.py` - быстрый старт
2. `python amazon_advanced.py` - парсинг Amazon

### Для продвинутых:

1. Настройте `CustomSiteParser` под ваш сайт
2. Используйте асинхронные методы
3. Добавьте обработку ошибок

### Для автоматизации:

1. Создайте cron задачу
2. Используйте планировщик задач
3. Настройте уведомления

## 📞 Поддержка

При возникновении проблем:

1. Проверьте логи в консоли
2. Запустите с `headless=False` для отладки
3. Проверьте селекторы в DevTools
4. Убедитесь в правильности URL

---

**Удачного парсинга! 🎉**
# pyton-parser
