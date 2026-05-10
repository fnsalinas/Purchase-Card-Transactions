import logging
import os
import pandas as pd
import joblib

logger = logging.getLogger(__name__)

def predict_anomalies(input_path='data/interim/prepared_consolidated_data.csv', model_path='models/anomaly_detector.pkl', output_path='data/processed/anomalies.csv'):
    """
    Loads the trained Isolation Forest model and predicts anomalies on the dataset.
    """
    logger.info(f"Predicting anomalies for {input_path}")
    
    if not os.path.exists(input_path):
        logger.error(f"Input file {input_path} not found.")
        return
        
    if not os.path.exists(model_path):
        logger.error(f"Model file {model_path} not found. Train the model first.")
        return

    df = pd.read_csv(input_path, sep='~')
    
    if 'original_gross_amt' not in df.columns:
        logger.error("Missing 'original_gross_amt' column, cannot run prediction.")
        return
        
    model = joblib.load(model_path)
    features = df[['original_gross_amt']].fillna(0)
    
    # Predict anomalies: -1 is anomalous, 1 is normal
    df['is_anomaly'] = model.predict(features)
    
    # Filter only anomalies
    anomalies = df[df['is_anomaly'] == -1].copy()
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    anomalies.to_csv(output_path, sep='~', index=False)
    logger.info(f"Saved {len(anomalies)} anomalies to {output_path}")
    
if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)
    predict_anomalies()
