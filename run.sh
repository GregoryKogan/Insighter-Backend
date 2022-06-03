#!/bin/sh

export FLASK_APP=./src/app.py

source venv/bin/activate

flask run -h 127.0.0.1
