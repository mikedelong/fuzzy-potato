from datetime import timedelta
from logging import INFO
from logging import basicConfig
from logging import getLogger
from time import time

import matplotlib.pyplot as plt
import pandas as pd
from pandas.plotting import register_matplotlib_converters
from plotly.graph_objects import Scatter
from plotly.offline import plot
from plotly.subplots import make_subplots

import numpy as np

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
    window_count = 5
    # todo compute the forecast weight to be a best fit
    forecast_weight = 1.0
    for target in ['positive', 'death']:
        once = True
        logger.info('forecasting {}'.format(target))
        target_df = df[['date', target]].copy(deep=True).sort_values(by='date')
        target_df['change'] = target_df[target].pct_change()

        if plot_method == plot_methods[0]:
            figure, axes = plt.subplots(figsize=(15, 10))
            # todo think about plotting y and log y in subplots for matplotlib only
            axes.set_yscale('log')
        else:
            figure = make_subplots(cols=2, rows=1)
            axes = None

        # todo fix hovertext for plotly
        # todo roll up projected data into columns
        for window in range(1, window_count + 1):
            column = 'rolling_change_{}'.format(window)
            target_df[column] = target_df['change'].rolling(window=window, min_periods=window, ).mean()

        for window in range(1, window_count + 1):
            column_to = 'projected_{}'.format(window)
            column_from = 'rolling_change_{}'.format(window)
            target_df[column_to] = target_df[target].shift(periods=1) * (1.0 + forecast_weight * target_df[column_from])

        # todo add forecast data one row at a time based on a mix of actual and forecast data
        # append the projection rows with just dates
        # todo patch up the rolling change and projected values for 'today'
        for project in range(5):
            new_row = {'date': target_df['date'].max() + timedelta(days=1, ), }
            for window in range(1, window_count + 1):
                column = 'rolling_change_{}'.format(window)
                column_to = 'projected_{}'.format(window)
                values = target_df[column].values[-window - 1:-1]
                new_row[column] = np.array(values).mean()
                if project == 0:
                    base_target_value = target_df[target_df['date'] == target_df['date'].max()][target][0]
                else:
                    base_target_value = target_df[target_df['date'] == target_df['date'].max()][column_to]
                new_row[column_to] = base_target_value * (1.0 + new_row[column])

            target_df = target_df.append(new_row, ignore_index=True)

        columns = ['date'] + ['rolling_change_{}'.format(window) for window in range(1, window_count + 1)]
        logger.info('\n{}'.format(target_df[columns].tail(6)))

        if once:
            once = False
            if plot_method == plot_methods[0]:
                for window in range(1, window_count + 1):
                    column = 'projected_{}'.format(window)
                    axes.scatter(target_df['date'], target_df[column], c='gray', label='forecast', marker='x', )
            elif plot_method == plot_methods[1]:
                for col in range(1, 3):
                    # todo fix name/legend
                    for window in range(1, window_count + 1):
                        column = 'projected_{}'.format(window)
                        figure.add_trace(
                            Scatter(marker=dict(color='Gray'), marker_symbol='x', mode='markers',
                                    name='forecast', showlegend=False, x=target_df['date'], y=target_df[column], ),
                            col=col, row=1, )
        else:
            if plot_method == plot_methods[0]:
                for window in range(1, window_count + 1):
                    column = 'projected_{}'.format(window)
                    axes.scatter(target_df['date'], target_df[column], c='gray', marker='x', )
            elif plot_method == plot_methods[1]:
                for col in range(1, 3):
                    for window in range(1, window_count + 1):
                        figure.add_trace(Scatter(marker=dict(color='Gray'), marker_symbol='x', mode='markers',
                                                 showlegend=False, x=target_df['date'],
                                                 y=target_df['projected_{}'.format(window)], ), col=col, row=1, )

        if plot_method == plot_methods[0]:
            axes.scatter(target_df['date'], target_df[target], label=target, c='blue', )
            axes.legend()
            out_file = './{}.png'.format(target)
            plt.savefig(out_file)
        elif plot_method == plot_methods[1]:
            for col in range(1, 3):
                if col == 1:
                    # todo no name here
                    figure.add_trace(Scatter(marker=dict(color=['blue']), mode='markers',
                                             showlegend=True, x=target_df['date'],
                                             y=target_df[target], ), col=col, row=1, )
                elif col == 2:
                    figure.add_trace(Scatter(marker=dict(color=['blue']), mode='markers', name=target,
                                             showlegend=True,
                                             x=target_df['date'], y=target_df[target], ), col=col, row=1, )
                else:
                    raise ValueError('col mysteriously neither 1 nor 2')
            figure.update_yaxes(col=2, row=1, type='log')
            output_file = './{}.html'.format(target)
            logger.info('saving HTML figure to {}'.format(output_file))
            plot(auto_open=False, auto_play=False, figure_or_data=figure, filename=output_file,
                 link_text='', output_type='file', show_link=False, validate=True, )
    logger.info('total time: {:5.2f}s'.format(time() - time_start))
