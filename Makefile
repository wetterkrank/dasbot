.PHONY: db db-stop run test docker-build
VENV_NAME=.venv

db:
	docker start mongo

db-stop:
	docker stop mongo

run:
	${VENV_NAME}\Scripts\activate && python dasbot.py

test: 
	${VENV_NAME}\Scripts\activate && python -m unittest

build:
	docker build -t dasbot .
