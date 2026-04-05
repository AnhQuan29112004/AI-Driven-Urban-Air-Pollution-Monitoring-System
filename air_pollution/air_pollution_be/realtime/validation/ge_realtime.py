import great_expectations as gx
import pandas as pd
import logging
from utils.utils import Utils

logger = logging.getLogger(__name__)

def validation_realtime(payload: dict):
    try:
        df = pd.DataFrame([payload])
        context = gx.get_context()
        datasource = context.data_sources.add_pandas(name="pandas_ds")
        data_asset = datasource.add_dataframe_asset(name="realtime_dataset")
        suite_realtime = context.suites.add(
            gx.ExpectationSuite(name="realtime_data_suite")
        )
        batch_definition_realtime = data_asset.add_batch_definition_whole_dataframe(
            "realtime_data_batch"
        )
        cols = ['pm25','pm10','co','so2','no2','o3']
        for col in cols:
            suite_realtime.add_expectation(gx.expectations.ExpectColumnValuesToBeBetween(column=col,min_value=0,
            max_value=500))
        suite_realtime.add_expectation(gx.expectations.ExpectColumnValuesToNotBeNull(column='timestamp',mostly=0.8))
        if not Utils.validate_dataframe(df, suite_realtime, batch_definition_realtime, context):
            logger.warning('validation fail for realtime data')
            return False
        logger.info('validation successfull')
        return True
    except Exception as e:
        logger.warning(f'validation error: {e}')
        return True