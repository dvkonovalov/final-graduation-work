FROM python:alpine

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY . .

CMD ["flask", "--app", "app.py", "run", "--host=0.0.0.0"]