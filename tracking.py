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
    logger.debug('data shape: {}'.format(df.shape))
    logger.debug('data types: {}'.format(df.dtypes))

    colors = ['dimgray', 'gray', 'darkgray', 'silver', 'lightgray']
    # todo compute the forecast weight to be a best fit
    forecast_weight = 0.8
    # todo introduce plotly as an alternative to matplotlib
    for target in ['positive', 'death']:
        once = True
        logger.info('forecasting {}'.format(target))
        target_df = df[['date', target]].copy(deep=True).sort_values(by='date')
        target_df['change'] = target_df[target].pct_change()
        fig, ax = plt.subplots(figsize=(15, 10))
        # todo think about plotting y and log y in subplots
        ax.set_yscale('log')

        for window in range(1, 9):
            target_df['rolling_change'] = target_df['change'].rolling(window=window, min_periods=window, ).mean()
            # row = target_df.tail(1).squeeze()
            for index, row in target_df[window:].iterrows():
                forecast_format = 'date: {}  {}d rm forecast {:.0f} change {:.0f}'
                forecast_date = (row['date'] + timedelta(days=1, )).date()
                forecast = row[target] * (1.0 + forecast_weight * row['rolling_change'])
                forecast_change = forecast - row[target]
                logger.info(forecast_format.format(forecast_date, window, forecast, forecast_change))
                for project in range(5):
                    if once:
                        ax.scatter([forecast_date], [forecast], c='orange', label='forecast', marker='x', )
                        once = False
                    else:
                        ax.scatter([forecast_date], [forecast],  c=colors[project], marker='x', )
                    forecast_date += timedelta(days=1, )
                    forecast *= (1.0 + forecast_weight * row['rolling_change'])

        ax.scatter(target_df['date'], target_df[target], label=target, c='blue', )
        ax.legend()
        out_file = './' + target + '.png'
        plt.savefig(out_file)
    logger.info('total time: {:5.2f}s'.format(time() - time_start))
