FROM python:3.8

WORKDIR /usr/src/app 
COPY . .

RUN python3 -m pip install --no-cache-dir -r ./requirements.txt

CMD [ "python3", "./dasbot.py" ]
