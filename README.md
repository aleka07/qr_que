# Digital Pager System (QR Queue)

Enterprise-ready система управления выдачей заказов для фудкортов с использованием QR-кодов.

## Архитектура

- **Backend:** Python 3.11+ (FastAPI) с асинхронными WebSockets
- **Database:** PostgreSQL + SQLAlchemy (Async)
- **Cache/Broker:** Redis
- **Frontend:** React (3 отдельных приложения)
- **Infrastructure:** Docker, Nginx

## Структура проекта

```
qr_que/
├── backend/           # FastAPI application
├── frontend/
│   ├── staff/        # Пульт управления
│   ├── display/      # Планшет с QR
│   └── client/       # Мобильное отслеживание
├── nginx/            # Nginx конфигурация
└── docker-compose.yml
```

## Быстрый старт

### Запуск Backend

```bash
# Запустить все сервисы
docker-compose up -d

# Применить миграции
docker-compose exec backend alembic upgrade head

# Посмотреть логи
docker-compose logs -f backend
```

### Разработка

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend (в отдельных терминалах)
cd frontend/staff && npm install && npm run dev
cd frontend/display && npm install && npm run dev
cd frontend/client && npm install && npm run dev
```

## API Endpoints

- `POST /orders` - Создать новый заказ
- `GET /orders` - Получить список заказов
- `PATCH /orders/{id}/status` - Обновить статус заказа
- `GET /orders/{token}` - Получить заказ по токену клиента

## WebSocket Endpoints

- `ws://api.kaskyralmaty.dev/ws/staff` - Для Staff App
- `ws://api.kaskyralmaty.dev/ws/display/{device_id}` - Для Display App
- `ws://api.kaskyralmaty.dev/ws/client/{token}` - Для Client App

## Субдомены

- `kaskyralmaty.dev` - Пустая страница (404)
- `api.kaskyralmaty.dev` - FastAPI Backend
- `staff.kaskyralmaty.dev` - Staff App
- `display.kaskyralmaty.dev` - Display App
- `track.kaskyralmaty.dev` - Client App
