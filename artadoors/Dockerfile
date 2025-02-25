FROM python:3.11-rc-slim  

# Обновляем пакеты и устанавливаем зависимости
RUN apt-get update && \
    apt-get install -y libjpeg-dev zlib1g-dev liblcms2-dev libopenjp2-7-dev libtiff5-dev libpq-dev gcc postgresql-client netcat

# Создаем и устанавливаем рабочую директорию
WORKDIR /code  

# Копируем файлы проекта
COPY . /code  

# Копируем wait-for-it.sh и делаем его исполняемым
COPY wait-for-it.sh /wait-for-it.sh
RUN chmod +x /wait-for-it.sh

# Устанавливаем зависимости
RUN pip install --upgrade pip
RUN pip install pillow==11.0.0 --only-binary :all:
RUN pip install --timeout=120 --no-cache-dir -v -r requirements/prod.txt

# Копируем переменные окружения
COPY .env.docker /code/.env  

# Устанавливаем переменные окружения (без пробелов вокруг `=`)
ENV APP_NAME=ARTADOORS  
ENV DJANGO_SETTINGS_MODULE=artadoors.settings.prod

# Запускаем Gunicorn с 3 воркерами и увеличенным таймаутом
CMD ["/wait-for-it.sh", "db:5432", "--strict", "--timeout=60", "--", "gunicorn", "artadoors.wsgi:application", "-b", "0.0.0.0:8000", "--workers", "3", "--timeout", "120"]
