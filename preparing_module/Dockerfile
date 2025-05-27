FROM python:slim

RUN apt-get update && apt-get install -y build-essential gcc pkg-config cmake && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN pip install --upgrade pip

RUN pip install --upgrade setuptools

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt --extra-index-url https://download.pytorch.org/whl/cpu

COPY requirements2.txt requirements2.txt 

RUN pip install -r requirements2.txt --extra-index-url https://download.pytorch.org/whl/cpu

COPY . .

CMD ["python", "app.py"]