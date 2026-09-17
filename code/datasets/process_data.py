import os
import pandas as pd
from sklearn.model_selection import train_test_split

RAW_DATA_PATH = "data/raw/winequality-red.csv"
TRAIN_DATA_PATH = "data/processed/train.csv"
TEST_DATA_PATH = "data/processed/test.csv"

def clean_and_split():
    df = pd.read_csv(RAW_DATA_PATH)
    
    # Удаление пропусков (если есть)
    df = df.dropna().drop_duplicates()
    
    # Фильтрация экстремальных выбросов по IQR для числовых признаков
    feature_cols = [c for c in df.columns if c != "quality"]
    for col in feature_cols:
        q25 = df[col].quantile(0.01)
        q75 = df[col].quantile(0.99)
        df = df[(df[col] >= q25) & (df[col] <= q75)]
        
    # Бинаризация таргета: 1 - хорошее вино (>= 6), 0 - обычное (< 6)
    df["target"] = (df["quality"] >= 6).astype(int)
    df = df.drop(columns=["quality"])
    
    # Разделение выборки со стратификацией
    train_df, test_df = train_test_split(df, test_size=0.2, random_state=42, stratify=df["target"])
    
    os.makedirs("data/processed", exist_ok=True)
    train_df.to_csv(TRAIN_DATA_PATH, index=False)
    test_df.to_csv(TEST_DATA_PATH, index=False)
    print("Stage 1 completed: data cleaned and split.")

if __name__ == "__main__":
    clean_and_split()