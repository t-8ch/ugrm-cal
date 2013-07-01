import requests


session = requests.Session()


class RemoteCalendarFetcher(object):
    def __init__(self, url):
        self.url = url
