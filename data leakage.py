import os
import hashlib
import json
import boto3  # AWS SDK for Python
from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
from sklearn.ensemble import IsolationForest
import pandas as pd

# Initialize Flask App
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# AWS S3 Configuration
s3 = boto3.client('s3', aws_access_key_id='YOUR_ACCESS_KEY', aws_secret_access_key='YOUR_SECRET_KEY')
BUCKET_NAME = "your-bucket-name"

# Function to generate file hash
def generate_hash(file_path):
    hasher = hashlib.sha256()
    with open(file_path, 'rb') as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()

# Upload File API
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    file = request.files['file']
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)
    
    # Compute Hash
    file_hash = generate_hash(file_path)
    
    # Upload to S3
    s3.upload_file(file_path, BUCKET_NAME, filename)
    
    return jsonify({'message': 'File uploaded successfully', 'hash': file_hash})

# Fetch Access Logs (Mocked for simplicity)
def get_access_logs():
    return pd.DataFrame({
        'user_id': [1, 2, 3, 4, 5, 6],
        'access_count': [5, 20, 10, 50, 2, 200],
        'download_flag': [0, 1, 0, 1, 0, 1]
    })

# Anomaly Detection API
@app.route('/detect', methods=['GET'])
def detect_leakage():
    logs = get_access_logs()
    model = IsolationForest(contamination=0.1)
    logs['anomaly'] = model.fit_predict(logs[['access_count', 'download_flag']])
    anomalies = logs[logs['anomaly'] == -1]
    return anomalies.to_json()

# Home Route with Interface
@app.route('/')
def home():
    return render_template('index.html')

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
