#!/usr/bin/env python
import pandas as pd
import joblib
import json
from datetime import datetime
import argparse
from generate_report import export_pdf

model = joblib.load("model/anomaly_detector.pkl")

def load_logs(org):
    logs = json.load(open("data/sample_logs.json"))
    df = pd.DataFrame(logs)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["org"] = org
    return df

def load_blockchain():
    return pd.read_csv("data/blockchain_txs.csv", parse_dates=["block_time"])

def cross_check(df_logs, df_chain):
    merged = df_logs.merge(df_chain, left_on="tx_hash", right_on="hash", how="left")
    merged["gap_sec"] = (merged["timestamp"] - merged["block_time"]).dt.total_seconds().abs()
    merged["anomaly"] = (merged["gap_sec"] > 300) | merged["privilege_escalation"]
    return merged

def predict(df):
    features = df[["gap_sec", "login_attempts", "privilege_escalation", "wallet_balance_change"]].fillna(0)
    df["risk_score"] = model.predict_proba(features)[:, 1]
    df["flag"] = df["risk_score"] > 0.67
    return df

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--org", default="demo")
    args = parser.parse_args()

    logs = load_logs(args.org)
    chain = load_blockchain()
    df = cross_check(logs, chain)
    df = predict(df)

    flagged = df[df["flag"]]
    print(f"{len(flagged)} anomalies flagged")

    df.to_csv("data/latest_audit.csv", index=False)
    export_pdf(flagged, args.org)
