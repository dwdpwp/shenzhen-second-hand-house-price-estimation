"""
Data Layer: Pure function implementation for optimal Streamlit caching.
"""
import pandas as pd
import streamlit as st
from config import DATA_PATH, DISTRICT_COORDS, logger

@st.cache_data(ttl=3600, show_spinner=False)
def load_data() -> pd.DataFrame:
    """
    Loads, cleans, and validates dataset.
    Returns: DataFrame (empty on failure).
    """
    if not DATA_PATH.exists():
        logger.critical(f"Dataset missing at: {DATA_PATH}")
        return pd.DataFrame()

    try:
        logger.info("Loading dataset into memory...")
        df = pd.read_csv(DATA_PATH)
        
        # --- Data Integrity Pipeline ---
        if df.empty:
            logger.warning("Loaded empty dataset.")
            return df

        # 1. Coordinate Filling (Fallback logic)
        if 'latitude' not in df.columns or 'longitude' not in df.columns:
            df['latitude'] = df['district'].map(lambda x: DISTRICT_COORDS.get(x, {}).get('lat', 22.54))
            df['longitude'] = df['district'].map(lambda x: DISTRICT_COORDS.get(x, {}).get('lon', 114.05))

        # 2. Total Price Calculation (Defense against missing columns)
        if 'total_price' not in df.columns:
            if 'unit_price' in df.columns and 'area_sqm' in df.columns:
                df['total_price'] = df['unit_price'] * df['area_sqm']
            else:
                df['total_price'] = 0.0
        
        return df

    except Exception as e:
        logger.exception("Data loading pipeline failed")
        return pd.DataFrame()
