# Система Аккаунтов / Account System

## Структура

### Организация (Organization)
Представляет сеть/бренд (например, "KFC", "Burger King"). Одна организация может иметь несколько точек.

### Точка (Location)  
Конкретная точка продаж в определенном ТРЦ/месте. Привязана к организации.

### Пользователь (User)
Имеет роль и доступ к определенным данным.

## Роли пользователей

| Роль | Описание | Доступ |
|------|----------|--------|
| `admin` | Супер-администратор | Видит все организации, точки и заказы |
| `owner` | Владелец сети | Видит все точки и заказы своей организации |
| `manager` | Менеджер точки | Видит заказы своей точки |
| `staff` | Персонал (касса) | Создает и управляет заказами своей точки |

## Тестовые аккаунты

После запуска `python -m app.seed`:

### Admin (видит всё)
```
Username: admin
Password: admin123
```

### Demo Owner (владелец демо-сети)
```
Username: demo
Password: demo123
```

### Demo Staff (персонал по точкам)
```
Username: demo_staff_1, demo_staff_2, demo_staff_3
Password: staff123
```

### Sample KFC Owner
```
Username: kfc_owner
Password: kfc123
```

## API Endpoints

### Аутентификация

```bash
# Login (form data)
POST /api/auth/login
Content-Type: application/x-www-form-urlencoded
username=demo&password=demo123

# Login (JSON)
POST /api/auth/login/json
{"username": "demo", "password": "demo123"}

# Get current user
GET /api/auth/me
Authorization: Bearer <token>

# Change password
PUT /api/auth/password
{"current_password": "...", "new_password": "..."}
```

### Организации

```bash
# List organizations (admin sees all, others see their own)
GET /api/organizations

# Get organization
GET /api/organizations/{id}

# Create organization (admin only)
POST /api/organizations
{"name": "New Restaurant", "slug": "new-restaurant"}

# Update organization
PATCH /api/organizations/{id}
{"name": "Updated Name"}
```

### Точки

```bash
# List locations
GET /api/locations
GET /api/locations?organization_id=...

# Get location
GET /api/locations/{id}

# Create location (admin or owner)
POST /api/locations
{
  "organization_id": "...",
  "name": "New Location",
  "slug": "new-location",
  "mall_name": "Mega",
  "city": "Almaty"
}

# Update location
PATCH /api/locations/{id}
```

### Пользователи

```bash
# List users
GET /api/users
GET /api/users?organization_id=...
GET /api/users?location_id=...

# Get user
GET /api/users/{id}

# Create user (admin or owner)
POST /api/users
{
  "username": "new_user",
  "password": "password123",
  "role": "staff",
  "organization_id": "...",
  "location_id": "..."
}

# Update user
PATCH /api/users/{id}

# Reset password
PUT /api/users/{id}/password
{"new_password": "..."}
```

### Заказы (обновленные)

Теперь заказы фильтруются по доступу пользователя:

```bash
# Get active orders (filtered by user's access)
GET /api/orders/active
GET /api/orders/active?location_id=...

# Create order
POST /api/orders
{
  "human_id": "A-47",
  "device_id": "tab_1",
  "location_id": "..."  # Optional if user has assigned location
}
```

## Логика доступа

### Заказы
- **Admin**: видит все заказы
- **Owner**: видит заказы всех точек своей организации
- **Manager/Staff**: видит заказы только своей точки

### WebSocket
При подключении можно передать `location_id`:
```
ws://host/api/ws/staff?location_id=<uuid>
```

- Без параметра: получает все сообщения (для admin)
- С параметром: получает только сообщения для указанной точки

## Пример: Сеть с несколькими точками в разных ТРЦ

```
Organization: "Burger Lab"
├── Location: "Burger Lab - Mega Almaty"
│   ├── mall_name: "Mega Almaty"
│   ├── city: "Almaty"
│   └── Users: staff_mega_1, staff_mega_2
│
├── Location: "Burger Lab - Dostyk Plaza"
│   ├── mall_name: "Dostyk Plaza"
│   ├── city: "Almaty"
│   └── Users: staff_dostyk_1
│
└── Location: "Burger Lab - Khan Shatyr"
    ├── mall_name: "Khan Shatyr"
    ├── city: "Astana"
    └── Users: staff_astana_1
```

Owner организации может:
- Видеть заказы всех 3-х точек
- Создавать менеджеров и персонал для любой точки
- Переключаться между точками в интерфейсе

Staff конкретной точки:
- Видит только заказы своей точки
- Не может переключаться на другие точки

## Запуск миграций

```bash
cd backend

# Применить миграции
alembic upgrade head

# Создать начальные данные
python -m app.seed
```

## Environment Variables

```env
# JWT Settings
SECRET_KEY=your-very-long-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=10080  # 7 days

# Default Admin
ADMIN_USERNAME=admin
ADMIN_PASSWORD=secure_admin_password

# Demo Account
DEMO_USERNAME=demo
DEMO_PASSWORD=demo123
```
