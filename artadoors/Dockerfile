# Используем официальный образ Python
FROM python:3.11-rc-slim  

# Устанавливаем системные зависимости
RUN apt-get update && \
    apt-get install -y libjpeg-dev zlib1g-dev liblcms2-dev libopenjp2-7-dev libtiff5-dev libpq-dev gcc postgresql-client netcat

# Устанавливаем рабочую директорию
WORKDIR /code  

# Копируем файлы проекта
COPY . /code  

# Копируем wait-for-it.sh для ожидания базы данных
COPY wait-for-it.sh /wait-for-it.sh
RUN chmod +x /wait-for-it.sh

# Устанавливаем зависимости
RUN pip install --upgrade pip
RUN pip install pillow==11.0.0 --only-binary :all:
RUN pip install --timeout=120 --no-cache-dir -r requirements/prod.txt

# Устанавливаем переменные окружения
ENV APP_NAME=ARTADOORS  
ENV DJANGO_SETTINGS_MODULE=artadoors.settings.prod

# Запускаем Gunicorn для Django
CMD ["/wait-for-it.sh", "db:5432", "--strict", "--timeout=60", "--", "sh", "-c", "python manage.py collectstatic --noinput && gunicorn artadoors.wsgi:application -b 0.0.0.0:8000 --workers 4 --timeout 60"]
