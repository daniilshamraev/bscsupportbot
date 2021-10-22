release: python3 ./bscsupportbot/manage.py migrate
worker: python3 ./bscsupportbot/manage.py bot
web: cd app/bscsupportbot/;gunicorn BSCSupportBot.wsgi --log-file -