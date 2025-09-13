import React, { useEffect, useState } from "react";

function Symbols() {
  const [symbols, setSymbols] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/api/symbols")
      .then((res) => res.json())
      .then((data) => {
        setSymbols(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error("خطا در گرفتن داده‌ها:", err);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return <div className="text-center mt-5">در حال بارگذاری...</div>;
  }

  return (
    <div className="container mt-4">
      <h2 className="mb-3">📊 لیست نمادها</h2>
      <table className="table table-striped table-bordered">
        <thead className="table-dark">
          <tr>
            <th>نماد</th>
            <th>نام</th>
            <th>قیمت پایانی</th>
            <th>تغییر</th>
            <th>درصد تغییر</th>
          </tr>
        </thead>
        <tbody>
          {symbols.map((item, index) => (
            <tr key={index}>
              <td>{item.symbol}</td>
              <td>{item.name}</td>
              <td>{item.price}</td>
              <td>{item.change}</td>
              <td>{item.percent}%</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default Symbols;
