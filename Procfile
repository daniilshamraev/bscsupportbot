release: python3 ./manage.py makemigrations;python3 ./manage.py migrate
worker: python3 ./manage.py bot
web: gunicorn BSCSupportBot.wsgi --log-file -