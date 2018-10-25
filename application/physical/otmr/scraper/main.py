import cStringIO
import csv
import datetime
import locale
import os
import urllib  # Python2.x
from decimal import Decimal, getcontext
from random import randint
from time import sleep

import cloudstorage as gcs
import MySQLdb
import webapp2
from bs4 import BeautifulSoup
from google.appengine.api import app_identity, urlfetch

urlfetch.set_default_fetch_deadline(10)

getcontext().prec = 7  # each thread has its own context

# These environment variables are configured in app.yaml.
CLOUDSQL_CONNECTION_NAME = os.environ.get('CLOUDSQL_CONNECTION_NAME')
CLOUDSQL_USER = os.environ.get('CLOUDSQL_USER')
CLOUDSQL_PASSWORD = os.environ.get('CLOUDSQL_PASSWORD')

# gapps does not support locale
# locale.setlocale(locale.LC_ALL, 'de_DE.UTF-8')


class CnnFearGreedScraper(object):

    def __init__(self):
        config = {}
        config['symbol'] = 'myCNNFG'
        config['xpath'] = '//*[@id="needleChart"]/ul/li[1]'
        config['selector'] = '#needleChart > ul > li:nth-child(1)'
        config['url'] = 'https://money.cnn.com/data/fear-and-greed/'
        config['timeout'] = 10
        self.config = config
        self.result = ''

    def __make_request(self):

        headers = {
            "User-Agent": "OTMR cprior@gmail.com",
            "Accept-Language": "de-DE"
        }

        try:
            result = urlfetch.fetch(
                self.config['url'], deadline=self.config['timeout'], headers=headers)
            if result.status_code == 200:
                # self.response.write(result.content)
                return result.status_code, self.config['url'], result.content
            else:
                # self.response.status_code = result.status_code
                return result.status_code, self.config['url'], None
        except urlfetch.Error:
            # self.response.status_code = 501
            return result.status_code, self.config['url'], None

    def __parse_result(self, url, html):
        try:
            soup = BeautifulSoup(html, 'html.parser')

            result = {}
            items = soup.select('#needleChart > ul > li')
            for item in items:
                item = item.text.strip()
                if item.split()[3] == "Now:":
                    for part in item.split():
                        try:
                            result['now'] = int(part)
                        except ValueError:
                            pass
                elif item.split()[3] == "Previous":
                    for part in item.split():
                        try:
                            result['previous'] = int(part)
                        except ValueError:
                            pass
                else:
                    pass
            lastupdatedstring = soup.select('#needleAsOfDate')
            # https://stackoverflow.com/a/1712131/9576512
            yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
            yesterday.strftime('%Y')

            # https://stackoverflow.com/a/466376/9576512
            datetime_object = datetime.datetime.strptime(yesterday.strftime(
                '%Y')+lastupdatedstring[0].text.strip(), '%YLast updated %b %d at %I:%M%p')

            result['date'] = datetime.datetime.strftime(
                datetime_object, "%Y-%m-%d")
            result['time'] = datetime.datetime.strftime(
                datetime_object, "%H:%M:%S")

            self.result = result

        except Exception as e:
            raise e

    def __persistFearGreed(self):
        db = connect_to_cloudsql()
        cursor = db.cursor()
        cursor.execute(
            'INSERT IGNORE INTO `otmr`.`quotes` (`isin`, `exchange_id`, `currency_id`, `date`,`time`,`close`) VALUES (%s, %s, %s, %s, %s, %s);', (
                self.config['symbol'], 2, 1, self.result['date'], self.result['time'], self.result['now']))
        db.commit()

    def handle(self):
        status_code, url, html = self.__make_request()
        if html is not None:
            self.__parse_result(url, html)
            # self.__saveCsv()
            self.__persistFearGreed()
        else:
            self.results = None


class OnvistaIndexScraper(object):

    def __init__(self, reqparam):

        todos = {'MSCIWorld': {'notationId': '3193857', 'assetNameUnquoted': 'MSCI WORLD ', 'currency': 'USD', 'type': 'index', 'id': 'msci-world', 'isin': 'XC0009692739', 'wkn': '969273'},
                 'MSCIEM': {'notationId': '1643097', 'assetNameUnquoted': 'MSCI EM', 'currency': 'USD', 'type': 'index', 'id': 'msci-em', 'isin': 'CH0007292201', 'wkn': 'A0LLXT'}}

        for todo in todos:
            if todo == reqparam:
                config = todos[todo]
                # print(todos[todo])
                break

        config['assetName'] = urllib.quote(config['assetNameUnquoted'])

        config['url'] = 'https://www.onvista.de/onvista/times+sales/popup/historische-kurse/?' \
            'notationId={0}&'\
            'dateStart={1}&'\
            'interval=M1&'\
            'assetName={2}&'\
            'exchange=au%C3%9Ferb%C3%B6rslich'\
            ''.format(config['notationId'],
                      (datetime.datetime.now() - datetime.timedelta(days=16)
                       ).date().strftime('%Y-%m-%d'),
                      config['assetName'])

        if 'timeout' not in config:
            config['timeout'] = 10

        self.config = config

        self.results = []

    def __make_request(self):

        headers = {
            "User-Agent": "OTMR cprior@gmail.com",
            "Accept-Language": "de-DE"
        }

        try:
            result = urlfetch.fetch(
                self.config['url'], deadline=self.config['timeout'], headers=headers)
            if result.status_code == 200:
                # self.response.write(result.content)
                return result.status_code, self.config['url'], result.content
            else:
                # self.response.status_code = result.status_code
                return result.status_code, self.config['url'], None
        except urlfetch.Error:
            # self.response.status_code = 501
            return result.status_code, self.config['url'], None

    def __parse_result(self, url, html):
        try:
            soup = BeautifulSoup(html, 'html.parser')

            # https://stackoverflow.com/a/14768242/9576512
            table = soup.find('table')
            table_body = table.find('tbody')

            rows = table_body.find_all('tr')
            for row in rows:
                cols = row.find_all('td')
                cols = [ele.text.strip() for ele in cols]
                if self.config['assetNameUnquoted'] in html:
                    # print('*'*100)
                    # self.results.append([ele for ele in cols if ele]) # Get rid of empty values
                    # ohlc are always the same value for MSCI indivces
                    getcontext().prec = 7
                    self.results.append([datetime.datetime.strptime(cols[0], '%d.%m.%Y').strftime('%Y-%m-%d'),
                                         'XXX',
                                         'MSCI',
                                         'index',
                                         self.config['isin'],
                                         Decimal(cols[1].replace(
                                             '.', '').replace(',', '.')),
                                         Decimal(cols[2].replace(
                                             '.', '').replace(',', '.')),
                                         Decimal(cols[3].replace(
                                             '.', '').replace(',', '.')),
                                         Decimal(cols[4].replace(
                                             '.', '').replace(',', '.')),
                                         Decimal(0)])

        except Exception as e:
            raise e

    def __persistQuote(self):
        db = connect_to_cloudsql()
        cursor = db.cursor()
        for result in self.results:
            cursor.execute(
                'INSERT IGNORE INTO `otmr`.`quotes` (`isin`, `exchange_id`, `currency_id`,`date`,`time`,`resolution`,`open`,`high`,`low`,`close`,`volume`) VALUES (%s, %s, %s, %s, %s,%s, %s, %s, %s, %s, %s);', (
                    result[4], 1, 1, result[0], '21:55:00', 'daily', result[5], result[5], result[5], result[5], 0))
        db.commit()

    def __persist(self):
        db = connect_to_cloudsql()
        cursor = db.cursor()
        cursor.execute('INSERT INTO `otmr`.`logs` (`msg`) VALUES ("test");')
        db.commit()

    def __saveCsv(self):
        bucket_name = os.environ.get(
            'BUCKET_NAME', app_identity.get_default_gcs_bucket_name())
        write_retry_params = gcs.RetryParams(backoff_factor=1.1)
        sio = cStringIO.StringIO()
        writer = csv.writer(sio)
        # writer.writerow(['foo', 'foo,bar', 'bar'])
        writer.writerow(['Date', 'Currency', 'Exchange', 'type', 'isin',
                         'open', 'high', 'low', 'close', 'volume'])
        for result in self.results:
            writer.writerow([result[0], result[1], result[2], result[3],
                             result[4], result[5], result[6], result[7]])
        sio.seek(0)

        gcs_file = gcs.open('/' + bucket_name + '/' + self.config['id'] + '.csv',
                            'w',
                            content_type='text/csv',
                            options={'x-goog-meta-foo': 'foo',
                                     'x-goog-meta-bar': 'bar'},
                            retry_params=write_retry_params)
        # sio -> Expected str but got <type 'cStringIO.StringO'>.
        gcs_file.write(sio.read())
        gcs_file.close()

    def handle(self):
        status_code, url, html = self.__make_request()
        if html is not None:
            self.__parse_result(url, html)
            self.__saveCsv()
            self.__persistQuote()
        else:
            self.results = None


class Onvista(webapp2.RequestHandler):
    def post(self, param1):
        scraper = OnvistaIndexScraper(param1)
        scraper.handle()

    def get(self, param1):
        mylog(param1)
        scraper = OnvistaIndexScraper(param1)
        scraper.handle()
        self.response.write(
            '<pre>'+scraper.config['url'] + '\n' + str(scraper.results) + '</pre>\n\n')


class CnnFearGreed(webapp2.RequestHandler):
    def post(self):
        scraper = CnnFearGreedScraper()
        scraper.handle()

    def get(self):
        mylog('cnnfeargreed')
        scraper = CnnFearGreedScraper()
        scraper.handle()
        self.response.write(
            '<pre>'+scraper.config['url'] + '\n' + str(scraper.result) + '</pre>\n\n')


class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'

        self.response.write('otmr-dev-scraper-v1/')


def connect_to_cloudsql():
    # When deployed to App Engine, the `SERVER_SOFTWARE` environment variable
    # will be set to 'Google App Engine/version'.
    if os.getenv('SERVER_SOFTWARE', '').startswith('Google App Engine/'):
        # Connect using the unix socket located at
        # /cloudsql/cloudsql-connection-name.
        cloudsql_unix_socket = os.path.join(
            '/cloudsql', CLOUDSQL_CONNECTION_NAME)

        db = MySQLdb.connect(
            unix_socket=cloudsql_unix_socket,
            user=CLOUDSQL_USER,
            passwd=CLOUDSQL_PASSWORD)

    # If the unix socket is unavailable, then try to connect using TCP. This
    # will work if you're running a local MySQL server or using the Cloud SQL
    # proxy, for example:
    #
    #   $ cloud_sql_proxy -instances=your-connection-name=tcp:3306
    #
    else:
        db = MySQLdb.connect(
            host='127.0.0.1', user=CLOUDSQL_USER, passwd=CLOUDSQL_PASSWORD)

    return db


def mylog(msg):
    db = connect_to_cloudsql()
    cursor = db.cursor()
    cursor.execute("INSERT INTO otmr.logs (msg) VALUES (%s);", [msg])
    db.commit()


class MysqlPage(webapp2.RequestHandler):
    def get(self):
        """Simple request handler that shows all of the MySQL variables."""
        self.response.headers['Content-Type'] = 'text/plain'

        db = connect_to_cloudsql()
        cursor = db.cursor()
        cursor.execute('INSERT INTO `otmr`.`logs` (`msg`) VALUES ("test");')
        db.commit()
        cursor.execute('SHOW VARIABLES')

        for r in cursor.fetchall():
            self.response.write('{}\n'.format(r))


app = webapp2.WSGIApplication([
    ('/onvista/(\w*?)$', Onvista),
    ('/cnnfeargreed', CnnFearGreed),
    ('/db', MysqlPage),
    ('/', MainPage),
], debug=True)
