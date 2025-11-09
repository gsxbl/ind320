"""module to manage session state variables in Streamlit."""
import streamlit as st
from .geo import GeoPos

class SessionState:
    """Class to manage Streamlit session state variables."""
    
    def __init__(self):
        self._geo = GeoPos()
        self._initialize_session_state()
    
    def _initialize_session_state(self):
        """Initialize default session state variables if not already set."""
        if 'area' not in st.session_state:
            st.session_state.area = 'NO1'

        if 'city' not in st.session_state:
            st.session_state.city = self._geo.city_name(st.session_state.area)

        if 'geo' not in st.session_state:
            st.session_state.geo = self._geo

        if 'month' not in st.session_state:
            st.session_state.month = '2021-01'

        if 'kind' not in st.session_state:
            st.session_state.kind = 'temperature_2m'

        if 'group' not in st.session_state:
            st.session_state.group = []

        if 'year' not in st.session_state:
            st.session_state.year = '2021'
            
        if 'timescale' not in st.session_state:
            st.session_state.timescale = 'Monthly'