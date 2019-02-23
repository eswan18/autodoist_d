FROM python:3.7

WORKDIR /autodoist/

COPY ./requirements.txt /autodoist/

RUN pip install -r requirements.txt

COPY . /autodoist

CMD python src/main.py
