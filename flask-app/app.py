from flask import Flask, request, jsonify
from redis import Redis
from pymongo import MongoClient
from kafka import KafkaProducer
import joblib
import os
import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.datasets import load_iris

app = Flask(__name__)

# Dependency hosts from environment or defaults for local Kubernetes
REDIS_HOST = os.environ.get('REDIS_HOST', 'redis')
MONGO_HOST = os.environ.get('MONGO_HOST', 'mongodb')
KAFKA_HOST = os.environ.get('KAFKA_HOST', 'kafka')

redis_client = Redis(host=REDIS_HOST, port=6379, db=0)
mongo_client = MongoClient(f'mongodb://{MONGO_HOST}:27017/')
producer = KafkaProducer(bootstrap_servers=[f'{KAFKA_HOST}:9092'])

db = mongo_client['mlops_db']
training_collection = db['training_data']
model_path = '/app/model.joblib'


def load_model():
    if os.path.exists(model_path):
        return joblib.load(model_path)
    return None


def save_model(model):
    joblib.dump(model, model_path)


@app.route('/health')
def health():
    return jsonify({'status': 'healthy'}), 200


@app.route('/train', methods=['POST'])
def train():
    data = training_collection.find({}, {'_id': 0}).limit(1000)
    df = pd.DataFrame(list(data))
    if df.empty:
        return jsonify({'error': 'no training data available'}), 400

    if 'target' not in df.columns:
        return jsonify({'error': 'training documents must include target field'}), 400

    X = df.drop(columns=['target'])
    y = df['target']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = LogisticRegression(max_iter=200)
    model.fit(X_train, y_train)
    save_model(model)

    score = model.score(X_test, y_test)
    redis_client.set('latest_model_score', score)
    redis_client.set('latest_model_version', 'v1')

    return jsonify({'message': 'model trained', 'score': float(score)}), 200


@app.route('/predict', methods=['POST'])
def predict():
    payload = request.json
    if not payload or 'features' not in payload:
        return jsonify({'error': 'missing features payload'}), 400

    model = load_model()
    if model is None:
        return jsonify({'error': 'no model found, train first'}), 404

    features = np.array(payload['features'])
    if features.ndim == 1:
        features = features.reshape(1, -1)

    prediction = model.predict(features).tolist()
    redis_client.set('last_prediction', str(prediction))
    return jsonify({'prediction': prediction}), 200


@app.route('/ingest', methods=['POST'])
def ingest():
    payload = request.json
    if not payload:
        return jsonify({'error': 'missing payload'}), 400

    training_collection.insert_one(payload)
    producer.send('ml-events', value=str(payload).encode('utf-8'))
    producer.flush()

    return jsonify({'message': 'event ingested'}), 200


@app.route('/status', methods=['GET'])
def status():
    model_score = redis_client.get('latest_model_score')
    model_version = redis_client.get('latest_model_version')
    last_prediction = redis_client.get('last_prediction')

    return jsonify({
        'model_version': model_version.decode() if model_version else None,
        'model_score': float(model_score) if model_score else None,
        'last_prediction': last_prediction.decode() if last_prediction else None
    }), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
