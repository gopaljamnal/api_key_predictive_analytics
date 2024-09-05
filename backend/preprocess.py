import pandas as pd


def preprocess_data(file_path):
    data = pd.read_csv(file_path)

    # Example of data cleaning: fill missing values
    data['Price'] = data['Price'].ffill()
    # Convert 'Date' column to datetime, assuming day comes first (format fix)
    data['Date'] = pd.to_datetime(data['Date'], dayfirst=True)

    # Convert Date column to an integer
    data['Date'] = pd.to_datetime(data['Date']).dt.strftime('%Y%m%d').astype(int)

    return data


# Preprocess and save cleaned data
if __name__ == "__main__":
    processed_data = preprocess_data('data/stock_data.csv')
    processed_data.to_csv('data/stock_data_cleaned.csv', index=False)
