import pandas as pd
from sklearn.svm import SVR
from sklearn.ensemble import RandomForestRegressor
from prophet import Prophet

def train_and_predict(data, algorithm="SVM"):
    df = pd.DataFrame(data)
    df = df.sort_values("date")  # مرتب کردن بر اساس تاریخ

    # ویژگی ها
    X = df[["first_price", "highest_price", "lowest_price", "close_price", "trade_volume"]].values
    y = df["close_price"].values

    # تقسیم داده: 25 روز train، 5 روز test
    X_train, y_train = X[:-5], y[:-5]
    X_test = X[-5:]

    if algorithm == "SVM":
        model = SVR()
        model.fit(X_train, y_train)
        pred = model.predict(X_test)
    elif algorithm == "RandomForest":
        model = RandomForestRegressor()
        model.fit(X_train, y_train)
        pred = model.predict(X_test)
    elif algorithm == "Prophet":
        # Prophet نیاز به فرمت خاص دارد
        df_prophet = pd.DataFrame({
            "ds": pd.to_datetime(df["date"]),
            "y": df["close_price"]
        })
        model = Prophet()
        model.fit(df_prophet[:-5])
        future = model.make_future_dataframe(periods=5)
        forecast = model.predict(future)
        pred = forecast["yhat"][-5:].values
    else:
        pred = []

    # پیشنهاد ساده: اگر میانگین پیش‌بینی > آخرین قیمت => buy
    last_price = y_train[-1]
    avg_pred = sum(pred)/len(pred)
    if avg_pred > last_price:
        suggestion = "buy"
    else:
        suggestion = "sell"

    return list(pred), suggestion
