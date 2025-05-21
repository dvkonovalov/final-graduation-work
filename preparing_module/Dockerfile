FROM python:alpine

# Устанавливаем рабочую директорию
WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

# Копируем файлы приложения внутрь контейнера
COPY . .

# Запускаем приложение
CMD ["flask", "--app", "app.py", "run", "--host=0.0.0.0"]