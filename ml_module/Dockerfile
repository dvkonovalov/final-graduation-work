FROM python:slim

RUN apt-get update && apt-get install -y build-essential gcc pkg-config cmake && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt --extra-index-url https://download.pytorch.org/whl/cpu

COPY . .

CMD ["python", "app.py"]