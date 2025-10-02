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
        self._success = False
    
    @property
    def success(self):
        return self._success

    @abstractmethod 
    def setup_query(self, kind, **kwargs):
        pass
    
    def call(self):
        if not self._run:
            return
        self._resp = re.get(self._url)
        if self._resp.status_code == 200:
            self._success = True

    def __call__(self, *args, **kwds):
        if isinstance(self._resp.json(), list):
            return self._resp.json()[0]
        else:
            return self._resp.json()


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
    

class Forcast(APICall):
    '''Special class for forcast calls'''
    def __init__(self, apiKey):
        super().__init__(apiKey)
        self._prefix = 'data/2.5/forecast?'

    def setup_query(self, **kwargs):
        lat = kwargs.get('lat', None)
        lon = kwargs.get('lon', None)

        # don't call the API without geolocation
        if not lat and lon:
            return
        
        self._url = self._BASEURL + self._prefix + \
            f'lat={lat}&lon={lon}' + f'&units={self._units}' + \
                f'&appid={self._APIkey}'

        self._run = True


class Weather:
    '''Wrapper class to hold all calls'''
    def __init__(self, apiKey):
        self._geoCode = GeoCode(apiKey)
        self._forcast = Forcast(apiKey)

    def location(self, kind, **kwargs):
        self.geoCode.setup_query(kind, **kwargs)
        self.geoCode.call()

    def upcoming(self):
        if not self.geoCode.success:
            st.write('forcast not called')
            return
        self.forcast.setup_query(**self.geoCode())
        st.write(self.forcast._url)
        # self.forcast.call()
        # return self.forcast()

    @property
    def geoCode(self):
        return self._geoCode
    
    @property
    def forcast(self):
        return self._forcast


