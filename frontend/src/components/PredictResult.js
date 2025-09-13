// src/components/PredictResult.js
import React from "react";

export default function PredictResult({ data, onBack }) {
  if (!data || !data.predictions || data.predictions.length === 0) {
    return <p>نتیجه‌ای برای نمایش وجود ندارد.</p>;
  }

  const { symbol, predictions } = data;

  // تحلیل ساده: اگر آخرین قیمت > اولین قیمت روند صعودیه
  const first = predictions[0];
  const last = predictions[predictions.length - 1];
  const trend = last > first ? "صعودی" : last < first ? "نزولی" : "ثابت";
  const recommendation = trend === "صعودی" ? "می‌تواند مناسب خرید باشد" : "خرید توصیه نمی‌شود";

  return (
    <div className="mt-4">
      <h3>پیش‌بینی ۱۰ روز آینده برای {symbol}:</h3>
      
      <ul className="list-group mt-3">
        {predictions.map((p, idx) => (
          <li key={idx} className="list-group-item bg-dark text-light">
            روز {idx + 1}: {p}
          </li>
        ))}
      </ul>

      <div className="mt-3 p-3 border border-light rounded">
        <p>روند پیش‌بینی: <strong>{trend}</strong></p>
        <p>پیشنهاد: <strong>{recommendation}</strong></p>
      </div>

      <button className="btn btn-secondary mt-3" onClick={onBack}>
        بازگشت
      </button>
    </div>
  );
}
