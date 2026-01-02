Принято. Переходим на **Python** (отличный выбор для бэкенда благодаря чистоте кода и скорости разработки) и строим архитектуру на **субдоменах**.

Это "Enterprise-ready" подход: каждый сервис изолирован на своем уровне.

---

# Техническое Задание (ТЗ): Digital Pager System (Python Edition)

**Основной домен:** `kaskyralmaty.dev` (Пустой / 403 Forbidden)
**Цель:** Система управления выдачей заказов для фудкортов (Manual Input Flow).
**Стек:**

* **Backend:** Python 3.11+ (**FastAPI**) — идеален для асинхронных WebSockets и высокой нагрузки.
* **Database:** PostgreSQL + **SQLAlchemy (Async)**.
* **Broker/Cache:** Redis (для обмена сообщениями между процессами Python).
* **Infrastructure:** Docker, Nginx (Reverse Proxy).
* **Frontend:** React (Vite) или Next.js (SSG export) — статика, раздаваемая Nginx.

---

## 🏗 Эпик 1: Инфраструктура и Маршрутизация (DevOps)

*Цель: Настроить сервер так, чтобы субдомены вели в нужные места.*

### 🎫 Ticket 1.1: Структура Nginx и Субдоменов

* **Описание:** Настроить конфигурацию Nginx (`sites-available`).
* `kaskyralmaty.dev` -> **Return 404** (или пустая белая страница).
* `api.kaskyralmaty.dev` -> `proxy_pass http://backend:8000` (FastAPI).
* `staff.kaskyralmaty.dev` -> `root /var/www/staff` (Статика React: Пульт управления).
* `display.kaskyralmaty.dev` -> `root /var/www/display` (Статика React: Планшет с QR).
* `track.kaskyralmaty.dev` -> `root /var/www/client` (Статика React: Телефон клиента).


* **Результат:** Четкое разделение доступов.

### 🎫 Ticket 1.2: Docker Compose для Python

* **Описание:** Написать `docker-compose.yml`.
* Service `db`: PostgreSQL.
* Service `redis`: Redis Alpine.
* Service `backend`: Python container (uvicorn start).


* **Результат:** Команда `docker-compose up` поднимает всю связку.

---

## 🐍 Эпик 2: Бэкенд (Python / FastAPI)

*Цель: Логика создания заказов и WebSocket Manager.*

### 🎫 Ticket 2.1: Модели данных (SQLAlchemy Async)

* **Описание:** Создать модель `Order`.
```python
class Order(Base):
    __tablename__ = "orders"
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    human_id = Column(String)  # Например "A-47"
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING)
    token = Column(String, unique=True) # Для ссылки клиента
    device_id = Column(String) # ID планшета кассы
    created_at = Column(DateTime, default=datetime.utcnow)

```


* **Результат:** Таблица создается в БД через Alembic (миграции).

### 🎫 Ticket 2.2: WebSocket Manager (Связь в реальном времени)

* **Описание:** Реализовать класс `ConnectionManager` в FastAPI.
* Хранить активные соединения: `List[WebSocket]`.
* Методы: `connect`, `disconnect`, `broadcast_to_staff`, `send_to_display`, `send_to_client`.


* **Технология:** Использовать нативные WebSockets FastAPI (`from fastapi import WebSocket`).

### 🎫 Ticket 2.3: API Эндпоинты (REST)

* **Описание:**
* `POST /orders`: Принимает `{human_id: "47", device_id: "tab_1"}`.
* Сохраняет в БД.
* **Асинхронно** отправляет сообщение в WebSocket планшета: "Покажи QR для заказа 47".


* `PATCH /orders/{id}/status`: Смена статуса.
* Триггерит уведомление клиенту.


* `GET /orders`: Список активных заказов (для Staff).



---

## 📱 Эпик 3: Приложения Фронтенда (React)

*Мы делаем 3 маленьких отдельных приложения (или одно с разным роутингом, но лучше отдельные билды для чистоты).*

### 🎫 Ticket 3.1: Staff App (`staff.kaskyralmaty.dev`)

* **Задача:** Интерфейс для быстрого набора.
* **Компоненты:**
* `NumPad`: Кнопки 0-9, Enter.
* `OrderList`: Сетка карточек.
* `SocketClient`: Подключение к `wss://api.kaskyralmaty.dev/ws/staff`.


* **Логика:** Ввел "47" -> Нажал Enter -> POST запрос улетел -> Список обновился.

### 🎫 Ticket 3.2: Display App (`display.kaskyralmaty.dev`)

* **Задача:** "Глупый" экран.
* **Логика:**
1. При открытии генерирует уникальный `device_id` (и сохраняет в LocalStorage), чтобы сервер знал, какой именно кассе слать команду.
2. Соединяется по WS: `wss://api.kaskyralmaty.dev/ws/display/{device_id}`.
3. Ждет команду `{type: "SHOW_QR", url: "https://track.kaskyralmaty.dev/xyz"}`.
4. Показывает QR на 30 секунд.



### 🎫 Ticket 3.3: Client App (`track.kaskyralmaty.dev`)

* **Задача:** Мобильный веб-пейджер.
* **Логика:**
1. Парсит токен из URL (например `track.kaskyralmaty.dev/?t=xyz`).
2. Делает GET запрос за текущим статусом.
3. Открывает WS соединение: `wss://api.kaskyralmaty.dev/ws/client/{token}`.
4. При получении `{status: "READY"}` -> Вибрация + Зеленый фон.

---