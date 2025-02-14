.PHONY: db db-stop run test build
VENV_NAME=.venv

db:
	docker start mongo

db-stop:
	docker stop mongo

run:
	. ${VENV_NAME}/bin/activate && watchmedo auto-restart --recursive --patterns="*.py;*.yml" --directory="." python dasbot.py

test:
	. ${VENV_NAME}/bin/activate && python -m unittest

build:
	docker build -t dasbot .
