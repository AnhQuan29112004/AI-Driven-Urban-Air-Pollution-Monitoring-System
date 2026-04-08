import pandas as pd
import logging
from statsmodels.tsa.stattools import adfuller, kpss

logger = logging.getLogger(__name__)

def validate_data_quality(df: pd.DataFrame, target_col: str = "pm25"):
    """Kiểm tra missing, duplicate, outlier, stationarity (ADF/KPSS)"""
    # Missing & duplicate
    missing_pct = df[target_col].isna().mean() * 100
    dup_ts = df.index.duplicated().sum()
    
    logger.info(f"Missing {target_col}: {missing_pct:.2f}% | Duplicate timestamps: {dup_ts}")
    
    # Outlier (IQR)
    Q1 = df[target_col].quantile(0.25)
    Q3 = df[target_col].quantile(0.75)
    IQR = Q3 - Q1
    outliers = ((df[target_col] < (Q1 - 1.5 * IQR)) | (df[target_col] > (Q3 + 1.5 * IQR))).sum()
    logger.info(f"Outliers: {outliers}")
    
    # Stationarity
    try:
        adf = adfuller(df[target_col].dropna())
        kpss_stat = kpss(df[target_col].dropna(), regression='c')
        logger.info(f"ADF p-value: {adf[1]:.4f} | KPSS p-value: {kpss_stat[1]:.4f}")
        if adf[1] < 0.05:
            logger.info("Stationary (ADF)")
        else:
            logger.warning("⚠️ Non-stationary → cần differencing sau")
    except Exception as e:
        logger.error(f"Stationarity test error: {e}")