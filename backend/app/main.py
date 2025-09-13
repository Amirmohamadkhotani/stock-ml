from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import symbols, prices, predict

app = FastAPI()

# فعال کردن CORS برای فرانت
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # فرانت
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(symbols.router, prefix="/api")
app.include_router(prices.router, prefix="/api")
app.include_router(predict.router, prefix="/api")