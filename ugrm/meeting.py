class Meeting(object):
    def __init__(self, name, time, description=None, url=None,
                 location=None, end=None):
        self.name = name
        self.time = time
        self.description = description
        self.url = url
        self.location = location
        self.end = end

    def __repr__(self):
        return '<Meeting: {} - {}>'.format(self.name, str(self.time))

    def __str__(self):
        return self.__repr__()
