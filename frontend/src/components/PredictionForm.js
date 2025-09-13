import React, { useState } from "react";
import { Typeahead } from 'react-bootstrap-typeahead';
import 'react-bootstrap-typeahead/css/Typeahead.css';
import 'bootstrap/dist/css/bootstrap.min.css';

export default function PredictionForm({ symbols, onSubmit }) {
  const [selectedSymbol, setSelectedSymbol] = useState([]);
  const [days, setDays] = useState(30);
  const [algorithm, setAlgorithm] = useState("SVM");

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!selectedSymbol.length) {
      alert("لطفاً یک نماد انتخاب کنید");
      return;
    }
    onSubmit({ symbol: selectedSymbol[0].symbol, days, algorithm });
  };

  return (
    <form onSubmit={handleSubmit} className="text-light">
      {/* نماد بورس */}
      <div className="mb-3">
        <label className="form-label">نماد بورس</label>
        <Typeahead
          id="symbol-typeahead"
          labelKey="name"
          options={symbols}
          placeholder="نماد را انتخاب کنید..."
          selected={selectedSymbol}
          onChange={setSelectedSymbol}
          maxResults={1000}
          minLength={0}
          renderMenuItemChildren={(option) => (
            <div>{option.name} ({option.symbol})</div>
          )}
          className="bg-dark text-light"
        />
      </div>

      {/* تعداد روز گذشته */}
      <div className="mb-3">
        <label className="form-label">تعداد روز گذشته</label>
        <select
          className="form-select bg-dark text-light"
          value={days}
          onChange={(e) => setDays(Number(e.target.value))}
        >
          <option value={15}>15 روز گذشته</option>
          <option value={30}>1 ماه گذشته</option>
          <option value={60}>2 ماه گذشته</option>
        </select>
      </div>

      {/* الگوریتم پیش‌بینی */}
      <div className="mb-3">
        <label className="form-label">الگوریتم پیش‌بینی</label>
        <select
          className="form-select bg-dark text-light"
          value={algorithm}
          onChange={(e) => setAlgorithm(e.target.value)}
        >
          <option value="SVM">SVM</option>
          <option value="RandomForest">RandomForest</option>
          <option value="Prophet">Prophet</option>
        </select>
      </div>

      <button type="submit" className="btn btn-primary">
        پیش‌بینی
      </button>
    </form>
  );
}
