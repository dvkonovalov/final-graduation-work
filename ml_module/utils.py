import pandas as pd
import numpy as np

def prepare_data(features_path="output/processed_features.csv", historical_path="output/processed_historical_data.csv",
                 sequence_length=24, prediction_horizon=1):
    features_df = pd.read_csv(features_path)
    historical_df = pd.read_csv(historical_path)

    features_df['time_bucket'] = pd.to_datetime(features_df['time_bucket']).dt.tz_localize(None)
    historical_df['timestamp'] = pd.to_datetime(historical_df['timestamp']).dt.tz_localize(None)

    features_df = features_df.sort_values('time_bucket')
    historical_df = historical_df.sort_values('timestamp')

    merged_df = pd.merge_asof(
        features_df,
        historical_df,
        left_on='time_bucket',
        right_on='timestamp',
        direction='nearest'
    )

    merged_df = merged_df.sort_values('time_bucket')

    feature_cols = merged_df.columns.difference(['timestamp', 'time_bucket', 'open', 'high', 'low', 'close', 'volume_y'])
    target_col = 'close'

    X, y = [], []

    for i in range(len(merged_df) - sequence_length - prediction_horizon):
        X.append(merged_df[feature_cols].iloc[i:i+sequence_length].values)
        y.append(merged_df[target_col].iloc[i+sequence_length+prediction_horizon-1])

    return np.array(X), np.array(y)  # <-- ВАЖНО!!!
