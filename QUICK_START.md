# 🚀 Быстрый старт - Парсер товаров

## ⚡ За 5 минут

### 1. Установка

```bash
# Активируйте виртуальное окружение
source venv/bin/activate

# Установите зависимости (уже установлены)
pip install -r requirements.txt

# Установите браузеры (уже установлены)
playwright install
```

### 2. Парсинг Amazon

```bash
python amazon_advanced.py
```

### 3. Экспорт в Excel

```bash
python quick_export.py
```

## 🎯 Готовые команды

| Команда                     | Описание                | Время  |
| --------------------------- | ----------------------- | ------ |
| `python quick_export.py`    | Быстрый экспорт в Excel | 30 сек |
| `python amazon_advanced.py` | Парсинг Amazon          | 60 сек |
| `python export_improved.py` | Улучшенный экспорт      | 60 сек |
| `python final_report.py`    | Сводный отчет           | 10 сек |

## 📊 Результат

После выполнения получите Excel файлы с товарами:

- **ID товара** - уникальный идентификатор
- **Название** - полное название товара
- **Цена** - цена в долларах
- **Дата парсинга** - когда был выполнен парсинг

## 🔧 Настройка

### Для других сайтов:

```python
from product_parser import parse_products

# Простой способ
products = parse_products("https://your-site.com/products")
```

### Для Amazon:

```python
from amazon_advanced import AdvancedAmazonParser
import asyncio

async def main():
    async with AdvancedAmazonParser() as parser:
        products = await parser.parse("https://www.amazon.com/s?k=shoes")
        print(products)

asyncio.run(main())
```

## ❓ Проблемы?

1. **Amazon блокирует** → Используйте `headless=False`
2. **Товары не найдены** → Проверьте URL
3. **Ошибки установки** → Переустановите зависимости

## 📚 Подробная документация

Смотрите `README.md` для полной документации.

---

**Готово! Начинайте парсинг! 🎉**
