token = "c35544a67970a51a73e693a8208610d3"
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import requests
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import SVR

router = APIRouter()

class PredictionRequest(BaseModel):
    symbol: str
    days: int = 30
    algorithm: str = "RandomForest"

@router.post("/predict")
def predict(request: PredictionRequest):
    # 1️⃣ گرفتن داده‌های گذشته
    url = f"https://apis.sourcearena.ir/api/?token=cc722f3bef3fa3cc7d013064047d86c8&name={request.symbol}&days={request.days}"
    try:
        response = requests.get(url, timeout=20)
        response.raise_for_status()
        data = response.json()
        df = pd.DataFrame(data)
        df = df[["first_price","highest_price","lowest_price","close_price","trade_volume"]].astype(float)

        # 2️⃣ آماده‌سازی X و y
        X = df[["first_price","highest_price","lowest_price","trade_volume"]]
        y = df["close_price"]

        # 3️⃣ انتخاب مدل
        if request.algorithm == "RandomForest":
            model = RandomForestRegressor(n_estimators=100, random_state=42)
        elif request.algorithm == "SVM":
            model = SVR()
        else:
            raise HTTPException(status_code=400, detail="الگوریتم معتبر نیست")

        # 4️⃣ ترین مدل
        model.fit(X, y)

        # 5️⃣ پیش‌بینی روزهای آینده (اینجا 10 روز)
        # فرض می‌کنیم آخرین X را تکرار می‌کنیم برای پیش‌بینی آینده
        last_row = X.iloc[-1:].values
        predictions = []
        for _ in range(10):
            pred = model.predict(last_row)[0]
            predictions.append(round(pred, 2))
            # update last_row برای روز بعد
            last_row[0][0] = pred  # first_price
            last_row[0][1] = pred  # highest_price
            last_row[0][2] = pred  # lowest_price
            last_row[0][3] = last_row[0][3]  # trade_volume ثابت

        return {"symbol": request.symbol, "predictions": predictions}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ارتباط برقرار نشد یا داده ناقص: {e}")
