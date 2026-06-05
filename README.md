# REST API для ФСТР (Федерация Спортивного Туризма России)

## О проекте

Проект выполнен в рамках виртуальной стажировки от SkillFactory.

**Задача:** Разработать REST API для мобильного приложения, которое позволит туристам отправлять данные о горных перевалах в ФСТР.

## Технологии

- Python 3.9+
- FastAPI
- PostgreSQL
- Render.com (хостинг)

## Методы API

Базовый URL: `https://fstr-pereval.onrender.com`

### 1. Добавление перевала
- **POST** `/submitData`
- Пример тела запроса в Swagger

### 2. Получение перевала по ID
- **GET** `/submitData/{id}`

### 3. Редактирование перевала
- **PATCH** `/submitData/{id}`
- Только для статуса `new`

### 4. Список перевалов пользователя
- **GET** `/submitData/?user_email=<email>`

## Swagger

Документация API: `https://fstr-pereval.onrender.com/docs`

## GitHub

Репозиторий: `https://github.com/NB-hub15/fstr_pereval`