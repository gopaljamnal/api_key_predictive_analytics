from flask import Flask, request, jsonify
from model import predict_stock_price
from security import authenticate_api
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend access

# Route for stock price prediction
@app.route('/predict', methods=['POST'])
@authenticate_api  # API authentication decorator
def predict():
    data = request.json
    if 'date' not in data:
        return jsonify({'error': 'Date field is missing'}), 400

    # Use the model to predict stock price
    prediction = predict_stock_price(data['date'])
    if prediction is None:
        return jsonify({'error': 'Prediction failed'}), 500

    return jsonify({'prediction': prediction})

if __name__ == "__main__":
    app.run(debug=True)
