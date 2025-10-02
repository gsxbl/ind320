from abc import ABC, abstractmethod
import requests as re
import streamlit as st

class APICall(ABC):
    '''Base class for API calls'''
    def __init__(self, apiKey:str):
        # key
        self._APIkey = apiKey

        # API
        self._BASEURL = 'http://api.openweathermap.org/'
        self._prefix = None
        self._units = 'metric'
        self._run = False
        self._resp = None

    @abstractmethod 
    def setup_query(self, kind, **kwargs):
        pass
    
    @abstractmethod
    def search(self):
        if not self._run:
            return
        self._resp = re.get(self._url)


class GeoCode(APICall):
    '''Special class for geolocation search calls'''
    def __init__(self, apiKey):
        super().__init__(apiKey)
        self._prefix = 'geo/1.0/'

    def setup_query(self, kind, **kwargs):
        if not kind:
            return
        
        city = kwargs.get('city', None)
        zcode = kwargs.get('zip', None)
        cc = kwargs.get('cc', None)
        
        if 'zip' in kind and zcode and cc:
            q = f'zip?zip={zcode},{cc}'
        elif city:
            q = f'direct?q={kwargs["city"]}'
        else:
            return
        
        self._url = self._BASEURL + self._prefix + q + \
                f'&limit={kwargs.get("limit", 1)}' \
                    f'&appid={self._APIkey}'
        
        # enable api call
        self._run = True
    
    def search(self):
        return super().search()
    

class Forcast(APICall):
    '''Special class for forcast calls'''
    def __init__(self, apiKey):
        super().__init__(apiKey)
        self._prefix = 'data/2.5/forecast?'

    def setup_query(self, kind, **kwargs):
        lat = kwargs.get('lat', None)
        lon = kwargs.get('lon`', None)

        if not lat and lon:
            return
        
        self._url = self._BASEURL + self._prefix + \
            f'lat={lat}&lon={lon}' + f'units={self._units}' + \
                f'&appid={self._APIkey}'

        self._run = True
    
    def search(self):
        return super().search()

class Weather:
    def __init__(self, apiKey):
        self._geoCode = GeoCode(apiKey)
        # self._forcast = Forcast(apiKey)

    @property
    def geoCode(self):
        return self._geoCode
    
    @property
    def forcast(self):
        return self._forcast


