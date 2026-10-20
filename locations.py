"""Google Places (New) adapter. Never persist API content or expose its key."""
import json
import math
import re
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class LocationUnavailable(ValueError):
    pass


class GooglePlaces:
    def __init__(self, key):
        self.key = key

    def call(self, path, data=None, fields=None):
        if not self.key:
            raise LocationUnavailable('Address lookup is unavailable. You can still browse and submit an address manually.')
        headers = {'X-Goog-Api-Key': self.key, 'Content-Type': 'application/json'}
        if fields:
            headers['X-Goog-FieldMask'] = fields
        req = Request('https://places.googleapis.com/v1/' + path,
                      data=json.dumps(data).encode() if data is not None else None, headers=headers)
        try:
            with urlopen(req, timeout=6) as response:
                return json.load(response)
        except (HTTPError, URLError, TimeoutError, OSError, ValueError):
            raise LocationUnavailable('Google location lookup could not finish. Try again later or browse without distance filters.') from None

    def geocode(self, address):
        places = self.call('places:searchText', {'textQuery': address, 'maxResultCount': 1}, 'places.location').get('places', [])
        if not places:
            raise LocationUnavailable('We could not find that address. Try a full street address, city, and state.')
        try:
            location = places[0]['location']
            lat, lon = float(location['latitude']), float(location['longitude'])
            if not math.isfinite(lat) or not math.isfinite(lon) or not -90 <= lat <= 90 or not -180 <= lon <= 180:
                raise ValueError()
            return lat, lon
        except (KeyError, TypeError, ValueError):
            raise LocationUnavailable('Google returned an incomplete location. Try another address.') from None

    def suggest(self, text, token):
        response = self.call('places:autocomplete', {'input': text, 'sessionToken': token,
                             'includedRegionCodes': ['us']}, 'suggestions.placePrediction.text')
        return [item['placePrediction']['text']['text'] for item in response.get('suggestions', [])
                if item.get('placePrediction', {}).get('text', {}).get('text')][:5]

    def kenosha(self):
        return self.call('places:searchText', {'textQuery': 'restaurants serving french fries in Kenosha Wisconsin',
                         'includedType': 'restaurant', 'maxResultCount': 5}, 'places.id').get('places', [])

    def details(self, place_id):
        if not re.fullmatch(r'[A-Za-z0-9_-]{1,255}', place_id):
            raise LocationUnavailable('Invalid Google place identifier.')
        return self.call('places/' + place_id, fields='displayName,formattedAddress,location,attributions,businessStatus')
