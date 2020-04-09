from logging import INFO
from logging import basicConfig
from logging import getLogger
from time import time

import matplotlib.pyplot as plt
import pandas as pd
import plotly.graph_objs as go

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
    min_limit = 5000

    ids = list()
    for geoId in df[target].unique():
        if geoId is not None:
            total = df[df[target] == geoId][['cases', ]].sum()
            population = df[df[target] == geoId]['popData2018'].max()
            if total['cases'] > min_limit:
                ids.append((geoId, total['cases'] / population))

    ids = sorted(ids, key=lambda x: x[1], reverse=True)
    ids = [item[0] for item in ids]
    for geoId in ids:
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
