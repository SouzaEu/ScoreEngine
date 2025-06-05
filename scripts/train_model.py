import joblib
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from pathlib import Path

OUTPUT_PATH = Path('model/xgboost_model.pkl')


def main():
    X, y = make_classification(
        n_samples=1000,
        n_features=4,
        n_informative=3,
        n_redundant=0,
        random_state=42,
    )
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    pipeline = Pipeline([
        ('scaler', StandardScaler()),
        ('clf', LogisticRegression())
    ])
    pipeline.fit(X_train, y_train)
    OUTPUT_PATH.parent.mkdir(exist_ok=True)
    joblib.dump(pipeline, OUTPUT_PATH)
    print(f'Model saved to {OUTPUT_PATH}')


if __name__ == '__main__':
    main()
