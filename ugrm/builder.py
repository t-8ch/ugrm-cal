from icalendar import (Calendar, Event, vDDDTypes, Timezone,
                       TimezoneDaylight, TimezoneStandard)
from config import (PRODID, MEETING_LENGTH, CAL_NAME, CAL_DESC,
                    REMOTE_SYNC_INTERVAL)
from datetime import datetime, timedelta, time
from hashlib import sha1
from pytz import utc

meeting_length = timedelta(minutes=MEETING_LENGTH)

tz = Timezone()
tz.add('tzid', 'Europe/Berlin')
tz.add('x-lic-location', 'Europe/Berlin')

_tzs = TimezoneStandard()
_tzs.add('tzname', 'CET')
_tzs.add('dtstart', datetime(1970, 10, 25, 3, 0, 0))
_tzs.add('rrule', {'freq': 'yearly', 'bymonth': 10, 'byday': '-1su'})
_tzs.add('TZOFFSETFROM', timedelta(hours=2))
_tzs.add('TZOFFSETTO', timedelta(hours=1))

_tzd = TimezoneDaylight()
_tzd.add('tzname', 'CEST')
_tzd.add('dtstart', datetime(1970, 3, 29, 2, 0, 0))
_tzd.add('rrule', {'freq': 'yearly', 'bymonth': 3, 'byday': '-1su'})
_tzd.add('TZOFFSETFROM', timedelta(hours=1))
_tzd.add('TZOFFSETTO', timedelta(hours=2))

tz.add_component(_tzs)
tz.add_component(_tzd)


def build_calendar(groups, exclude=None):
    exclude = set(exclude or [])
    included_slugs = sorted(list(set(map(lambda x: x.slug, groups)) - exclude))

    cal = Calendar()
    cal.add('prodid', PRODID)
    cal.add('version', '2.0')
    cal.add('x-wr-calname', CAL_NAME)
    desc = '{} ({})'.format(CAL_DESC, ', '.join(included_slugs))
    cal.add('x-wr-caldesc', desc)
    # https://tools.ietf.org/html/draft-daboo-icalendar-extensions-05#section-5.6
    refresh = vDDDTypes(timedelta(minutes=REMOTE_SYNC_INTERVAL))
    cal.add('refresh-interval;value=duration', refresh)
    cal.add('x-published-ttl', refresh)

    cal.add_component(tz)

    events = []

    now = datetime.now()

    for group in groups:
        if group.schedule is not None and group.slug not in exclude:
            for meeting in group.schedule:
                name = meeting.name
                start = meeting.time
                event = Event()
                event.add('summary', group.name + ': ' + name)
                event.add('dtstart', start)
                if meeting.end is None:
                    event.add('dtend', start + meeting_length)
                else:
                    event.add('dtend', meeting.end)
                event.add('dtstamp', now)
                if meeting.location:
                    event.add('location', unicode(meeting.location))
                    if hasattr('coordinates', meeting.location):
                        coords = meeting.location.coordinates
                        if coords:
                            event.add('geo', (coords['lat'], coords['lon']))
                if meeting.url:
                    event.add('url', meeting.url)
                if meeting.description:
                    event.add('description', meeting.description)
                if meeting.repeat:
                    event.add('rrule', meeting.repeat)
                event['uid'] = sha1(name.encode('utf-8') +
                                    str(start)).hexdigest()

                events.append(event)

    events = sorted(events, cmp=_cmp_dates)

    for event in events:
        cal.add_component(event)

    return cal.to_ical()


def _cmp_dates(d1, d2):
    d1 = d1['dtstart'].dt
    d2 = d2['dtstart'].dt

    if not isinstance(d1, datetime):
        d1 = datetime.combine(d1, time())
    if not isinstance(d2, datetime):
        d2 = datetime.combine(d2, time())

    if d1.tzinfo is None:
        d1 = d1.replace(tzinfo=utc)

    if d2.tzinfo is None:
        d2 = d2.replace(tzinfo=utc)

    return cmp(d1, d2)
