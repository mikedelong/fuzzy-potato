from logging import INFO
from logging import basicConfig
from logging import getLogger
from time import time
import pandas as pd
import matplotlib.pyplot as plt


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

    # fig, ax = plt.subplots(figsize=(15, 10))
    fig = plt.figure(figsize=(15, 10))
    ax = fig.add_subplot(111)

    for geoId in df['geoId'].unique():
        if geoId not in {'CN', 'JPG11668', } and geoId is not None:
            geodf = df[df['geoId'] == geoId][['dateRep', 'cases', 'deaths']]
            if len(geodf) > 10:
                logger.info('id: {} shape: {}'.format(geoId, geodf.shape))
                geodf['dateRep'] = pd.to_datetime(geodf['dateRep'])
                geodf = geodf[geodf['dateRep'] > '2020-03-01']
                geodf.set_index(['dateRep', 'cases', 'deaths']).unstack(fill_value=0, ).stack().sort_index(
                    level=1, ).reset_index()
                geodf = geodf.sort_values(by=['dateRep'], axis=0, ascending=True)
                logger.info('id: {} shape: {}'.format(geoId, geodf.shape))
                geodf['case_cumsum'] = geodf['cases'].cumsum()
                geodf['death_cumsum'] = geodf['deaths'].cumsum()
                if geodf['case_cumsum'].max() > 10000:
                    geodf.plot(x='dateRep', y='case_cumsum', ax=ax, style='.', label=geoId, )
    plt.show()
    logger.info('total time: {:5.2f}s'.format(time() - time_start))
