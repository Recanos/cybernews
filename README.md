# CyberNews - Платформа для киберспортивных новостей и турниров

## Описание
CyberNews - это веб-платформа для публикации новостей из мира киберспорта, управления турнирами и отслеживания матчей. Платформа предоставляет функционал для администраторов, модераторов и обычных пользователей.

## Основные функции
- Публикация и управление новостями
- Комментирование новостей
- Управление турнирами и матчами
- Профили команд и игроков
- Система тегов и категорий
- Поиск по новостям и турнирам

## Технологии
- Python 3.12
- Django 5.0
- SQLite3
- Bootstrap 5
- Crispy Forms
- Django AllAuth

## Установка и запуск

1. Клонируйте репозиторий:
```bash
git clone https://github.com/Recanos/cybernews.git
cd cybernews
```

2. Создайте и активируйте виртуальное окружение:
```bash
python3 -m venv venv
source venv/bin/activate  # для Linux/Mac
# или
venv\Scripts\activate  # для Windows
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

4. Настройка переменных окружения:
   - Проверьте и при необходимости измените следующие настройки в файле .env:
     - `DJANGO_SECRET_KEY`: секретный ключ для Django (обязательно измените на свой)
     - `DJANGO_DEBUG`: режим отладки (True для разработки, False для продакшн)
     - `DJANGO_ALLOWED_HOSTS`: разрешенные хосты (localhost,127.0.0.1 для разработки)

5. Созданией миграций:
```bash
python3 manage.py makemigrations
```
Это создаст необходимые миграции.

6. Примените миграций:
```bash
python3 manage.py migrate
```
Это создаст необходимые таблицы в базе данных.

7. (Опционально) Загрузка тестовых данных:
```bash
python3 manage.py loaddata fixtures/initial_data.json fixtures/many_to_many.json
```
Это загрузит тестовые данные, включая:
- Тестовые аккаунты пользователей
- Примеры новостей
- Примеры турниров и матчей
⚠️ Внимание: загрузка тестовых данных перезапишет существующие данные в базе.

8. Создайте суперпользователя:
```bash
python3 manage.py createsuperuser
```
Следуйте инструкциям в консоли для создания администратора сайта.

9. Запустите сервер разработки:
```bash
python3 manage.py runserver
```
Сервер будет доступен по адресу http://127.0.0.1:8000/

## Конфигурация приложения

### Настройка отправки email

#### Разработка
В режиме разработки письма выводятся в консоль. Для этого в `settings.py` используется:
```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

#### Продакшн
Для отправки реальных писем в продакшн:

1. В `settings.py` раскомментируйте и настройте параметры SMTP:
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'  # Для Gmail
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'  # Используйте пароль приложения для Gmail
DEFAULT_FROM_EMAIL = 'CyberNews <noreply@cybernews.com>'
```

2. Для Gmail:
   - Включите двухфакторную аутентификацию
   - Создайте пароль приложения в настройках безопасности Google Account
   - Используйте этот пароль в `EMAIL_HOST_PASSWORD`

### Настройка статических файлов

В режиме разработки статические файлы обрабатываются автоматически. Для продакшн:

1. Соберите статические файлы:
```bash
python3 manage.py collectstatic
```

2. Убедитесь, что в `settings.py` настроены:
```python
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
```

### Настройка медиафайлов

В режиме разработки медиафайлы обрабатываются автоматически. Директория `media` будет создана автоматически при первой загрузке файла.

Убедитесь, что в `settings.py` настроены:
```python
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

## Тестовые аккаунты

Для тестирования доступны следующие аккаунты:

1. Администратор:
   - Логин: admin
   - Почта: admin@cybernews.com
   - Пароль: admin123

2. Модератор:
   - Логин: moderator
   - Почта: moderator@cybernews.com
   - Пароль: moderator123

## Лицензия

MIT 
