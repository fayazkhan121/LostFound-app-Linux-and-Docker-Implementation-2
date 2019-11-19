#!/bin/sh

echo "Waiting for Mysql..."

while ! nc -z lostfound-db 3306; do
  sleep 0.1
done

echo "Mysql started"

python manage.py run -h 0.0.0.0