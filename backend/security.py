from functools import wraps
from flask import request, jsonify

API_KEY = "12345abcde"

def authenticate_api(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('API-Key')
        if api_key != API_KEY:
            return jsonify({'error': 'Unauthorized access'}), 401
        return f(*args, **kwargs)
    return decorated_function

# Encryption (optional, e.g., for sensitive data)
from cryptography.fernet import Fernet

# Generate a key for encryption (run once)
def generate_key():
    key = Fernet.generate_key()
    with open('secret.key', 'wb') as key_file:
        key_file.write(key)

# Load the encryption key
def load_key():
    return open('secret.key', 'rb').read()

# Encrypt sensitive data
def encrypt_data(data):
    key = load_key()
    f = Fernet(key)
    return f.encrypt(data.encode())

# Decrypt sensitive data
def decrypt_data(encrypted_data):
    key = load_key()
    f = Fernet(key)
    return f.decrypt(encrypted_data).decode()
