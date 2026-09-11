# PS Store Turkey — Telegram Mini App MVP

Первая рабочая версия премиального магазина игр для Telegram Mini App.

## Что уже работает

- Премиальный dark gaming UI.
- Главная страница с подборками.
- Каталог игр.
- Поиск.
- Фильтры PS5 / PS4.
- Карточка игры.
- Добавление/удаление из корзины.
- Изменение количества.
- Расчёт TRY → RUB.
- Наценка по умолчанию 10%.
- Профиль Telegram-пользователя через Telegram WebApp SDK, если приложение запущено внутри Telegram.
- Экран checkout.
- Кнопка оплаты подготовлена под следующий этап.
- Backend API на FastAPI.
- SQLite для локального MVP.
- Docker Compose для запуска frontend + backend.

## Важно

Каталог в этой версии демонстрационный. Цены и игры лежат в backend database/seed и НЕ являются актуальными ценами PlayStation Store.

Автоматическое получение актуального каталога PS Store Turkey — следующий этап. Не стоит использовать обходные методы, нарушающие правила Sony/PlayStation Store; источник каталога нужно определить отдельно.

## Быстрый запуск без Docker

### Backend

Требуется Python 3.11+.

```bash
cd backend
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

API будет доступен на:
http://localhost:8000

Swagger:
http://localhost:8000/docs

### Frontend

Требуется Node.js 20+.

```bash
cd frontend
npm install
npm run dev
```

Открой:
http://localhost:5173

Для локального запуска вне Telegram приложение использует demo-пользователя.

## Запуск через Docker

```bash
docker compose up --build
```

Frontend:
http://localhost:5173

Backend:
http://localhost:8000

## Структура

```text
ps-store-telegram-miniapp/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── database.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── seed.py
│   │   └── routers/
│   │       ├── games.py
│   │       ├── settings.py
│   │       └── orders.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── api.js
│   │   ├── main.jsx
│   │   └── styles.css
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

## Переменные окружения

Backend:

```env
DATABASE_URL=sqlite:///./store.db
DEFAULT_TRY_RUB=2.28
DEFAULT_MARKUP=0.10
BOT_USERNAME=your_bot_username
```

Frontend:

```env
VITE_API_URL=http://localhost:8000/api
VITE_BOT_USERNAME=your_bot_username
```

## Что нужно сделать перед продакшеном

1. Подключить реальный источник каталога.
2. Добавить планировщик обновления каталога и цен.
3. Хранить историю курсов.
4. Перейти на PostgreSQL.
5. Добавить Telegram initData validation на backend.
6. Подключить реальную оплату.
7. Создавать заказ на backend только после подтверждённой оплаты.
8. После оплаты открывать Telegram-бота с ID заказа.
9. Сделать полноценную админку.
10. Настроить HTTPS и Telegram Mini App в BotFather.

## Архитектура будущей покупки

```text
Mini App
   ↓
Checkout
   ↓
Payment Provider
   ↓
Backend подтверждает оплату
   ↓
Order #1234
   ↓
Открывается Telegram Bot
   ↓
Бот показывает заказ #1234
   ↓
Оформление покупки игры
```


## Публикация в Telegram

См. `DEPLOY_TELEGRAM.md`.


## PS4 / PS5 + PS Plus

Добавлен модуль каталога PlayStation Store Turkey. См. `CATALOG_UPGRADE.md`.
