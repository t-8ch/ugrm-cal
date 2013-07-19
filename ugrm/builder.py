from icalendar import Calendar, Event, vDDDTypes
from config import (PRODID, MEETING_LENGTH, CAL_NAME, CAL_DESC,
                    REMOTE_SYNC_INTERVAL)
from datetime import datetime, timedelta, time
from hashlib import sha1
from pytz import utc

meeting_length = timedelta(minutes=MEETING_LENGTH)


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
                if meeting.url:
                    event.add('url', meeting.url)
                if meeting.description:
                    event.add('description', meeting.description)
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
