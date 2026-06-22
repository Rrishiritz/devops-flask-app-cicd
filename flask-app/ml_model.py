import os
import joblib
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from pymongo import MongoClient

MONGO_HOST = os.environ.get('MONGO_HOST', 'mongodb')
model_path = '/app/model.joblib'


def get_training_data():
    client = MongoClient(f'mongodb://{MONGO_HOST}:27017/')
    db = client['mlops_db']
    collection = db['training_data']
    data = list(collection.find({}, {'_id': 0}))
    return pd.DataFrame(data)


def train_model():
    df = get_training_data()
    if df.empty or 'target' not in df.columns:
        raise ValueError('training data missing or no target field')

    X = df.drop(columns=['target'])
    y = df['target']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = LogisticRegression(max_iter=200)
    model.fit(X_train, y_train)
    score = model.score(X_test, y_test)
    joblib.dump(model, model_path)
    return model, score


def load_model():
    if os.path.exists(model_path):
        return joblib.load(model_path)
    return None
