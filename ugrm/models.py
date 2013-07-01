from remote import RemoteCalendarFetcher

__all__ = ['UserGroup', 'Meeting', 'Location', 'IcalSchedule',
           'StaticSchedule']


class UserGroup(object):
    def __init__(self, tag, name, schedule=None, url=None,
                 default_location=None):
        self.tag = tag
        self.name = name
        self.schedule = schedule
        self.url = url
        self.default_location = default_location

    def __repr__(self):
        return '<UserGroup: {} ({})'.format(self.name, self.tag)

    def __str__(self):
        return self.__repr__()


class Meeting(object):
    def __init__(self, name, time, description=None, url=None,
                 location=None):
        self.name = name
        self.time = time
        self.description = description
        self.url = url
        self.location = location

    def __repr__(self):
        return '<Meeting: {} - {} >'.format(self.name, str(self.time))

    def __str__(self):
        return self.__repr__()


class Location(object):
    def __init__(self, name, street, zipcode, city, url=None):
        self.name = name
        self.street = street
        self.zipcode = zipcode
        self.city = city
        self.url = url

    def __repr__(self):
        if self.url is None:
            return '<Location: {} - {}, {} {} >'.format(
                self.name, self.street, self.zipcode, self.city)
        else:
            return '<Location: {} - {}, {} {} ({})>'.format(
                self.name, self.street, self.zipcode, self.city, self.url)

    def __str__(self):
        return "foO"


class Schedule(object):
    def get_data(self):
        raise NotImplementedError('subclass needs to override this')

    def alternative_url(self):
        raise NotImplementedError('subclass needs to override this')

    def __iter__(self):
        return self.get_data().__iter__()

    def __str__(self):
        return self.__repr__()


class IcalSchedule(Schedule):
    def __init__(self, url):
        raise NotImplementedError('needs to be done')
        self.url = url
        self.remote_fetcher = RemoteCalendarFetcher(url)

    def alternative_url(self):
        return self.url

    def __repr__(self):
        return '<IcalSchedule: {} >'.format(self.url)


class StaticSchedule(Schedule):
    def __init__(self, meetings):
        self.meetings = meetings

    def alternative_url(self):
        return None

    def get_data(self):
        return self.meetings

    def __repr__(self):
        return '<StaticSchedule: {} meetings >'.format(len(self.meetings))
