#!/bin/sh
python app.py --port 8000
gunicorn -c ./gunicorn_setting/gunicorn_config.py app.main:app