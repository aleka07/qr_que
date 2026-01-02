# 🎯 Digital Pager System - Quick Start

## Полная реализация выполнена!

Система состоит из:
- ✅ **Backend** (FastAPI + PostgreSQL + Redis + WebSocket)
- ✅ **Staff App** - Пульт управления для создания заказов
- ✅ **Display App** - Планшет для отображения QR-кодов
- ✅ **Client App** - Мобильное отслеживание для клиентов
- ✅ **Nginx** - Конфигурация для субдоменов
- ✅ **Docker** - Полная контейнеризация

---

## 🚀 Быстрый старт (Локальная разработка)

### Вариант 1: Автоматическая настройка

```bash
# Запустить setup скрипт
./scripts/setup.sh

# В отдельных терминалах запустить frontend приложения:
# Terminal 1
cd frontend/staff && npm install && npm run dev

# Terminal 2
cd frontend/display && npm install && npm run dev

# Terminal 3
cd frontend/client && npm install && npm run dev
```

### Вариант 2: Ручная настройка

#### 1. Backend Setup

```bash
# Запустить PostgreSQL и Redis
docker-compose up -d db redis

# Создать виртуальное окружение
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac

# Установить зависимости
pip install -r requirements.txt

# Создать .env файл
cp .env.example .env

# Применить миграции
alembic upgrade head

# Запустить сервер
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend API: http://localhost:8000  
API Docs: http://localhost:8000/docs

#### 2. Frontend Setup

**Staff App** (порт 3000):
```bash
cd frontend/staff
npm install
npm run dev
```

**Display App** (порт 3001):
```bash
cd frontend/display
npm install
npm run dev
```

**Client App** (порт 3002):
```bash
cd frontend/client
npm install
npm run dev
```

---

## 🧪 Тестирование

### Сценарий полного цикла:

1. **Откройте приложения:**
   - Staff App: http://localhost:3000
   - Display App: http://localhost:3001

2. **Создайте заказ:**
   - В Staff App выберите "Планшет 1"
   - Введите номер "47"
   - Нажмите Enter

3. **Проверьте Display:**
   - В Display App должен появиться QR-код с номером "47"
   - QR-код исчезнет через 30 секунд

4. **Сканируйте QR:**
   - Скопируйте URL из QR-кода
   - Откройте в новой вкладке (или на телефоне)
   - Client App покажет статус заказа

5. **Измените статус:**
   - В Staff App кликните на карточку заказа
   - Статус изменится: pending → scanned → preparing → ready
   - В Client App статус обновится в реальном времени
   - При статусе "ready" телефон завибрирует

### API Тестирование:

```bash
# Создать заказ
curl -X POST http://localhost:8000/api/orders \
  -H "Content-Type: application/json" \
  -d '{"human_id": "A-42", "device_id": "tab_1"}'

# Получить активные заказы
curl http://localhost:8000/api/orders/active

# Health check
curl http://localhost:8000/health
```

---

## 🐳 Docker Production Deploy

```bash
# Собрать все приложения
./scripts/build_frontend.sh

# Запустить production окружение
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Применить миграции
docker-compose exec backend alembic upgrade head

# Проверить логи
docker-compose logs -f
```

---

## 📁 Структура проекта

```
qr_que/
├── backend/                 # FastAPI Backend
│   ├── app/
│   │   ├── main.py         # Главный файл приложения
│   │   ├── models.py       # SQLAlchemy модели
│   │   ├── schemas.py      # Pydantic схемы
│   │   ├── routes.py       # API endpoints + WebSocket
│   │   ├── websocket.py    # WebSocket Manager
│   │   ├── crud.py         # Database operations
│   │   ├── database.py     # DB connection
│   │   ├── config.py       # Settings
│   │   └── utils.py        # Utility functions
│   ├── alembic/            # Database migrations
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/
│   ├── staff/              # Staff Dashboard
│   │   ├── src/
│   │   │   ├── App.jsx
│   │   │   ├── api.js
│   │   │   └── components/
│   │   │       ├── NumPad.jsx
│   │   │       └── OrderList.jsx
│   │   └── package.json
│   │
│   ├── display/            # QR Display
│   │   ├── src/
│   │   │   ├── App.jsx
│   │   │   ├── api.js
│   │   │   └── components/
│   │   │       └── QRDisplay.jsx
│   │   └── package.json
│   │
│   └── client/             # Client Tracker
│       ├── src/
│       │   ├── App.jsx
│       │   ├── api.js
│       │   └── components/
│       │       └── OrderStatus.jsx
│       └── package.json
│
├── nginx/                  # Nginx configuration
│   ├── sites-available/
│   │   └── qr_que.conf
│   └── Dockerfile
│
├── scripts/                # Utility scripts
│   ├── setup.sh           # Development setup
│   ├── build_frontend.sh  # Build all frontends
│   └── deploy.sh          # Production deploy
│
├── docker-compose.yml      # Development compose
├── docker-compose.prod.yml # Production overrides
├── README.md
├── TESTING.md
└── TZ.md                   # Technical Specification
```

---

## 🔌 API Endpoints

### REST API

- `POST /api/orders` - Создать заказ
- `GET /api/orders` - Список всех заказов
- `GET /api/orders/active` - Активные заказы
- `GET /api/orders/{id}` - Заказ по ID
- `GET /api/track/{token}` - Заказ по токену (public)
- `PATCH /api/orders/{id}/status` - Обновить статус

### WebSocket Endpoints

- `ws://api/ws/staff` - Staff Dashboard
- `ws://api/ws/display/{device_id}` - Display Device
- `ws://api/ws/client/{token}` - Client Tracker

---

## 🌐 Субдомены (Production)

- `kaskyralmaty.dev` → 404 (empty)
- `api.kaskyralmaty.dev` → Backend API
- `staff.kaskyralmaty.dev` → Staff Dashboard
- `display.kaskyralmaty.dev` → QR Display
- `track.kaskyralmaty.dev` → Client Tracker

---

## 🛠 Технологический стек

**Backend:**
- Python 3.11+
- FastAPI (async)
- SQLAlchemy (async)
- PostgreSQL
- Redis
- Alembic (migrations)
- WebSockets

**Frontend:**
- React 18
- Vite (build tool)
- QRCode library
- Native WebSocket API
- Vibration API (mobile)

**Infrastructure:**
- Docker & Docker Compose
- Nginx (reverse proxy)
- Ubuntu/Linux

---

## 📊 Статусы заказов

1. **pending** - Создан, QR показан
2. **scanned** - Клиент отсканировал QR
3. **preparing** - В процессе приготовления
4. **ready** - Готов к выдаче (вибрация на телефоне!)
5. **completed** - Выдан клиенту
6. **cancelled** - Отменен

---

## 🎨 Особенности реализации

✨ **Real-time коммуникация:**
- WebSocket для мгновенных обновлений
- Автоматическое переподключение
- Ping/pong для keep-alive

✨ **UX/UI:**
- Responsive design
- Градиентные анимации
- Пульсация при статусе "ready"
- Вибрация на мобильных устройствах
- QR-код с таймером обратного отсчета

✨ **Безопасность:**
- Уникальные токены для каждого заказа
- UUID для ID заказов
- CORS настройки
- Public и Private API разделение

✨ **Масштабируемость:**
- Async/await во всем коде
- Connection pooling
- Redis для кеширования
- Docker для изоляции
- Nginx для load balancing

---

## 📝 Дальнейшие улучшения (опционально)

- [ ] Push-уведомления (Service Workers)
- [ ] Звуковые уведомления для staff
- [ ] История заказов
- [ ] Аналитика и статистика
- [ ] Экспорт отчетов
- [ ] Multi-tenancy (несколько фудкортов)
- [ ] Telegram/SMS уведомления
- [ ] PWA для офлайн-режима
- [ ] Темная тема
- [ ] Internationalization (i18n)

---

## 🐛 Troubleshooting

**Backend не стартует:**
```bash
docker-compose logs backend
# Проверить миграции
docker-compose exec backend alembic current
```

**WebSocket не подключается:**
- Проверьте CORS в config.py
- Проверьте что backend запущен
- Откройте DevTools → Network → WS

**Frontend не собирается:**
```bash
rm -rf node_modules package-lock.json
npm install
```

**Порты заняты:**
```bash
# Проверить какие порты заняты
lsof -i :8000
lsof -i :5432
# Остановить все контейнеры
docker-compose down
```

---

## 📞 Контакты и поддержка

Документация:
- [README.md](README.md) - Основная информация
- [TESTING.md](TESTING.md) - Подробное руководство по тестированию
- [TZ.md](TZ.md) - Техническое задание

API Documentation: http://localhost:8000/docs

---

## ✅ Чеклист готовности к production

- [x] Backend API реализован
- [x] База данных настроена
- [x] WebSocket работает
- [x] 3 Frontend приложения созданы
- [x] Docker конфигурация готова
- [x] Nginx настроен
- [x] Миграции базы данных
- [x] CORS настроен
- [x] Скрипты развертывания
- [ ] SSL сертификаты (Let's Encrypt)
- [ ] Environment variables для production
- [ ] Логирование в файлы
- [ ] Мониторинг (опционально)
- [ ] Backup базы данных

---

**Система полностью готова к использованию! 🚀**

Для запуска: `./scripts/setup.sh`
