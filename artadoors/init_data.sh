#!/bin/sh
docker exec django_app python manage.py migrate
echo "⏳ Ждём запуск базы данных..."
sleep 5  # Ждём, пока PostgreSQL поднимется

echo "🚀 Загружаем фикстуры..."
docker exec django_app python manage.py flush --no-input
docker exec django_app python manage.py loaddata shop_data.json

echo "🔄 Обновляем последовательности ID..."
docker exec django_app python manage.py sqlsequencereset shop | docker exec -i django_app python manage.py dbshell

echo "✅ Данные загружены!"
