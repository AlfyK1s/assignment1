import os
import joblib
import mlflow
import mlflow.sklearn
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

TRAIN_DATA_PATH = "data/processed/train.csv"
TEST_DATA_PATH = "data/processed/test.csv"
MODEL_PATH = "models/model.pkl"

def train():
    train_df = pd.read_csv(TRAIN_DATA_PATH)
    test_df = pd.read_csv(TEST_DATA_PATH)
    
    X_train, y_train = train_df.drop(columns=["target"]), train_df["target"]
    X_test, y_test = test_df.drop(columns=["target"]), test_df["target"]
    
    mlflow.set_experiment("Wine_Quality_Classification")
    
    with mlflow.start_run():
        c_param = 1.0
        max_iter = 500
        
        pipeline = Pipeline([
            ("scaler", StandardScaler()),
            ("classifier", LogisticRegression(C=c_param, max_iter=max_iter, random_state=42))
        ])
        
        pipeline.fit(X_train, y_train)
        preds = pipeline.predict(X_test)
        probs = pipeline.predict_proba(X_test)[:, 1]
        
        acc = accuracy_score(y_test, preds)
        f1 = f1_score(y_test, preds)
        auc = roc_auc_score(y_test, probs)
        
        # Логирование в MLflow
        mlflow.log_params({"C": c_param, "max_iter": max_iter, "solver": "lbfgs"})
        mlflow.log_metrics({"accuracy": acc, "f1_score": f1, "roc_auc": auc})
        mlflow.sklearn.log_model(pipeline, artifact_path="model")
        
        os.makedirs("models", exist_ok=True)
        joblib.dump(pipeline, MODEL_PATH)
        print(f"Stage 2 completed: Model saved to {MODEL_PATH}. Test AUC: {auc:.4f}")

if __name__ == "__main__":
    train()