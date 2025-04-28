import pandas as pd
import os

file_path = 'backups/backup_historical.csv'

# Проверим, что файл существует и не пустой
if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
    try:
        # Попробуем прочитать файл
        df = pd.read_csv(file_path)
        print("Файл успешно загружен:")
        print(df.head())  # Печать первых 5 строк файла
    except pd.errors.EmptyDataError:
        print(f"Ошибка: файл {file_path} пуст!")
    except pd.errors.ParserError:
        print(f"Ошибка при парсинге файла {file_path}!")
else:
    print(f"Файл {file_path} не существует или пуст!")
