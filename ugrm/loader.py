import xml.etree.ElementTree as ET
from path import path
from dateutil.parser import parse as parsedate
from pytz import utc

from meeting import Meeting
from models import UserGroup, Location, IcalSchedule, StaticSchedule

__all__ = ['XmlLoader']


class XmlLoader(object):

    def __init__(self, datadir):
        self.datadir = path(datadir)
        if not self.datadir.isdir():
            raise ValueError(
                'Invalid datadir specified "{}"'.format(str(self.datadir)))

    def list_groups(self):
        for f in self.datadir.glob('*.xml'):
            yield str(f.basename().stripext())

    def load_group(self, slug):
        root = ET.parse(str(self.datadir / path(slug + '.xml')))
        group_name = root.find('name').text
        group_url = root.find('url').text.strip()
        _dml = root.find('defaultmeetinglocation')

        schedule = None
        _schedule = root.find('schedule')

        default_location = None
        if _dml is not None:
            use_dml = _schedule.get('usedefaultmeetinglocation', '') == 'true'
            if use_dml:
                default_location = self._extract_location(_dml)

        tags = []
        _tags = root.find('tags')
        for _tag in _tags.findall('tag'):
            tags.append(_tag.text.lower())

        if _schedule is not None:
            ical_feed = _schedule.find('ical')
            if ical_feed is not None:
                schedule = IcalSchedule(ical_feed.text)
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

                    url = group_url
                    _url = meeting.find('url')
                    if _url is not None:
                        url = _url.text.strip()

                    location = self._extract_location(meeting.find('location'))
                    location = location or default_location
                    meetings.append(Meeting(name=name, time=time,
                                            description=description,
                                            url=url, location=location))

                schedule = StaticSchedule(meetings)

        thumbnail = self._get_thumbnail(slug)

        return UserGroup(slug=slug, name=group_name, schedule=schedule,
                         url=group_url, default_location=default_location,
                         tags=tags, thumbnail=thumbnail)

    @staticmethod
    def _extract_location(root):
        if root is None:
            return None

        name = root.find('name').text
        url = None
        _url = root.find('url')
        if _url is not None:
            url = _url.text
        street = root.find('street').text
        zipcode = root.find('zip').text
        city = root.find('city').text

        return Location(name=name, url=url, street=street, zipcode=zipcode,
                        city=city)

    @staticmethod
    def _normalize_description(desc):
        return ' '.join(desc.split())

    def _get_thumbnail(self, slug):
        extensions = ['png', 'jpg']
        for e in extensions:
            p = self.datadir.joinpath(slug + '.logo.' + e)
            if p.isfile():
                return p.basename()

    def load_all(self):
        for group in self.list_groups():
            yield self.load_group(group)

    def __str__(self):
        return '<XmlLoader: {} >'.format(str(self.datadir))
