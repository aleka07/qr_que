# QR Queue Testing Guide

## Локальное тестирование

### 1. Запуск Backend

```bash
# Создать виртуальное окружение
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или venv\Scripts\activate  # Windows

# Установить зависимости
pip install -r requirements.txt

# Запустить PostgreSQL и Redis (Docker)
cd ..
docker-compose up -d db redis

# Применить миграции
cd backend
alembic upgrade head

# Запустить сервер
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend будет доступен на: http://localhost:8000

API Documentation: http://localhost:8000/docs

### 2. Запуск Frontend приложений

Откройте три отдельных терминала:

#### Terminal 1 - Staff App
```bash
cd frontend/staff
npm install
npm run dev
```
Доступен на: http://localhost:3000

#### Terminal 2 - Display App
```bash
cd frontend/display
npm install
npm run dev
```
Доступен на: http://localhost:3001

#### Terminal 3 - Client App
```bash
cd frontend/client
npm install
npm run dev
```
Доступен на: http://localhost:3002

## Сценарий тестирования

### Шаг 1: Подготовка
1. Откройте Staff App в браузере: http://localhost:3000
2. Откройте Display App в другой вкладке: http://localhost:3001
3. Откройте консоль разработчика (F12) в обеих вкладках

### Шаг 2: Создание заказа
1. В Staff App:
   - Выберите планшет (например, "Планшет 1")
   - Введите номер заказа (например, "47")
   - Нажмите "Создать заказ" или Enter

2. Проверьте:
   - ✅ Заказ появился в списке активных заказов
   - ✅ В Display App появился QR-код
   - ✅ QR-код показывает номер заказа "47"

### Шаг 3: Сканирование QR-кода
1. Отсканируйте QR-код или скопируйте URL из Display App
2. Откройте URL в новой вкладке или на мобильном устройстве
3. Проверьте:
   - ✅ Client App открылся с номером заказа
   - ✅ Статус: "Ожидание"
   - ✅ WebSocket подключен

### Шаг 4: Изменение статуса
1. В Staff App кликните на карточку заказа
2. Статус автоматически изменится на следующий:
   - pending → scanned → preparing → ready → completed

3. Проверьте в Client App:
   - ✅ Статус обновился в реальном времени
   - ✅ Изменился цвет и emoji
   - ✅ Прогресс-бар обновился
   - ✅ При статусе "ready" появилась анимация и вибрация (на мобильном)

### Шаг 5: Тест WebSocket
1. Откройте консоль разработчика в Client App
2. Закройте вкладку и откройте снова через 5 секунд
3. Проверьте:
   - ✅ WebSocket переподключился
   - ✅ Актуальный статус загрузился

## Тестирование API напрямую

### Создать заказ
```bash
curl -X POST http://localhost:8000/api/orders \
  -H "Content-Type: application/json" \
  -d '{
    "human_id": "A-42",
    "device_id": "tab_1"
  }'
```

### Получить список заказов
```bash
curl http://localhost:8000/api/orders/active
```

### Обновить статус
```bash
curl -X PATCH http://localhost:8000/api/orders/{order_id}/status \
  -H "Content-Type: application/json" \
  -d '{"status": "ready"}'
```

### Получить заказ по токену
```bash
curl http://localhost:8000/api/track/{token}
```

## Тестирование WebSocket

Используйте wscat для тестирования WebSocket соединений:

```bash
# Установить wscat
npm install -g wscat

# Staff WebSocket
wscat -c ws://localhost:8000/api/ws/staff

# Display WebSocket
wscat -c ws://localhost:8000/api/ws/display/tab_1

# Client WebSocket
wscat -c ws://localhost:8000/api/ws/client/{token}
```

## Docker-based тестирование

```bash
# Запустить все сервисы
./scripts/setup.sh

# Проверить логи
docker-compose logs -f backend

# Проверить здоровье сервисов
curl http://localhost:8000/health
```

## Проблемы и решения

### Backend не запускается
- Проверьте, что PostgreSQL и Redis запущены
- Проверьте .env файл
- Проверьте логи: `docker-compose logs backend`

### Frontend не подключается к API
- Проверьте URL в файлах `api.js`
- Проверьте CORS настройки в backend
- Откройте Network tab в DevTools

### WebSocket не работает
- Проверьте консоль браузера на ошибки
- Убедитесь, что backend запущен
- Проверьте, что порт 8000 открыт

### QR-код не отображается
- Проверьте, что библиотека qrcode установлена
- Проверьте логи Display App в консоли
- Проверьте WebSocket соединение

## Метрики для проверки

- ✅ Время создания заказа < 500ms
- ✅ WebSocket latency < 100ms
- ✅ QR-код отображается < 2 секунды
- ✅ Обновление статуса в реальном времени < 200ms
- ✅ Автоматическое переподключение WebSocket работает
