import numpy as np
import cStringIO
import matplotlib.pyplot as plt
import datetime
from matplotlib import dates

import matplotlib.dates as mdates
from mpl_finance import candlestick_ohlc

import webapp2

import logging
import json
import os
import cloudstorage as gcs

from google.appengine.api import app_identity

import mplsol
#from cycler import cycler


class CharterPage(webapp2.RequestHandler):

    def get(self, part_1, part_2):
        self.handle(part_1, part_2)

    def post(self, part_1, part_2):
        self.handle(part_1, part_2)

    def handle(self, part_1, part_2):
        bucket_name = os.environ.get(
            'BUCKET_NAME', app_identity.get_default_gcs_bucket_name())

        # plt.plot(np.random.random((20)), "r-")
        # sio = cStringIO.StringIO()
        # plt.savefig(sio, format="png")
        # https: // stackoverflow.com/a/8598881/9576512
        # sio.seek(0)
        self.response.headers['Content-Type'] = 'text/plain'

        gcs_file = gcs.open('/' + bucket_name + '/' +
                            "av_TIME_SERIES_DAILY_ADJUSTED_"+part_2+".json")
        content = gcs_file.read()
        gcs_file.close()

        data = json.loads(content)
        date = []
        open = []
        high = []
        low = []
        close = []
        ohlc = []
        for day in data['Time Series (Daily)']:
            if data['Time Series (Daily)'][day]['1. open'] != '0.0000':
                date.append(dates.date2num(
                    datetime.datetime.strptime(day, '%Y-%m-%d')))
                open.append(data['Time Series (Daily)'][day]['1. open'])
                high.append(data['Time Series (Daily)'][day]['2. high'])
                low.append(data['Time Series (Daily)'][day]['3. low'])
                close.append(data['Time Series (Daily)']
                             [day]['5. adjusted close'])
                appendme = dates.date2num(datetime.datetime.strptime(day, '%Y-%m-%d')), \
                    float(data['Time Series (Daily)'][day]['1. open']),\
                    float(data['Time Series (Daily)'][day]['2. high']),\
                    float(data['Time Series (Daily)'][day]['3. low']),\
                    float(data['Time Series (Daily)']
                          [day]['5. adjusted close'])
                ohlc.append(appendme)
        # self.response.write(ohlc)

        mplsol.setup(color="sol", lines_only=False, dark=False)

        f1, ax = plt.subplots(figsize=(10, 5))
        candlestick_ohlc(ax, ohlc, width=0.6,
                         colorup='#859900', colordown='#dc322f')
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        sio = cStringIO.StringIO()
        plt.title("Last {0} days of {1}".format(len(ohlc), part_2))
        plt.savefig(sio, format="png")
        # https: // stackoverflow.com/a/8598881/9576512
        sio.seek(0)

        self.response.write('Using bucket name: ' + bucket_name + '\n\n')
        self.response.write(self.request.route_args)

        write_retry_params = gcs.RetryParams(backoff_factor=1.1)
        gcs_file = gcs.open('/' + bucket_name + '/' + part_2 + '.png',
                            'w',
                            content_type='image/png',
                            options={'x-goog-meta-foo': 'foo',
                                     'x-goog-meta-bar': 'bar',
                                     'cache-control': 'public, max-age=30',
                                     'x-goog-acl': 'public-read'},  # default
                            retry_params=write_retry_params)
        # sio -> Expected str but got <type 'cStringIO.StringO'>.
        gcs_file.write(sio.read())
        gcs_file.close()


class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'

        self.response.write('otmr-dev-charter-v1/')


app = webapp2.WSGIApplication([('/(\w*?)/(\w*?)$', CharterPage),
                               ('/', MainPage)], debug=True)
