from logging import INFO
from logging import basicConfig
from logging import getLogger
from time import time

import pandas as pd
from datetime import timedelta

if __name__ == '__main__':
    time_start = time()
    logger = getLogger(__name__)
    basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=INFO)
    logger.info('started.')

    url = 'https://covidtracking.com/api/us/daily.csv'
    logger.info('reading from {}'.format(url))
    df = pd.read_csv(url)
    date_format = '%Y%m%d'
    df.date = pd.to_datetime(df.date.astype(int), format=date_format, )
    logger.info('data shape: {}'.format(df.shape))
    logger.info('data types: {}'.format(df.dtypes))

    for window in range(1, 9):
        positive_df = df[['date', 'positive']].copy(deep=True).sort_values(by='date')
        positive_df['positive_change'] = positive_df['positive'].pct_change()
        positive_df['rolling_positive_change'] = positive_df['positive_change'].rolling(window=window,
                                                                                        min_periods=window, ).mean()
        row = positive_df.tail(1).squeeze()
        forecast_format = 'date: {}  {}d rm forecast {:.0f}'
        logger.info(forecast_format.format((row['date'] + timedelta(days=1, )).date(), window,
                                           row['positive'] * (1.0 + row['rolling_positive_change'])))

    logger.info('total time: {:5.2f}s'.format(time() - time_start))
