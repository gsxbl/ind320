"""This module will handle header to hold session state variables."""

import streamlit as st
from .session import SessionState
from .db import Mongo


class Header:
    '''
    This class represents the header module.
    
    It initializes the session state for the app.
    '''
    def __init__(self):
        # Initialize session state
        SessionState()
    
        # instantiate client
        self._db = Mongo()

        # render
        self.render_header()

    def _get_areas(self):
        '''
        Method to get available priceAreas for
        frontend radio selector
        '''
        self._areas = self._db.distinct(column='priceArea')

    def _get_groups(self):
        '''
        Method to get available productionGroups for
        frontend pills selector
        '''
        self._groups = self._db.distinct(column='productionGroup')

    def _get_years(self):
        '''
        Method to get available years from the cached data
        for frontend year selector
        '''
        self._years = self._db.years()

    def _get_months(self):
        '''
        Method to get available months from the cached data
        for frontend month selector
        '''
        self._months = self._db.months()

    def _setup_year_selector(self):
        '''
        Method to get year selection from
        frontend. Persist to streamlit session state.
        '''
        self._year = st.selectbox(
            '', self._years,
            index=self._years.index(st.session_state.year)
            )

        st.session_state.year = self._year

    def _setup_month_selector(self):
        '''
        Method to get month selection from
        frontend. Persist to streamlit session state.
        '''
        self._month = st.selectbox(
            '', self._months,
            index=self._months.index(st.session_state.month)
            )

        st.session_state.month = self._month

    def _setup_area_selector(self):
        '''
        Method to get radio button selection from
        frontend. Persist to streamlit session state.
        '''
        self._area = st.radio(
            '', self._areas,
            index=self._areas.index(st.session_state.area),
            horizontal=True
            )
        
        st.session_state.area = self._area

    def _setup_group_selector(self):
        '''
        Method to get pill button selections from
        frontend
        '''
        self._group = st.radio(
            '', self._groups,
            index=self._groups.index(st.session_state.group),
            horizontal=True
        )
        st.session_state.group = self._group

    def _setup_containers(self):
        '''
        Method to setup containers for header layout
        '''
        self._c1, self._c2 =st.columns(2)
    
    def render_header(self):
        '''
        Method to render the header components
        '''
        self._get_areas()
        self._get_groups()
        self._get_years()
        self._get_months()

        with st.expander('Data Selection Settings', expanded=False):
            self._setup_containers()

        with self._c1:
            self._setup_year_selector()
            self._setup_area_selector()
        with self._c2:
            self._setup_month_selector()
            self._setup_group_selector()