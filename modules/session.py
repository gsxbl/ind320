"""module to manage session state variables in Streamlit."""
import streamlit as st
from datetime import datetime, date
from .geo import GeoPos

class SessionState:
    """Class to manage Streamlit session state variables."""
    
    def __init__(self):
        self._geo = GeoPos()
        self._initialize_session_state()
    
    def _initialize_session_state(self):
        """Initialize default session state variables if not already set."""
        ### MONGODB / Data Selection Parameters ###
        if 'table' not in st.session_state:
            st.session_state.table = 'consumption'
        
        if 'column' not in st.session_state:
            st.session_state.column = 'consumptionGroup'

        if 'group' not in st.session_state:
            st.session_state.group = []

        if 'month' not in st.session_state:
            st.session_state.month = datetime(2022, 1, 1)

        if 'year' not in st.session_state:
            st.session_state.year = datetime(2022, 1, 1)

        if 'start_time' not in st.session_state:
            st.session_state.start_time = datetime(2022, 1, 1, 0, 0, 0)

        if 'end_time' not in st.session_state:
            st.session_state.end_time = datetime(2022, 2, 1, 0, 0, 0)

        if 'timescale' not in st.session_state:
            st.session_state.timescale = 'Monthly'
        
        if 'area' not in st.session_state:
            st.session_state.area = 'NO1'

        ### GEO / Location Parameters ###
        if 'city' not in st.session_state:
            st.session_state.city = self._geo.city_name(st.session_state.area)

        if 'geo' not in st.session_state:
            st.session_state.geo = self._geo(st.session_state.area)

        if 'nve_code' not in st.session_state:
            st.session_state.nve_code = self._geo._locations[
                st.session_state.area]['nve_code']

        ### OPENMETEO / Weather Parameters ###
        if 'kind' not in st.session_state:
            st.session_state.kind = 'temperature_2m'

        # if 'latitude' not in st.session_state:
        #     st.session_state.latitude = st.session_state.geo['latitude']
        
        # if 'longitude' not in st.session_state:
        #     st.session_state.longitude = st.session_state.geo['longitude']

        ### SNOW ANALYSIS PARAMETERS ###
        if 'T' not in st.session_state:
            st.session_state.T = 3000
        
        if 'F' not in st.session_state:
            st.session_state.F = 30000

        if 'theta' not in st.session_state:
            st.session_state.theta = 0.5

    def update_area(self, area_code):
        """Update area-related session state variables."""
        st.session_state.area = area_code
        st.session_state.city = self._geo.city_name(area_code)
        st.session_state.geo = self._geo(area_code)
        st.session_state.nve_code = self._geo._locations[area_code]['nve_code']

    def update_datetimes(self, dt_object):
        """Update datetime-related session state variables."""
        y, m = dt_object.year, dt_object.month

        if st.session_state.timescale == 'Annual':
            st.session_state.start_time = datetime(y, 1, 1, 0, 0, 0)
            st.session_state.end_time = datetime(y + 1, 1, 1, 0, 0, 0)
        elif st.session_state.timescale == 'Monthly':
            st.session_state.start_time = datetime(y, m, 1, 0, 0, 0)
            if m == 12:
                st.session_state.end_time = datetime(y + 1, 1, 1, 0, 0, 0)
            else:
                st.session_state.end_time = datetime(y, m + 1, 1, 0, 0, 0)

        st.session_state.year = datetime(y, 1, 1)
        st.session_state.month = datetime(y, m, 1)

    def _return_kwargs(self):
        """Return current session state as keyword arguments."""
        return {
            'table': st.session_state.table,
            'area': st.session_state.area,
            'city': st.session_state.city,
            'geo': st.session_state.geo,
            'nve_code': st.session_state.nve_code,
            'kind': st.session_state.kind,
            'group': st.session_state.group,
            'month': st.session_state.month,
            'year': st.session_state.year,
            'start_time': st.session_state.start_time,
            'end_time': st.session_state.end_time,
            'timescale': st.session_state.timescale,
            'column': st.session_state.column,
            'latitude': st.session_state.geo['latitude'],
            'longitude': st.session_state.geo['longitude'],
            'start_date': st.session_state.start_time.date().strftime('%Y-%m-%d'),
            'end_date': st.session_state.end_time.date().strftime('%Y-%m-%d'),
            'T': st.session_state.T,
            'F': st.session_state.F,
            'theta': st.session_state.theta
        }

    @property
    def kwargs(self):
        """Return current session state as keyword arguments."""
        return self._return_kwargs()
