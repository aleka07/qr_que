# 📋 QR Queue Project History & Architecture

> Документация по истории разработки и архитектуре проекта Digital Pager System (QR Queue).

---

## 🎯 Описание проекта

**QR Queue** — система управления очередью выдачи заказов для фудкортов с использованием QR-кодов.

### Основная идея
1. Клиент делает заказ на кассе
2. Кассир создаёт заказ в системе → на планшете показывается QR-код
3. Клиент сканирует QR → попадает на страницу отслеживания
4. Кассир меняет статус заказа → клиент получает уведомление в реальном времени

---

## 🏗️ Архитектура

```
┌─────────────────────────────────────────────────────────────┐
│                        NGINX Reverse Proxy                   │
│  staff.kaskyralmaty.dev │ display.* │ track.* │ api.*       │
└─────────────────────────────────────────────────────────────┘
           │                    │           │         │
           ▼                    ▼           ▼         ▼
┌──────────────┐  ┌──────────────┐  ┌───────────┐  ┌─────────┐
│  Staff App   │  │ Display App  │  │Client App │  │ Backend │
│   (React)    │  │   (React)    │  │  (React)  │  │(FastAPI)│
└──────────────┘  └──────────────┘  └───────────┘  └─────────┘
                                                        │
                              ┌─────────────────────────┴───────┐
                              ▼                                 ▼
                       ┌──────────────┐                 ┌──────────────┐
                       │  PostgreSQL  │                 │    Redis     │
                       └──────────────┘                 └──────────────┘
```

### Frontend приложения

| Приложение | Назначение | Субдомен |
|------------|-----------|----------|
| **Staff** | Пульт кассира: создание заказов, управление статусами | `staff.kaskyralmaty.dev` |
| **Display** | Планшет у кассы: показывает QR-код для сканирования | `display.kaskyralmaty.dev` |
| **Client** | Мобильная страница клиента: отслеживание статуса заказа | `track.kaskyralmaty.dev` |

---

## 📂 Структура проекта

```
qr_que/
├── backend/                 # FastAPI бэкенд
│   ├── app/
│   │   ├── main.py         # Точка входа, CORS, роутеры
│   │   ├── models.py       # SQLAlchemy модели
│   │   ├── schemas.py      # Pydantic схемы
│   │   ├── routes.py       # Основные API роуты + WebSocket
│   │   ├── routes_auth.py  # Авторизация, управление пользователями
│   │   ├── crud.py         # Операции с БД
│   │   ├── auth.py         # JWT авторизация
│   │   ├── config.py       # Настройки приложения
│   │   ├── database.py     # Подключение к PostgreSQL
│   │   ├── websocket.py    # WebSocket менеджер
│   │   └── seed.py         # Начальные данные (демо)
│   ├── alembic/            # Миграции БД
│   └── Dockerfile
│
├── frontend/
│   ├── staff/              # React App кассира
│   ├── display/            # React App планшета
│   └── client/             # React App клиента
│
├── nginx/                  # Конфигурация Nginx
├── scripts/                # Скрипты деплоя
└── docker-compose.yml      # Docker оркестрация
```

---

## 📊 Модели данных

### Organization (Организация/Сеть)
```
- id: UUID
- name: "KFC", "Burger King"...
- slug: URL-friendly name
- is_demo: флаг демо-аккаунта
```

### Location (Точка продаж)
```
- id: UUID
- organization_id: → Organization
- name: "KFC Mega Almaty"
- mall_name: "Mega Almaty"
- city, address
```

### User (Пользователь)
```
- id: UUID
- organization_id, location_id
- username, email, hashed_password
- role: admin | owner | manager | staff
```

### Order (Заказ)
```
- id: UUID
- location_id: → Location
- human_id: "A-47", "B-12" (номер для клиента)
- status: pending → scanned → preparing → ready → completed
- token: уникальный токен для клиента
- device_id: ID планшета/кассы
```

---

## 🔐 Роли пользователей

| Роль | Описание | Доступ |
|------|----------|--------|
| **admin** | Супер-админ | Все организации, все точки |
| **owner** | Владелец сети | Все точки своей организации |
| **manager** | Менеджер точки | Только своя точка |
| **staff** | Персонал (кассир) | Только своя точка |

---

## 🕐 Хронология разработки

### Фаза 1: Базовая инфраструктура (10:44 - 10:46)
> Первоначальная настройка проекта

| Время | Файл | Описание |
|-------|------|----------|
| 10:44 | `TZ.md` | Техническое задание |
| 10:46 | `.gitignore` | Git конфигурация |
| 10:46 | `docker-compose.yml` | Docker оркестрация |
| 10:46 | `backend/Dockerfile` | Dockerfile бэкенда |
| 10:46 | `backend/.env.example` | Пример переменных окружения |
| 10:46 | `backend/app/database.py` | Подключение к PostgreSQL |
| 10:46 | `README.md` | Документация проекта |
| 10:46 | `backend/app/utils.py` | Утилиты (генерация URL) |

### Фаза 2: Миграции базы данных (10:49)
> Начальная структура БД (только заказы)

| Время | Файл | Описание |
|-------|------|----------|
| 10:49 | `alembic.ini` | Конфигурация Alembic |
| 10:49 | `alembic/env.py` | Окружение миграций |
| 10:49 | `001_initial_migration.py` | Таблица `orders` |

### Фаза 3: Frontend Staff + Display (10:50 - 10:50)
> Базовые интерфейсы кассира и планшета

| Время | Файл | Описание |
|-------|------|----------|
| 10:50 | `frontend/staff/*` | NumPad для ввода номера заказа |
| 10:50 | `frontend/display/*` | QRDisplay компонент |

### Фаза 4: Frontend Client (10:52)
> Мобильное приложение клиента

| Время | Файл | Описание |
|-------|------|----------|
| 10:52 | `frontend/client/*` | OrderStatus, App, api |

### Фаза 5: Инфраструктура продакшена (10:53 - 10:54)
> Nginx, скрипты деплоя

| Время | Файл | Описание |
|-------|------|----------|
| 10:53 | `nginx/Dockerfile` | Nginx контейнер |
| 10:53 | `nginx/qr_que.conf` | Nginx конфиг |
| 10:53 | `scripts/setup.sh` | Скрипт установки |
| 10:53 | `scripts/deploy.sh` | Скрипт деплоя |
| 10:53 | `scripts/build_frontend.sh` | Сборка фронтендов |
| 10:54 | `docker-compose.prod.yml` | Продакшен Docker |

### Фаза 6: Документация (10:54 - 10:58)
> Инструкции и документация

| Время | Файл | Описание |
|-------|------|----------|
| 10:54 | `TESTING.md` | Инструкция по тестированию |
| 10:55 | `backend/.env` | Реальные переменные окружения |
| 10:55 | `QUICKSTART.md` | Быстрый старт |
| 10:56 | `SUMMARY.md` | Сводка проекта |
| 10:58 | `FILES.md` | Описание файлов |

### Фаза 7: Production конфиги (11:13 - 11:14)
> Настройки для продакшена

| Время | Файл | Описание |
|-------|------|----------|
| 11:13 | `package-lock.json` (все 3) | Фиксация зависимостей |
| 11:14 | `.env.production` (все 3) | Продакшен переменные |
| 11:14 | `qr_que_ssl.conf` | SSL конфигурация Nginx |

### Фаза 8: Успешный деплой (11:20)
> Документация деплоя

| Время | Файл | Описание |
|-------|------|----------|
| 11:20 | `DEPLOYMENT_SUCCESS.md` | Отчёт о деплое |

### Фаза 9: UI улучшения (11:35 - 11:37)
> Добавлен список заказов для кассира

| Время | Файл | Описание |
|-------|------|----------|
| 11:35 | `staff/OrderList.jsx` | Компонент списка заказов |
| 11:35 | `staff/OrderList.css` | Стили списка |
| 11:37 | `display/QRDisplay.jsx` | Обновлённый QR дисплей |

### Фаза 10: Мультитенантность + Авторизация (12:13 - 12:30)
> **Крупное обновление**: добавлена система организаций, точек и пользователей

| Время | Файл | Описание |
|-------|------|----------|
| 12:13 | `backend/app/auth.py` | JWT авторизация |
| 12:13 | `backend/app/config.py` | Настройки |
| 12:13 | `backend/app/models.py` | +Organization, Location, User |
| 12:13 | `backend/app/websocket.py` | WebSocket с фильтрацией по location |
| 12:13 | `backend/app/main.py` | Обновлённые роуты |
| 12:13 | `backend/app/seed.py` | Демо-данные |
| 12:13 | `backend/routes_auth.py` | API авторизации |
| 12:13 | `ACCOUNTS.md` | Документация по аккаунтам |
| 12:13 | `staff/Login.jsx` | Форма входа |
| 12:13 | `staff/App.jsx` | Авторизация + выбор точки |
| 12:13 | `staff/api.js` | API с токенами |
| 12:17 | `002_add_accounts.py` | Миграция: орг., точки, юзеры |
| 12:17 | `requirements.txt` | +passlib, python-jose |

### Фаза 11: Финализация (12:30 - 12:32)
> Обновление CRUD и UI под мультитенант

| Время | Файл | Описание |
|-------|------|----------|
| 12:30 | `backend/app/crud.py` | Фильтрация по org/location |
| 12:30 | `backend/app/routes.py` | Проверка доступа |
| 12:30 | `backend/app/schemas.py` | Новые схемы |
| 12:32 | `display/App.jsx` | Выбор локации |
| 12:32 | `display/App.css` | Стили |
| 12:32 | `display/api.js` | API локаций |

---

## 🔄 API Endpoints

### Заказы
```
POST   /api/orders                  - Создать заказ
GET    /api/orders                  - Список заказов
GET    /api/orders/active           - Активные заказы
GET    /api/orders/{id}             - Заказ по ID
PATCH  /api/orders/{id}/status      - Обновить статус
GET    /api/track/{token}           - Публичный статус по токену
```

### Авторизация
```
POST   /api/auth/login              - Вход
GET    /api/auth/me                 - Текущий пользователь
```

### Организации & Локации
```
GET    /api/locations/public        - Публичный список точек
GET    /api/organizations           - Список организаций (admin/owner)
GET    /api/locations               - Список точек (по доступу)
```

### WebSocket
```
ws://api/ws/staff?location_id=...   - Для Staff App
ws://api/ws/display/{device_id}     - Для Display App  
ws://api/ws/client/{token}          - Для Client App
```

---

## ⚙️ Конфигурация

### Backend (.env)
```bash
DATABASE_URL=postgresql+asyncpg://user:pass@db:5432/qr_que
REDIS_URL=redis://redis:6379
JWT_SECRET_KEY=your-secret-key
CORS_ORIGINS=["https://staff.*", "https://display.*", "https://track.*"]
BASE_URL=https://track.kaskyralmaty.dev
```

### Frontend (.env.production)
```bash
VITE_API_URL=https://api.kaskyralmaty.dev
```

---

## 🚀 Деплой

```bash
# Клонировать и настроить
git clone <repo>
cd qr_que
cp backend/.env.example backend/.env

# Запустить в Docker
docker-compose up -d

# Применить миграции
docker-compose exec backend alembic upgrade head

# Создать демо-данные
docker-compose exec backend python -m app.seed
```

---

## 📝 Changelog

### v1.0 (Initial)
- Базовая система заказов
- 3 React приложения (staff, display, client)
- WebSocket для real-time обновлений
- Docker + Nginx

### v2.0 (Multi-tenant)
- Добавлены Organization, Location, User
- JWT авторизация
- Роли: admin, owner, manager, staff
- Фильтрация данных по доступу
- Выбор локации в Display App
- Форма входа в Staff App

### v3.0 (Display Auth + Admin Panel + Стабильность)
- Авторизация Display App с фильтрацией локаций
- Админ-панель: пользователи, организации, локации
- Автоматический переход pending→preparing при сканировании QR
- Защита от дубликатов заказов
- Поиск пользователей в админ-панели
- Удалены демо-ссылки из UI

---

## 🕐 Фаза 12: Display Auth + Admin Panel (02.01.2026, 17:50 - 18:05)
> Авторизация для Display App и административная панель

| Файл | Изменения |
|------|-----------|
| `display/components/Login.jsx` | **NEW** Форма входа для Display |
| `display/components/Login.css` | **NEW** Стили логина |
| `display/api.js` | +login, logout, getMe, isAuthenticated |
| `display/App.jsx` | Авторизация, фильтрация локаций, logout |
| `display/App.css` | +стили logout, user-badge |
| `staff/components/AdminPanel.jsx` | **NEW** CRUD пользователей/организаций/локаций |
| `staff/components/AdminPanel.css` | **NEW** Стили админ-панели с табами |
| `staff/api.js` | +getUsers, createUser, updateUser, resetUserPassword, getOrganizations, createOrganization, updateOrganization, createLocation, updateLocation |
| `staff/App.jsx` | +вкладки "Заказы" / "Управление" |
| `staff/App.css` | +стили табов |
| `staff/components/Login.jsx` | Удалена демо-подсказка |
| `backend/routes.py` | `/track/{token}` автоматически pending→preparing |

---

## 🕐 Фаза 13: Защита от дубликатов + Поиск (02.01.2026, 18:15 - 18:30)
> Исправление багов и UX улучшения

| Файл | Изменения |
|------|-----------|
| `backend/crud.py` | +check_duplicate_active_order, create_order проверяет дубликаты |
| `backend/routes.py` | +ValueError → 400 Bad Request с сообщением |
| `staff/components/NumPad.jsx` | +debounce защита от двойного клика |
| `staff/App.jsx` | +дедупликация заказов в WebSocket, +loading prop |
| `staff/components/AdminPanel.jsx` | +userSearch фильтр |
| `staff/components/AdminPanel.css` | +search-input стили |

### Ключевые изменения:
1. **Защита от дубликатов**: Нельзя создать заказ с номером, который уже активен на этой локации
2. **Debounce**: Кнопка "Создать заказ" блокируется на 500мс после нажатия
3. **WebSocket дедупликация**: Если такой заказ уже есть в списке, дубликат игнорируется
4. **Поиск пользователей**: Фильтр по имени, логину, email, организации, локации

---

*Документ обновлён: 2026-01-02*
https://display.kaskyralmaty.dev/