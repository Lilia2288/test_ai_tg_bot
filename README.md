# Telegram Recipe Bot

Бот для поиска рецептов по имеющимся продуктам или получения случайного рецепта.

## Функциональность

- 🎲 Получение случайного рецепта
- 🔍 Поиск рецептов по имеющимся продуктам
- 📝 Подробные инструкции по приготовлению

## Установка

1. Клонируйте репозиторий
2. Установите зависимости:
```bash
pip install -r requirements.txt
```
3. Создайте файл `.env` и добавьте в него токен вашего бота:
```
TELEGRAM_TOKEN=your_bot_token_here
```

## Запуск

```bash
python bot.py
```

## Использование

1. Отправьте команду `/start` для начала работы
2. Используйте `/random` для получения случайного рецепта
3. Отправьте список продуктов через запятую для поиска подходящих рецептов
   Например: `яйца, помидоры, лук`