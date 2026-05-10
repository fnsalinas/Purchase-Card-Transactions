import logging
import os
import pandas as pd
from sklearn.ensemble import IsolationForest
import joblib

logger = logging.getLogger(__name__)

def train_anomaly_detector(input_path='data/interim/prepared_consolidated_data.csv', model_output_path='models/anomaly_detector.pkl'):
    """
    Trains an Isolation Forest model to detect anomalous transactions.
    """
    logger.info(f"Training anomaly detection model using {input_path}")
    
    if not os.path.exists(input_path):
        logger.error(f"Input file {input_path} not found.")
        return

    df = pd.read_csv(input_path, sep='~')
    
    if 'original_gross_amt' not in df.columns:
        logger.error("Missing 'original_gross_amt' column, cannot train model.")
        return
    
    # Basic feature engineering for the model
    # We will use transaction amount as the primary feature for this baseline model
    features = df[['original_gross_amt']].fillna(0)
    
    # Initialize and train Isolation Forest
    # Contamination defines the expected proportion of outliers
    model = IsolationForest(n_estimators=100, contamination=0.01, random_state=42)
    model.fit(features)
    
    os.makedirs(os.path.dirname(model_output_path), exist_ok=True)
    joblib.dump(model, model_output_path)
    logger.info(f"Model trained and saved to {model_output_path}")

if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)
    train_anomaly_detector()
