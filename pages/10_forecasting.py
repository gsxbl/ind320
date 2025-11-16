'''This page will implement forecasting functionalities.'''
import streamlit as st


from modules.api import OpenMeteo
from modules.db import Mongo
from modules.header import Header
from modules.session import SessionState


class Forecast:
    def __init__(self):
        # general setup
        self._state = SessionState()
        Header()

        self._api = OpenMeteo()
        self._db = Mongo()

    def _get_energy_data(self):
        '''get data from mongodb'''
        self._df_e = self._db.get_data(
            **self._state.kwargs,
            # index=['priceArea', st.session_state.column, 'startTime']
            index=['startTime']
        )

    def _get_wather_data(self):
        '''get data from openmeteo api'''
        self._df_w = self._api.get_weather_data(
            **st.session_state.geo,
            start_date=st.session_state.start_time,
            end_date=st.session_state.end_time,
            timescale=st.session_state.timescale
        )
    
    def _setup_forecasting_ui(self):
        '''setup forecasting ui elements'''
        pass

    def run(self):
        pass
    
if __name__ == '__main__':
    main = Forecast()
    main.run()