import pandas as pd
from lightgbm import LGBMClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import precision_score
import joblib
from datetime import datetime

df = pd.read_json("data/sample_logs.json")
df_chain = pd.read_csv("data/blockchain_txs.csv")
df = df.merge(df_chain, left_on="tx_hash", right_on="hash", how="left")
df["gap_sec"] = (pd.to_datetime(df["timestamp"]) - pd.to_datetime(df["block_time"])).dt.total_seconds().abs()
df["label"] = (df["gap_sec"] > 300) | df["known_attack"]

X = df[["gap_sec", "login_attempts", "privilege_escalation", "wallet_balance_change"]].fillna(0)
y = df["label"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model = LGBMClassifier(n_estimators=200, learning_rate=0.05)
model.fit(X_train, y_train)

preds = model.predict(X_test)
precision = precision_score(y_test, preds)
print(f"Precision: {precision:.3%}")

joblib.dump(model, "model/anomaly_detector.pkl")
with open("audit.log", "w") as f:
    f.write(f"Precision: {precision:.3%}\nTrained: {datetime.now()}\n")
