import pandas as pd
import numpy as np
import xgboost as xgb
import pyarrow.parquet as pq
import os
import json

def load_data():
    print("Loading data...")
    pf = pq.ParquetFile('data/bought_deployers_activity.parquet')
    cols = ['wallet', 'timestamp', 'event_type', 'token_address']
    df_list = []
    for i in range(pf.num_row_groups):
        df_list.append(pf.read_row_group(i, columns=cols).to_pandas())
    deployer_activity = pd.concat(df_list, ignore_index=True)
    
    bought_deploys = pd.read_parquet('data/bought_deploy_txs_index.parquet')
    bought_tokens = set(bought_deploys['token_address'])
    
    return deployer_activity, bought_tokens

def engineer_features(deployer_activity, bought_tokens):
    print("Engineering deep features...")
    launches = deployer_activity[deployer_activity['event_type'] == 'launch'].copy()
    launches['is_bought'] = launches['token_address'].apply(lambda x: 1 if x in bought_tokens else 0)
    launches = launches.sort_values(['wallet', 'timestamp'])
    
    # 1. Historical Creator Profiling
    launches['cum_launches'] = launches.groupby('wallet').cumcount()
    launches['cum_wins'] = launches.groupby('wallet')['is_bought'].cumsum() - launches['is_bought']
    launches['historical_win_rate'] = np.where(
        launches['cum_launches'] > 0,
        launches['cum_wins'] / launches['cum_launches'],
        0.0
    )
    
    # 2. Temporal Launch Velocity
    launches['prev_timestamp'] = launches.groupby('wallet')['timestamp'].shift(1)
    launches['time_since_last_launch'] = (launches['timestamp'] - launches['prev_timestamp']).fillna(-1)
    
    return launches

def train_replica_model(launches):
    print("Training replica model...")
    feature_cols = ['cum_launches', 'cum_wins', 'historical_win_rate', 'time_since_last_launch']
    X = launches[feature_cols]
    y = launches['is_bought']
    
    model = xgb.XGBClassifier(
        n_estimators=150,
        max_depth=5,
        learning_rate=0.05,
        scale_pos_weight=len(y[y==0])/len(y[y==1]),
        random_state=42
    )
    model.fit(X, y)
    return model, feature_cols

if __name__ == "__main__":
    activity, bought_tokens = load_data()
    df = engineer_features(activity, bought_tokens)
    model, features = train_replica_model(df)
    
    # Save model
    model.save_model('sniper_replica_v2.json')
    print("Replica strategy training complete. Model saved as sniper_replica_v2.json")
    
    # Display Feature Importance
    importances = model.feature_importances_
    for f, imp in zip(features, importances):
        print(f"Feature: {f}, Importance: {imp:.4f}")
