import streamlit as st
from modules.openWeather import Weather

class Page5:
    
    def __init__(self):
        # general page setup
        st.set_page_config(layout='wide')
        st.header('[dev] Weather app')

        # API wrappers
        self._APIkey = st.secrets['openWeather']['apiKey']
        self._Weather = Weather(self._APIkey)
        self._kwargs = {}

    def _setup_contents(self):
        self._mode = st.pills('Select search mode',
                 ['name', 'zip'])
    
        if self._mode == 'name':
            self._kwargs['city'] = st.text_input('Location name:')

        elif self._mode == 'zip':
            self._kwargs['zip'] = st.text_input('Zip Code:')
            self._kwargs['cc'] = st.text_input('Country code:')

    def _get_geolocation(self):
        self._Weather.location(
            self._mode, **self._kwargs
            )
          
    def _get_forcast(self):
        self._Weather.upcoming()
        


    def run(self):
        self._setup_contents()
        self._get_geolocation()
        self._get_forcast()

if __name__ == '__main__':
    page = Page5()
    page.run()