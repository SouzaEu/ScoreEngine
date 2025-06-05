# Lynex Score Engine

This project provides a FastAPI application that exposes a predictive score
endpoint backed by a scikit-learn model.

## Training a demo model

The repository does not ship with a trained model. A helper script is included
to train a small logistic regression model that produces
`model/xgboost_model.pkl` used by the API. Run this script before starting the
application or executing the tests.

```bash
pip install -r requirements.txt
python scripts/train_model.py
```

## Running the API

Start the application with Uvicorn:

```bash
uvicorn app.main:app --reload
```

The interactive documentation is available at `http://localhost:8000/docs`.

## Running tests

Install dependencies and run pytest:

```bash
pip install -r requirements.txt
pytest
```

## Docker

A basic Dockerfile is provided. Build and run the image:

```bash
docker build -t lynex-score-engine .
docker run -p 8000:8000 lynex-score-engine
```
