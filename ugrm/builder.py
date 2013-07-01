from icalendar import Calendar, Event
from config import PRODID, MEETING_LENGTH
from datetime import datetime, timedelta
from hashlib import sha1

meeting_length = timedelta(minutes=MEETING_LENGTH)


def build_calendar(groups, exclude=None):
    exclude = set(exclude or [])

    cal = Calendar()
    cal.add('prodid', PRODID)
    cal.add('version', '2.0')

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
                event.add('dtend', start + meeting_length)
                event.add('dtstamp', now)
                if meeting.location is not None:
                    event.add('location', unicode(meeting.location))
                if meeting.url is not None:
                    event.add('url', meeting.url)
                if meeting.description is not None:
                    event.add('description', meeting.description)
                event['uid'] = sha1(name.encode('utf-8')).hexdigest()

                events.append(event)

    events = sorted(events, key=lambda x: x['dtstart'].dt)

    for event in events:
        cal.add_component(event)

    return cal.to_ical()
