from datetime import datetime, timedelta
import random

# Начальная дата и время
start_date = datetime.strptime("2025-04-25 00:00:00", "%Y-%m-%d %H:%M:%S")
step = timedelta(minutes=10)

# Начальные значения для колонок
initial_value = 50000
last_open = initial_value
last_high = last_open + random.randint(0, 500)
last_low = last_open - random.randint(0, 500)
last_close = int((last_open + last_high + last_low) / 3)
volume = random.randint(1000, 2000)

for i in range(100):
    current_time = start_date + step * i
    formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")[:-3]

    # Изменяем цену и объем
    open_price = last_close
    high_price = max(open_price + random.randint(0, 500), last_high)
    low_price = min(open_price - random.randint(0, 500), last_low)
    close_price = int((open_price + high_price + low_price) / 3)
    volume = random.randint(1000, 2000)

    # Обновляем предыдущие цены
    last_open = open_price
    last_high = high_price
    last_low = low_price
    last_close = close_price

    # Создаем строку
    line = f"{formatted_time},{open_price},{high_price},{low_price},{close_price},{volume}"
    print(line)