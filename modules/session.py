"""module to manage session state variables in Streamlit."""
import streamlit as st

class SessionState:
    """Class to manage Streamlit session state variables."""
    
    def __init__(self):
        self._initialize_session_state()
    
    def _initialize_session_state(self):
        """Initialize default session state variables if not already set."""
        if 'area' not in st.session_state:
            st.session_state.area = 'NO1'
        if 'month' not in st.session_state:
            st.session_state.month = '2021-01'