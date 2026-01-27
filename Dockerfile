FROM python:3.12-bookworm

COPY ./requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY ./earnin_airline earnin_airline/

CMD fastapi run earnin_airline/app.py
