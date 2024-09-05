import pandas as pd
from sklearn.linear_model import LinearRegression
import joblib

from preprocess import preprocess_data

# Load the dataset
data = pd.read_csv('data/stock_data_cleaned.csv')

print(data)


# Train a simple Linear Regression model
def train_model():
    X = data[['Date']].values.reshape(-1, 1)  # Features
    y = data['Price'].values  # Target

    model = LinearRegression()
    model.fit(X, y)

    # Save the model
    joblib.dump(model, 'models/stock_model.pkl')

# Load the pretrained model
def load_model():
    return joblib.load('models/stock_model.pkl')

# Predict the stock price for a given date
def predict_stock_price(date):
    model = load_model()
    X_new = [[int(date)]]
    return model.predict(X_new)[0]

# Train the model (can be triggered when required)
if __name__ == "__main__":
    train_model()
