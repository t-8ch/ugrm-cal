from icalendar import Calendar, Event
from config import PRODID, MEETING_LENGTH, CAL_NAME, CAL_DESC
from datetime import datetime, timedelta, time
from hashlib import sha1

meeting_length = timedelta(minutes=MEETING_LENGTH)


def build_calendar(groups, exclude=None):
    exclude = set(exclude or [])
    included_tags = sorted(list(set(map(lambda x: x.tag, groups)) - exclude))

    cal = Calendar()
    cal.add('prodid', PRODID)
    cal.add('version', '2.0')
    cal.add('x-wr-calname', CAL_NAME)
    desc = '{} ({})'.format(CAL_DESC, ', '.join(included_tags))
    cal.add('x-wr-caldesc', desc)

    events = []

    now = datetime.now()

    for group in groups:
        if group.schedule is not None and group.tag not in exclude:
            for meeting in group.schedule:
                name = meeting.name
                start = meeting.time
                event = Event()
                event.add('summary', name)
                event.add('dtstart', start)
                if meeting.end is None:
                    event.add('dtend', start + meeting_length)
                else:
                    event.add('dtend', meeting.end)
                event.add('dtstamp', now)
                if meeting.location is not None:
                    event.add('location', unicode(meeting.location))
                if meeting.url is not None:
                    event.add('url', meeting.url)
                if meeting.description is not None:
                    event.add('description', meeting.description)
                event['uid'] = sha1(name.encode('utf-8')).hexdigest()

                events.append(event)

    events = sorted(events, cmp=_cmp_dates)

    for event in events:
        cal.add_component(event)

    return cal.to_ical()


def _cmp_dates(d1, d2):
    if isinstance(d1, datetime):
        d1 = datetime.combine(d1, time())
    if isinstance(d2, datetime):
        d2 = datetime.combine(d2, time())

    return cmp(d1, d2)
