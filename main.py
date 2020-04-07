from logging import INFO
from logging import basicConfig
from logging import getLogger
from time import time

import matplotlib.pyplot as plt
import pandas as pd
import plotly.graph_objs as go


def float_color_to_hex(arg_float, arg_colormap):
    color_value = tuple([int(255 * arg_colormap(arg_float)[index]) for index in range(3)])
    return '#{:02x}{:02x}{:02x}'.format(color_value[0], color_value[1], color_value[2])


if __name__ == '__main__':
    time_start = time()
    logger = getLogger(__name__)
    basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=INFO)
    logger.info('started.')

    url = 'https://www.ecdc.europa.eu/sites/default/files/documents/COVID-19-geographic-disbtribution-worldwide.xlsx'
    logger.info('reading from {}'.format(url))
    df = pd.read_excel(url, )
    logger.info('data shape: {}'.format(df.shape))
    logger.info('data types: {}'.format(df.dtypes))

    plots = ['matplotlib', 'plotly', ]
    plot = plots[1]
    ax, fig = None, None
    if plot == plots[0]:
        fig, ax = plt.subplots(figsize=(15, 10))
    elif plot == plots[1]:
        fig = go.Figure()

    targets = ['countriesAndTerritories', 'geoId']
    target = targets[0]
    count = 0
    # todo can we sort by size instead of alphabetically by name?
    for geoId in df[target].unique():
        # todo get exclusion list in line with target/targets
        if geoId not in {'CN', 'JPG11668', } and geoId is not None:
            geodf = df[df[target] == geoId][['dateRep', 'cases', 'deaths', 'popData2018']]
            if len(geodf) > 10:
                logger.info('id: {} shape: {}'.format(geoId, geodf.shape))
                geodf['dateRep'] = pd.to_datetime(geodf['dateRep'])
                geodf = geodf[geodf['dateRep'] > '2020-03-01']
                geodf.set_index(['dateRep', 'cases', 'deaths']).unstack(fill_value=0, ).stack().sort_index(
                    level=1, ).reset_index()
                geodf = geodf.sort_values(by=['dateRep'], axis=0, ascending=True)
                logger.info('id: {} shape: {}'.format(geoId, geodf.shape))
                geodf['case_cumsum'] = geodf['cases'].cumsum()
                geodf['y'] = 10000 * geodf['case_cumsum'] / geodf['popData2018']
                geodf['death_cumsum'] = geodf['deaths'].cumsum()
                if geodf['case_cumsum'].max() > 5000:
                    if plot == plots[0]:
                        geodf.plot(x='dateRep', y='y', ax=ax, style='.', label=geoId, )
                    elif plot == plots[1]:
                        fig.add_trace(
                            go.Scatter(x=geodf.dateRep, y=geodf.y, name=geoId.replace('_', ' '), )
                        )

    if plot == plots[0]:
        plt.show()
    elif plot == plots[1]:
        fig.show()
    logger.info('total time: {:5.2f}s'.format(time() - time_start))
