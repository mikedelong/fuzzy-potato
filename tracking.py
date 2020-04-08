from logging import INFO
from logging import basicConfig
from logging import getLogger
from time import time

import pandas as pd

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
    df = df.sort_values(by='date')
    logger.info('data types: {}'.format(df.dtypes))

    df = df[['date', 'positive']]
    df['positive_change'] = df['positive'].pct_change()
    df['rolling_positive_change'] = df['positive_change'].rolling(window=5, min_periods=5).mean()

    logger.info('total time: {:5.2f}s'.format(time() - time_start))
