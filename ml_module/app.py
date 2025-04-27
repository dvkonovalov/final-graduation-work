# app.py

from fastapi import FastAPI
from train import train_models
from predict import predict_price
from pydantic import BaseModel
import uvicorn

app = FastAPI()

class PredictRequest(BaseModel):
    features: dict  # словарь: {feature_name: value}

@app.post("/train")
def train_endpoint():
    train_models()
    return {"status": "success", "message": "Models trained and saved."}

@app.post("/predict")
def predict_endpoint(request: PredictRequest):
    prediction = predict_price(request.features)
    return {"status": "success", "prediction": prediction}

if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
