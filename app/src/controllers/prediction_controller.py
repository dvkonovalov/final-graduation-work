from flask import render_template, jsonify, request
import random
from src.models.cryptocurrency import Cryptocurrency
from src.db import db, button_clicks
import datetime
from src.logger import logger


def index():
    currencies = [
        {"name": "Bitcoin", "price": 45000, "change": 2.3},
        {"name": "Ethereum", "price": 3200, "change": -1.5},
        {"name": "Litecoin", "price": 180, "change": 0.7}
    ]
    return render_template('index.html', currencies=currencies)


async def update():
    button_clicks.inc()
    date = request.args.get('created_date')
    last_prediction_time = None
    try:
        last_prediction_time = datetime.datetime.strptime(date, "%a, %d %b %Y %H:%M:%S %Z")
    except:
        logger.warning(f"Невозможно конвертировать {date} в DateTime!")
    logger.debug(last_prediction_time)
    currencies = [
        {"name": "Bitcoin", "price": random.randint(40000, 50000), "change": random.uniform(-5, 5)},
        {"name": "Ethereum", "price": random.randint(3000, 4000), "change": random.uniform(-5, 5)},
        {"name": "Litecoin", "price": random.randint(150, 250), "change": random.uniform(-5, 5)}
    ]
    for currency in currencies:
        new_rec = Cryptocurrency(
            name = currency["name"],
            price = currency["price"],
            change = currency["change"]
        )
        await save_changes(new_rec)
    if last_prediction_time is not None:
        currencies = Cryptocurrency.query.filter(Cryptocurrency.created_date > last_prediction_time).all()
    else:
        logger.debug('get')
        currencies = Cryptocurrency.query.all()
    result = []
    for currency in currencies:
        result.append({
            "name": currency.name,
            "price": currency.price,
            "change": currency.change,
            "created_date": currency.created_date,
        })
    # logger.debug(jsonify(result))
    logger.debug(result)
    return jsonify(result)

async def save_changes(data) -> None:
    db.session.add(data)
    db.session.commit()
