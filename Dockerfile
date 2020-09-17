FROM python:3.8-alpine

WORKDIR /code

COPY . .

RUN pip install -r requirements.txt

RUN python entrypoint.py

CMD ["python", "./main.py"]