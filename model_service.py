"""
Service Layer: Handles model inference.
"""
import joblib
import pandas as pd
import streamlit as st
from typing import Dict, Any, Tuple
from config import MODEL_PATH, COLUMNS_PATH, logger

class ModelService:
    def __init__(self):
        self.model = None
        self.model_columns = None
        self._load_resources()

    def _load_resources(self) -> None:
        try:
            if not MODEL_PATH.exists() or not COLUMNS_PATH.exists():
                logger.warning("Model artifacts missing.")
                return
            self.model = joblib.load(MODEL_PATH)
            self.model_columns = joblib.load(COLUMNS_PATH)
            logger.info("Model loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")

    def predict(self, features: Dict[str, Any]) -> Tuple[float, float]:
        """
        Returns: (Total Price, Unit Price)
        """
        if not self.model:
            return 0.0, 0.0

        try:
            df_input = pd.DataFrame([features])
            df_encoded = pd.get_dummies(df_input)
            # Reindex ensures we handle 'floor'/'year' gracefully even if model ignores them
            df_encoded = df_encoded.reindex(columns=self.model_columns, fill_value=0)
            
            pred_total = self.model.predict(df_encoded)[0]
            area = features.get('area_sqm', 1.0)
            pred_unit = pred_total / area if area > 0 else 0.0
            
            logger.info(f"Prediction success: {pred_total:.2f}")
            return pred_total, pred_unit

        except Exception as e:
            logger.exception("Prediction logic failed")
            return 0.0, 0.0
