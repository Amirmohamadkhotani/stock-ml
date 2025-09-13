from fastapi import APIRouter, HTTPException
import requests

router = APIRouter()

@router.get("/symbols")
def get_symbols():
    url = "https://brsapi.ir/Api/Tsetmc/AllSymbols.php?key=BWNWXVP88fAfWuN3isA8m91eY42XJ818"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json, text/plain, */*"
    }
    try:
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()
        data = response.json()

        # فقط چند فیلد مهم رو نگه می‌داریم
        simplified = [
            {
                "symbol": item["l18"],   # نماد
                "name": item["l30"],     # نام کامل
                "price": item["pc"],     # قیمت پایانی
                "change": item["pcc"],   # تغییر قیمت
                "percent": item["pcp"]   # درصد تغییر
            }
            for item in data
        ]
        return simplified

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ارتباط برقرار نشد: {e}")
