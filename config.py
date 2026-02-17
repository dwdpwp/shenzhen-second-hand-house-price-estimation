"""
System Configuration Layer
Centralizes paths, settings, logging, and basic business rules.
"""
from pathlib import Path
import logging
import sys

# ====================== 1. Path Configuration ======================
BASE_DIR = Path(__file__).parent
DATA_PATH = BASE_DIR / 'shenzhen_listings_cleaned.csv'
MODEL_PATH = BASE_DIR / 'shenzhen_house_model.pkl'
COLUMNS_PATH = BASE_DIR / 'model_columns.pkl'
LOG_FILE = BASE_DIR / 'app.log'

# ====================== 2. Business Logic (Arbitrage Anchors) ======================
# 2026年深圳各区新房限价参考 (Hard Anchor)
# 来源：结合住建局备案均价与市场调研
NEW_HOUSE_LIMITS = {
    '南山': 96000, '福田': 92000, '罗湖': 75000, '宝安': 68000,
    '龙华': 65000, '龙岗': 42000, '光明': 45000, '盐田': 50000,
    '坪山': 35000, '大鹏': 30000
}
# 套利阈值 (15% 价差)
ARBITRAGE_THRESHOLD = 0.15 

# ====================== 3. Robust Singleton Logging ======================
def _configure_logger():
    # Use a specific name to isolate from Streamlit's internal logs
    logger = logging.getLogger("shenzhen_housing")
    
    # Idempotency check: if handlers exist, return immediately to prevent duplicates
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Console Handler (Standard Output for Cloud Logs)
    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    
    # File Handler (Persistent Local Log)
    try:
        fh = logging.FileHandler(LOG_FILE, encoding='utf-8')
        fh.setFormatter(formatter)
        logger.addHandler(fh)
    except Exception:
        pass # Fallback for read-only cloud environments
    
    return logger

# Export the global logger instance
logger = _configure_logger()

# ====================== 4. UI Constants ======================
DISTRICT_COORDS = {
    '南山': {'lat': 22.5333, 'lon': 113.9303},
    '福田': {'lat': 22.5429, 'lon': 114.0596},
    '罗湖': {'lat': 22.5468, 'lon': 114.1312},
    '宝安': {'lat': 22.5533, 'lon': 113.8831},
    '龙岗': {'lat': 22.7207, 'lon': 114.2478},
    '盐田': {'lat': 22.5909, 'lon': 114.2450},
    '龙华': {'lat': 22.6549, 'lon': 114.0377},
    '坪山': {'lat': 22.6910, 'lon': 114.3463},
    '光明': {'lat': 22.7539, 'lon': 113.9272},
    '大鹏': {'lat': 22.5975, 'lon': 114.4735}
}
AREA_MIN = 10.0
AREA_MAX = 500.0
PAGE_TITLE = "Shenzhen AI Housing | 深圳房产智脑"