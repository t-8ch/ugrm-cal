import requests
import time
from config import REMOTE_SYNC_INTERVAL, DEFAULT_TIMEZONE
from icalendar import Calendar
from pytz import utc, timezone
from meeting import Meeting
import logging
import datetime

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


session = requests.Session()
session.verify = False  # meh!
default_timezone = timezone(DEFAULT_TIMEZONE)


class RemoteCalendarFetcher(object):

    last_synced = 0
    data = []

    def __init__(self, url):
        self.url = url

    def get_data(self):
        now = time.time()
        if not (now - self.last_synced) > REMOTE_SYNC_INTERVAL * 60:
            logger.debug('Serving "{}" from cache'.format(self.url))
            return self.data

        meetings = []

        logger.info('Fetching "{}"'.format(self.url))
        resp = None
        try:
            resp = session.get(self.url)
        except requests.RequestError as e:
            logger.error('Failed to fetch "{}": "{}"'.format(self.url, str(e)))
            return []

        rcal = Calendar.from_ical(resp.text)

        # doing a full roundtrip here for convenience and to enforce utc
        for c in rcal.walk():
            if c.name == 'VEVENT':

                # don't support recurring for now, timezone issues
                if c.get('rrule'):
                    continue

                name = unicode(c.get('summary'))
                description = c.get('description', None)
                if description is not None:
                    description = unicode(description)

                start = None
                _start = c.get('dtstart').dt
                if isinstance(_start, datetime.date):
                    start = _start
                else:
                    start = _start.astimezone(utc)

                end = None
                _end = c.get('dtend', None)
                if _end is not None:
                    _end = _end.dt
                    if isinstance(_end, datetime.date):
                        end = _end
                    else:
                        end = _end.astimezone(utc)
                else:
                    _duration = c.get('duration', None)
                    end = start + _duration
                    end.replace(tzinfo=default_timezone)

                location = None
                _location = c.get('location')
                if _location is not None:
                    location = unicode(_location)

                meetings.append(Meeting(name=name, time=start,
                                description=description, end=end,
                                location=location))

        self.data = meetings
        self.last_synced = now
        return meetings
