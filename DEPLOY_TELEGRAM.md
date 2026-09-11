# Публикация Mini App и подключение к Telegram

Эта версия подготовлена для запуска как один Web Service:
FastAPI раздаёт API и собранный React frontend по одному HTTPS-адресу.

## 1. Загрузить проект в GitHub
Создайте новый репозиторий, например `ps-store-miniapp`, и загрузите туда все файлы проекта.

## 2. Развернуть на Render
1. Войдите на Render.
2. Нажмите New -> Web Service.
3. Подключите GitHub и выберите репозиторий.
4. Выберите Docker.
5. Создайте Web Service.
6. После deploy получите HTTPS-адрес вида `https://...onrender.com`.
7. Проверьте `/api/health`.
8. Откройте корневой адрес — должен появиться магазин.

## 3. Создать Telegram-бота
В Telegram откройте @BotFather:
1. `/newbot`
2. Задайте имя и username.
3. Сохраните token в безопасном месте.

## 4. Привязать Mini App
В @BotFather выберите вашего бота и настройте Menu Button / Web App.
Укажите HTTPS URL из Render.
Текст кнопки: `Открыть магазин`.

## 5. BOT_USERNAME
В Render -> Environment задайте:
`BOT_USERNAME=username_вашего_бота`
без `@`.

## Важно
Это MVP:
- каталог демонстрационный;
- реальная оплата не подключена;
- серверная проверка Telegram initData ещё не добавлена;
- SQLite используется только для прототипа.
