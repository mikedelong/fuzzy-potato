from datetime import timedelta
from logging import INFO
from logging import basicConfig
from logging import getLogger
from time import time

import matplotlib.pyplot as plt
import pandas as pd
from pandas.plotting import register_matplotlib_converters
from plotly.graph_objects import Figure
from plotly.graph_objects import Scatter
from plotly.offline import plot
from plotly.subplots import make_subplots

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
    plot_methods = ['matplotlib', 'plotly']
    plot_method = plot_methods[1]
    colors = ['dimgray', 'gray', 'darkgray', 'silver', 'lightgray']
    # todo compute the forecast weight to be a best fit
    forecast_weight = 0.8
    for target in ['positive', 'death']:
        once = True
        logger.info('forecasting {}'.format(target))
        target_df = df[['date', target]].copy(deep=True).sort_values(by='date')
        target_df['change'] = target_df[target].pct_change()
        if plot_method == plot_methods[0]:
            figure, ax = plt.subplots(figsize=(15, 10))
            # todo think about plotting y and log y in subplots
            ax.set_yscale('log')
        else:
            figure = make_subplots(cols=2, rows=1)
            ax = None

        for window in range(1, 9):
            target_df['rolling_change'] = target_df['change'].rolling(window=window, min_periods=window, ).mean()
            for index, row in target_df[window:].iterrows():
                forecast_format = 'date: {}  {}d rm forecast {:.0f} change {:.0f}'
                forecast_date = (row['date'] + timedelta(days=1, )).date()
                forecast = row[target] * (1.0 + forecast_weight * row['rolling_change'])
                forecast_change = forecast - row[target]
                logger.info(forecast_format.format(forecast_date, window, forecast, forecast_change))
                for project in range(5):
                    if once:
                        once = False
                        if plot_method == plot_methods[0]:
                            ax.scatter([forecast_date], [forecast], c=colors[project], label='forecast', marker='x', )
                        elif plot_method == plot_methods[1]:
                            for col in range(1, 3):
                                figure.add_trace(
                                    Scatter(marker=dict(color=['gray']), mode='markers', name='forecast',
                                            showlegend=True, x=[forecast_date], y=[forecast], ), col=col, row=1,)
                    else:
                        if plot_method == plot_methods[0]:
                            ax.scatter([forecast_date], [forecast], c=colors[project], marker='x', )
                        elif plot_method == plot_methods[1]:
                            for col in range(1, 3):
                                figure.add_trace(Scatter(marker=dict(color=['gray']), mode='markers', showlegend=False,
                                                         x=[forecast_date], y=[forecast], ), col=col, row=1,)
                    forecast_date += timedelta(days=1, )
                    forecast *= (1.0 + forecast_weight * row['rolling_change'])

        if plot_method == plot_methods[0]:
            ax.scatter(target_df['date'], target_df[target], label=target, c='blue', )
            ax.legend()
            out_file = './{}.png'.format(target)
            plt.savefig(out_file)
        elif plot_method == plot_methods[1]:
            for col in range(1, 3):
                figure.add_trace(Scatter(marker=dict(color=['blue']), mode='markers', name=target, x=target_df['date'],
                                         y=target_df[target], ), col=col, row=1, )
            figure.update_yaxes(col=2, row=1, type='log')
            output_file = './{}.html'.format(target)
            logger.info('saving HTML figure to {}'.format(output_file))
            plot(auto_open=False, auto_play=False, figure_or_data=figure, filename=output_file,
                 link_text='', output_type='file', show_link=False, validate=True, )
    logger.info('total time: {:5.2f}s'.format(time() - time_start))
