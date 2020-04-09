from datetime import timedelta
from logging import INFO
from logging import basicConfig
from logging import getLogger
from time import time

import matplotlib.pyplot as plt
import pandas as pd
from pandas.plotting import register_matplotlib_converters

if __name__ == '__main__':
    time_start = time()
    logger = getLogger(__name__)
    basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=INFO)
    logger.info('started.')
    register_matplotlib_converters()

    url = 'https://covidtracking.com/api/us/daily.csv'
    logger.info('reading from {}'.format(url))
    df = pd.read_csv(url)
    date_format = '%Y%m%d'
    df.date = pd.to_datetime(df.date.astype(int), format=date_format, )
    logger.info('data shape: {}'.format(df.shape))
    logger.info('data types: {}'.format(df.dtypes))

    for target in ['positive', 'death']:
        logger.info('forecasting {}'.format(target))
        target_df = df[['date', target]].copy(deep=True).sort_values(by='date')
        fig, ax = plt.subplots(figsize=(15, 10))
        ax.scatter(target_df['date'], target_df[target], label=target, )

        for window in range(1, 9):
            target_df['change'] = target_df[target].pct_change()
            target_df['rolling_change'] = target_df['change'].rolling(window=window, min_periods=window, ).mean()
            row = target_df.tail(1).squeeze()
            forecast_format = 'date: {}  {}d rm forecast {:.0f} change {:.0f}'
            forecast_date = (row['date'] + timedelta(days=1, )).date()
            forecast = row[target] * (1.0 + row['rolling_change'])
            forecast_change = forecast - row[target]
            logger.info(forecast_format.format(forecast_date, window, forecast, forecast_change))
            ax.scatter([forecast_date], [forecast], )

        out_file = './' + target + '.png'
        plt.savefig(out_file)
    logger.info('total time: {:5.2f}s'.format(time() - time_start))
