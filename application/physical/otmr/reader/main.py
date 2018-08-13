from datetime import datetime
import feedparser
import os

import webapp2

# These environment variables are configured in app.yaml.
CLOUDSQL_CONNECTION_NAME = os.environ.get('CLOUDSQL_CONNECTION_NAME')
CLOUDSQL_USER = os.environ.get('CLOUDSQL_USER')
CLOUDSQL_PASSWORD = os.environ.get('CLOUDSQL_PASSWORD')


class RssReader(object):

    def __init__(self, reqparam):
        config = {}
        if reqparam in ["usd", "gbp"]:
            config['fxref'] = reqparam
            config['url'] = "https://www.ecb.europa.eu/rss/fxref-{}.html".format(
                config['fxref'])
            self.etag = ""
            self.ratesToInsert = []
        else:
            config['fxref'] = 'usd'
            config['url'] = "https://www.ecb.europa.eu/rss/fxref-usd.html"

        self.config = config

    def read(self):
        feed = feedparser.parse(self.config['url'])
        self.ratesToInsert = feed.entries
        self.etag = feed.etag

    def handle(self, reqparam):
        self.read()
        return self.ratesToInsert


class RssPage(webapp2.RequestHandler):

    def post(self, param1):
        self.get(param1)

    def get(self, param1):
        reader = RssReader(param1)
        entries = reader.handle(param1)
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('otmr-dev-reader-v1/rss {}\n'.format(param1))
        for entry in entries:
            self.response.write('targetcurrency {}\nexchangerate {}\nupdated {}\n\n'.format(entry.cb_targetcurrency, entry.cb_exchangerate.replace(
                "\nEUR", "").strip(), datetime(*entry.updated_parsed[:5]+(min(entry.updated_parsed[5], 59),))))


class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('otmr-dev-reader-v1/')


app = webapp2.WSGIApplication([
    (r'/rss/ecb/(\w*?)$', RssPage),
    ('/', MainPage),
], debug=True)
