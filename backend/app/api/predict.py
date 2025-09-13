# backend/app/api/predict.py
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
import requests
import pandas as pd
from sklearn.svm import SVR
from sklearn.ensemble import RandomForestRegressor
from urllib.parse import quote

router = APIRouter()

class PredictRequest(BaseModel):
    symbol: str
    days: int
    algorithm: str

@router.post("/predict")
async def predict_stock(request: Request):
    try:
        # دریافت داده خام از کلاینت
        data_json = await request.json()
        print("Raw JSON received:", data_json)

        # تبدیل به PredictRequest
        req = PredictRequest(**data_json)
        print(f"Parsed Request -> Symbol: {req.symbol}, Days: {req.days}, Algorithm: {req.algorithm}")

        # آماده‌سازی URL و درخواست API
        symbol_encoded = quote(req.symbol)
        url = f"https://apis.sourcearena.ir/api/?token=cc722f3bef3fa3cc7d013064047d86c8&name={symbol_encoded}&days={req.days}"
        headers = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()
        data = response.json()

        if not data:
            raise HTTPException(status_code=404, detail="داده‌ای یافت نشد")

        # تبدیل به DataFrame و انتخاب ویژگی‌ها
        df = pd.DataFrame(data)
        df = df.rename(columns={
            "first_price": "pf",
            "highest_price": "pmax",
            "lowest_price": "pmin",
            "close_price": "pc",
            "trade_volume": "tvol"
        })
        df["py"] = df["pc"].shift(1)
        df = df.dropna()
        features = df[["pf","pmax","pmin","py","pc","tvol"]]
        target = df["pc"]

        if len(features) < 2:
            raise HTTPException(status_code=500, detail="داده کافی برای پیش‌بینی وجود ندارد")

        # انتخاب مدل
        if req.algorithm == "SVM":
            model = SVR()
        elif req.algorithm == "RandomForest":
            model = RandomForestRegressor()
        else:
            raise HTTPException(status_code=400, detail="الگوریتم نامعتبر است")

        # آموزش مدل
        model.fit(features, target)

        # پیش‌بینی ۱۰ روز آینده بدون گرد کردن
        last_features = features.tail(1).copy()
        predictions = []
        for _ in range(10):
            pred = model.predict(last_features)[0]
            predictions.append(pred)  # عدد دقیق اضافه می‌شود
            # بروزرسانی py و pc برای روز بعد
            last_features.iloc[0, 3] = last_features.iloc[0, 4]  # py = pc
            last_features.iloc[0, 4] = pred  # pc = pred

        return {"symbol": req.symbol, "predictions": predictions}

    except Exception as e:
        print("Error:", e)
        raise HTTPException(status_code=500, detail=f"خطای سرور: {e}")
