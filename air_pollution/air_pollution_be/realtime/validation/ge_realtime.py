import great_expectations as gx
import pandas as pd
import logging
from utils.utils import Utils

import threading

logger = logging.getLogger(__name__)

class GERealtimeSingleton:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(GERealtimeSingleton, cls).__new__(cls)
                cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        logger.info("Initializing Great Expectations context and suite as Singleton...")
        self.context = gx.get_context()
        datasource = self.context.data_sources.add_pandas(name="pandas_ds")
        data_asset = datasource.add_dataframe_asset(name="realtime_dataset")
        self.suite = self.context.suites.add(
            gx.ExpectationSuite(name="realtime_data_suite")
        )
        self.batch_definition = data_asset.add_batch_definition_whole_dataframe(
            "realtime_data_batch"
        )
        cols = ['pm25','pm10','co','so2','no2','o3']
        for col in cols:
            self.suite.add_expectation(gx.expectations.ExpectColumnValuesToBeBetween(column=col, min_value=0, max_value=500))
        self.suite.add_expectation(gx.expectations.ExpectColumnValuesToNotBeNull(column='timestamp', mostly=0.8))
        logger.info("GE Suite Singleton initialized successfully")

def validation_realtime(payload: dict):
    try:
        df = pd.DataFrame([payload])
        ge_instance = GERealtimeSingleton()
        
        if not Utils.validate_dataframe(df, ge_instance.suite, ge_instance.batch_definition, ge_instance.context):
            logger.warning('validation fail for realtime data')
            return False
        logger.info('validation successfull')
        return True
    except Exception as e:
        logger.warning(f'validation error: {e}')
        return False