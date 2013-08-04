from remote import RemoteCalendarFetcher

__all__ = ['UserGroup', 'Location', 'IcalSchedule',
           'StaticSchedule']


class UserGroup(object):
    def __init__(self, slug, name, schedule=None, url=None,
                 default_location=None, tags=[], thumbnail=None):
        self.slug = slug
        self.name = name
        self.schedule = schedule
        self.url = url
        self.default_location = default_location
        self.tags = tags
        self.thumbnail = thumbnail

    def __repr__(self):
        return '<UserGroup: {} ({})'.format(self.name, self.slug)

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
        if self.url is None:
            return u'{}, {}, {} {}'.format(self.name, self.street,
                                           self.zipcode, self.city)
        else:
            return u'{} ({}), {}, {} {}'.format(self.name, self.url,
                                                self.street, self.zipcode,
                                                self.city)


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
        self.url = url
        self.remote_fetcher = RemoteCalendarFetcher(url)

    def alternative_url(self):
        return self.url

    def get_data(self):
        return self.remote_fetcher.get_data()

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
