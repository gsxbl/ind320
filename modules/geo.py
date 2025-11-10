'''Module to handle geographical data.'''

class GeoPos:
    """Callable class to get geographical positions of Norwegian cities."""
    def __init__(self):
        self._locations = {
            "NO1": {
                'city': "Oslo",
                'nve_code': 6,
                'location': {
                    "latitude": 59.91,
                    "longitude": 10.75
                }
            },
            "NO2": {
                'city': "Kristiansand",
                'nve_code': 7,
                'location': {
                    "latitude": 58.15,
                    "longitude": 8.00
                }
            },
            "NO3": {
                'city': "Trondheim",
                'nve_code': 7,
                'location': {
                    "latitude": 63.43,
                    "longitude": 10.40
                }
            },
            "NO4": {
                'city': "Tromsø",
                'nve_code': 8,
                'location': {
                    "latitude": 69.65,
                    "longitude": 18.96
                }
            },
            "NO5": {
                'city': "Bergen",
                'nve_code': 9,
                'location': {
                    "latitude": 60.39,
                    "longitude": 5.32
                }
            },
        }

    def __call__(self, area_code):
        '''Method to get lat and long from area code'''
        loc = self._locations.get(area_code)
        return loc['location'] if loc else None

    def city_name(self, area_code):
        '''Method to get city name from area code'''
        loc = self._locations.get(area_code)
        return loc['city'] if loc else None
