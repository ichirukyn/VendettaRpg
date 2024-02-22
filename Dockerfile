FROM python:3.10-slim

WORKDIR /usr/src/app/"vendetta-bot"

COPY requirements.txt /usr/src/app/"vendetta-bot"
RUN pip install -r /usr/src/app/"vendetta-bot"/requirements.txt
COPY . /usr/src/app/"vendetta-bot"

CMD ["python", "bot.py"]