# https://covidtracking.com/api/us/daily.csv
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

    url = 'https://covidtracking.com/api/us/daily.csv'
    logger.info('reading from {}'.format(url))
    df = pd.read_csv(url)
    logger.info('data shape: {}'.format(df.shape))
    logger.info('data types: {}'.format(df.dtypes))

    logger.info('total time: {:5.2f}s'.format(time() - time_start))

