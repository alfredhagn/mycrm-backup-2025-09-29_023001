#!/bin/bash
set -e

echo "📦 System vorbereiten..."
apt update && apt install -y python3 python3-pip python3-venv default-libmysqlclient-dev build-essential unzip

echo "🛠 Virtuelle Umgebung erstellen..."
python3 -m venv venv
source venv/bin/activate

echo "📦 Abhängigkeiten installieren..."
pip install -r requirements.txt

echo "📂 Migrationen durchführen..."
python manage.py makemigrations
python manage.py migrate

echo "👤 Superuser anlegen..."
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('alfred', 'alfred@example.com', 'ddcm9677')" | python manage.py shell

echo "🚀 Entwicklungsserver starten..."
python manage.py runserver 0.0.0.0:8000