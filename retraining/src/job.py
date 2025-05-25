import pandas as pd
from datetime import datetime, timedelta

from src.models.cryptocurrency import Cryptocurrency
from src.db import db, Bitcoin_MSE, Etherium_MSE, Litecoin_MSE
from src.logger import logger

currency_dict = {
    'Bitcoin': Bitcoin_MSE,
    'Ethereum': Etherium_MSE,
    'Litecoin': Litecoin_MSE
}

def read_from_db(collection : str) -> pd.DataFrame:
    docs = list(db[collection].find())
    df_from_mongo = pd.DataFrame(docs)

    df_from_mongo.drop(columns=["_id"], inplace=True)
    return df_from_mongo

def get_all_collections() -> bool:
    return db.list_collection_names()
    
    
def job():
    today = datetime.now()
    yesterday = today - timedelta(days=1)
    
    collections = []
    for collection in get_all_collections():
        if collection.startswith('backup_historical'):
            collections.append(collection)
            
    for collection in collections:
        currency_name = collection.split('_')[-1]
        currency_backup = read_from_db(collection)
        
        currency = Cryptocurrency.query.filter((Cryptocurrency.name == currency_name[0].upper() + currency_name[1:]) & (Cryptocurrency.created_date == yesterday)).first()
        
        currency_backup['timestamp'] = pd.to_datetime(currency_backup['timestamp'])
        df_yesterday = currency_backup.loc[currency_backup['timestamp'].dt.date == yesterday.date]
        if not df_yesterday.empty and currency:
            currency_dict[currency.name].set((df_yesterday["close"] - currency.price)**2)
        
        