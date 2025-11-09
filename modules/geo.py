'''Module to handle geographical data.'''

class GeoPos:
    """Callable class to get geographical positions of Norwegian cities."""
    def __init__(self):
        self._locations = {
            "Oslo": {"latitude": 59.91, "longitude": 10.75},
            "Bergen": {"latitude": 60.39, "longitude": 5.32},
            "Trondheim": {"latitude": 63.43, "longitude": 10.40},
            "Tromsø": {"latitude": 69.65, "longitude": 18.96},
            "Kristiansand": {"latitude": 58.15, "longitude": 8.00},
        }

        self._conv = {'NO1':'Oslo', 'NO2':'Kristiansand', 
                   'NO3':'Trondheim', 'NO4':'Tromsø', 'NO5':'Bergen'}
        
        self._conv2 = {v:k for k,v in self._conv.items()}

    def __call__(self, arg):
        '''Method to get lat and long from area code'''
        # if to_loc:
        #     return self._conv.get(arg, None)
        arg = self._conv.get(arg, None)
        return self._locations.get(arg, None)
    
    def city_name(self, area_code):
        '''Method to get city name from area code'''
        return self._conv.get(area_code, None)
