FROM python:3.7

WORKDIR /autodoist_d/

COPY ./requirements.txt /autodoist_d/

RUN pip install -r requirements.txt

COPY src /autodoist_d/src

CMD python src/main.py
