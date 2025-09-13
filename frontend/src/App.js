import React, { useState, useEffect } from "react";
import PredictionForm from "./components/PredictionForm";
import PredictResult from "./components/PredictResult";

export default function App() {
  const [symbols, setSymbols] = useState([]);
  const [predictions, setPredictions] = useState(null); // اینجا کل response ذخیره میشه

  useEffect(() => {
    fetch("http://127.0.0.1:8000/api/symbols")
      .then(res => res.json())
      .then(data => {
        const formatted = data.map(s => ({
          symbol: s.symbol,
          name: s.name
        }));
        setSymbols(formatted);
      })
      .catch(err => console.error("خطا در گرفتن نمادها:", err));
  }, []);

  const handleSubmit = ({ symbol, days, algorithm }) => {
    fetch("http://127.0.0.1:8000/api/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ symbol, days, algorithm })
    })
      .then(res => res.json())
      .then(data => {
      console.log("Response from /predict:", data); // باید اینو بررسی کنی
      setPredictions({ symbol: data.symbol, predictions: data.predictions });
    })

      .catch(err => console.error("خطا در پیش‌بینی:", err));
  };

  return (
    <div className="container mt-5 bg-dark text-light min-vh-100">
      <h2 className="mb-4">پیش‌بینی بورس ایران</h2>

      {!predictions && (
        <PredictionForm symbols={symbols} onSubmit={handleSubmit} />
      )}

      {predictions && predictions.predictions && (
      <PredictResult
        symbol={predictions.symbol}
        data={predictions} // حالا data همان {symbol, predictions: [...]}
        onBack={() => setPredictions(null)}
      />
    )}

          
    </div>
  );
}
