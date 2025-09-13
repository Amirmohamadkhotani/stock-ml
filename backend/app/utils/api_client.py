# backend/app/utils/api_client.py
import os
import asyncio
from typing import Optional
from datetime import datetime
import httpx
import pandas as pd
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", "..", ".env"))

BASE_URL = os.getenv("EXCHANGE_API_URL", "").rstrip("/")
API_KEY = os.getenv("EXCHANGE_API_KEY", "")
REQUEST_TIMEOUT = float(os.getenv("REQUEST_TIMEOUT", "10"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "4"))

# یک client سراسری async (ببندش با close_client وقتی تمام شد)
_client: Optional[httpx.AsyncClient] = None

def get_client() -> httpx.AsyncClient:
    global _client
    if _client is None:
        _client = httpx.AsyncClient(timeout=REQUEST_TIMEOUT)
    return _client

async def close_client():
    global _client
    if _client:
        await _client.aclose()
        _client = None

async def _get_json(path: str, params: dict = None):
    """
    GET با retry ساده و exponential backoff برای خطاهای موقت شبکه/۵xx.
    """
    url = f"{BASE_URL}{path}"
    headers = {"Accept": "application/json"}
    if API_KEY:
        headers["Authorization"] = f"Bearer {API_KEY}"

    client = get_client()
    backoff = 1.0
    for attempt in range(MAX_RETRIES + 1):
        try:
            resp = await client.get(url, params=params, headers=headers)
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPStatusError as e:
            status = e.response.status_code
            # اگر خطای سرور بود (5xx) retry کن
            if 500 <= status < 600 and attempt < MAX_RETRIES:
                await asyncio.sleep(backoff)
                backoff *= 2
                continue
            raise
        except (httpx.ConnectError, httpx.ReadTimeout, httpx.NetworkError):
            if attempt < MAX_RETRIES:
                await asyncio.sleep(backoff)
                backoff *= 2
                continue
            raise

async def fetch_historical(symbol: str, start: Optional[str] = None, end: Optional[str] = None) -> pd.DataFrame:
    """
    فراخوانی endpoint تاریخی و تبدیل JSON به DataFrame استاندارد:
    خروجی: DataFrame با ستون‌های Date, Open, High, Low, Close, Volume
    توجه: ممکن است ساختار JSON API متفاوت باشد — اگر‌ متفاوت بود باید مپینگ را اصلاح کنی.
    """
    # مثال path: /historical یا /prices - این را بسته به API واقعی تنظیم کن
    path = "/historical"  # <-- اگر API تو مسیر دیگری دارد این را عوض کن
    params = {"symbol": symbol}
    if start: params["start"] = start
    if end: params["end"] = end

    data = await _get_json(path, params=params)

    # --- *** مهم: ساختار JSON را چاپ کن و بر اساس آن مپینگ بنویس ***
    # برای شروع فرض می‌کنیم API پاسخ مثل: {"data":[{"date":"YYYY-MM-DD","open":..,"high":..,...}, ...]}
    if isinstance(data, dict) and "data" in data:
        rows = data["data"]
    elif isinstance(data, list):
        rows = data
    else:
        # اگر ساختار متفاوت است، برگردون تا ببینی
        raise ValueError("Unexpected API response structure. inspect 'data' variable.")

    df = pd.DataFrame(rows)

    # سعی می‌کنیم نام ستون‌ها را استاندارد کنیم (ممکنه لازم باشه تغییر بدی)
    colmap = {}
    for c in df.columns:
        lc = c.lower()
        if "date" in lc: colmap[c] = "Date"
        elif lc in ("open", "o"): colmap[c] = "Open"
        elif lc in ("high", "h"): colmap[c] = "High"
        elif lc in ("low", "l"): colmap[c] = "Low"
        elif lc in ("close", "c", "price"): colmap[c] = "Close"
        elif "volume" in lc or lc == "v": colmap[c] = "Volume"

    df = df.rename(columns=colmap)

    # تبدیل تاریخ
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"])
    else:
        raise ValueError("API result has no date column after mapping. Check response.")

    # اگر بعضی ستون‌ها نبودند، ستونی با NaN بساز
    for col in ["Open", "High", "Low", "Close", "Volume"]:
        if col not in df.columns:
            df[col] = pd.NA

    # مرتب‌سازی و بازگرداندن
    df = df[["Date", "Open", "High", "Low", "Close", "Volume"]]
    df = df.sort_values("Date").reset_index(drop=True)
    return df
