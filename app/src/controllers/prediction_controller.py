from flask import render_template, jsonify, request
import random
from src.models.cryptocurrency import Cryptocurrency
from src.db import db, update_clicks, site_entered
import datetime
from src.logger import logger


def index():
    return render_template('index.html')


async def update():
    update_clicks.inc()
    date = request.args.get('created_date')
    
    last_prediction_time = None
    try:
        last_prediction_time = datetime.datetime.strptime(date, "%a, %d %b %Y %H:%M:%S %Z")
    except:
        logger.warning(f"Невозможно конвертировать {date} в DateTime!")
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
        currencies = Cryptocurrency.query.all()
    result = []
    for currency in currencies:
        result.append({
            "name": currency.name,
            "price": currency.price,
            "change": currency.change,
            "created_date": currency.created_date,
        })
    return jsonify(result)

def get_all_data():
    site_entered.inc()
    currencies = Cryptocurrency.query.all()
    result = []
    for currency in currencies:
        result.append({
            "name": currency.name,
            "price": currency.price,
            "change": currency.change,
            "created_date": currency.created_date,
        })
    return jsonify(result)

async def save_changes(data) -> None:
    db.session.add(data)
    db.session.commit()
