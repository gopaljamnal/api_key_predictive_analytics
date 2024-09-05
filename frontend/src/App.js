import React, { useState } from 'react';
import './App.css';

function App() {
  const [date, setDate] = useState('');
  const [prediction, setPrediction] = useState('');
  const [error, setError] = useState('');

  const handlePrediction = async () => {
    try {
      const response = await fetch('http://127.0.0.1:5000/predict', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'API-Key': '12345abcde',
        },
        body: JSON.stringify({ date }),
      });

      const data = await response.json();

      if (response.ok) {
        setPrediction(`Predicted Price: ${data.prediction}`);
        setError('');
      } else {
        setError(`Error: ${data.error}`);
        setPrediction('');
      }
    } catch (err) {
      setError('Failed to fetch prediction');
      setPrediction('');
    }
  };

  return (
    <div className="App">
      <h1>Predict Stock Price</h1>
      <input
        type="text"
        value={date}
        onChange={(e) => setDate(e.target.value)}
        placeholder="Enter a date (YYYYMMDD)"
      />
      <button onClick={handlePrediction}>Predict</button>
      <p>{prediction}</p>
      <p className="error">{error}</p>
    </div>
  );
}

export default App;
