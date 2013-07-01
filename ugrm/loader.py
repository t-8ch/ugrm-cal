import xml.etree.ElementTree as ET
from path import path
from dateutil.parser import parse as parsedate
from pytz import utc

from models import UserGroup, Meeting, Location, StaticSchedule, IcalSchedule

__all__ = ['XmlLoader']


class XmlLoader(object):

    def __init__(self, datadir):
        self.datadir = path(datadir)

    def list_groups(self):
        for f in self.datadir.glob('*.xml'):
            yield str(f.basename().stripext())

    def load_group(self, tag):
        root = ET.parse(str(self.datadir / path(tag + '.xml')))
        group_name = root.find('name').text
        group_url = root.find('url').text
        _defaultmeetinglocation = root.find('defaultmeetinglocation')

        default_location = None
        if _defaultmeetinglocation is not None:
            default_location = _defaultmeetinglocation.text

        schedule = None

        _schedule = root.find('schedule')
        if _schedule is not None:
            ical_feed = _schedule.find('ical')
            if ical_feed is not None:
                pass  # not implemented for now
                # schedule = IcalSchedule(ical_feed.text)
            else:
                meetings = []
                for meeting in _schedule.findall('meeting'):
                    time = parsedate(meeting.find('time').text).astimezone(utc)
                    name = meeting.find('name').text

                    description = None
                    _description = meeting.find('description')
                    if _description is not None:
                        description = self._normalize_description(
                            _description.text)

                    url = None
                    _url = meeting.find('url')
                    if url is not None:
                        url = _url

                    location = self._extract_location(meeting.find('location'))
                    meetings.append(Meeting(name=name, time=time,
                                            description=description,
                                            url=url, location=location))

                schedule = StaticSchedule(meetings)

        return UserGroup(tag=tag, name=group_name, schedule=schedule,
                         url=group_url, default_location=default_location)

    @staticmethod
    def _extract_location(root):
        if root is None:
            return None

        name = root.find('name').text
        url = None
        _url = root.find('url')
        if _url is not None:
            url = _url
        street = root.find('street').text
        zipcode = root.find('zip').text
        city = root.find('city').text

        return Location(name=name, url=url, street=street, zipcode=zipcode,
                        city=city)

    @staticmethod
    def _normalize_description(desc):
        return ' '.join(desc.split())

    def load_all(self):
        for group in self.list_groups():
            yield self.load_group(group)

    def __str__(self):
        return '<XmlLoader: {} >'.format(str(self.datadir))
