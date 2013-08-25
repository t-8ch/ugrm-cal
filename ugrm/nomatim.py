import requests

DEFAULT_API_URL = 'http://nominatim.openstreetmap.org/search'


class Nomatim(object):
    def __init__(self, api_url=DEFAULT_API_URL):
        self.session = requests.Session()
        self.session.params = {
            'format': 'json',
            'limit': '1',
        }
        self.api_url = api_url

    def resolve_coordinates(self, meeting):
        if not meeting.location:
            return

        location = meeting.location

        if location.coordinates:
            return

        if not location.zipcode or not location.city or location.city == 'TBA':
            return

        params = {
            'postalcode': location.zipcode,
            'city': location.city,
        }

        if location.street:
            if location.street == 'TBA':
                return
            params['street'] = location.street

        res = self.session.get(self.api_url, params=params)
        j = res.json()

        if len(j) == 0:
            return

        r = j[0]
        coords = {
            'lon': round(float(r['lon']), 6),
            'lat': round(float(r['lat']), 6),
        }

        location.coordinates = coords
