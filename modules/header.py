"""This module will handle header to hold session state variables."""

import streamlit as st
from .session import SessionState
from .geo import GeoPos
from .db import Mongo


class Header:
    '''
    This class represents the header module.
    
    It initializes the session state for the app.
    '''
    def __init__(self, render=True, **kwargs):
        # Initialize session state
        self._state = SessionState()
        GeoPos()
    
        # instantiate client
        self._db = Mongo()
        self._set_kwargs(**kwargs)

        # Optionally render header UI
        if render:
            self.render_header()
        else:
            self.initialize()
    
    def initialize(self):
        '''
        Initialize all header variables and data without rendering UI.
        Can be cached and used on the main page.
        '''
        # Fetch all required data
        self._get_areas()
        self._get_groups()
        self._get_years()
        self._get_months()
        self._get_time_range()
        
        # Set current timescale value
        self._timescale = st.session_state.timescale
    
    def _set_kwargs(self, **kwargs):
        '''
        Method to set any kwargs passed to the class
        '''
        self._group_options = kwargs.get('group_options', 'multi')

    def _get_areas(self):
        '''
        Method to get available priceAreas for
        frontend radio selector
        '''
        self._areas = self._db.distinct(column='priceArea', table=st.session_state.table)

    def _get_groups(self):
        '''
        Method to get available productionGroups for
        frontend pills selector
        '''
        st.session_state.column = 'productionGroup' if st.session_state.table == 'elhub' else 'consumptionGroup'
        self._groups = self._db.distinct(**self._state.kwargs)

    def _get_years(self):
        '''
        Method to get available years from the cached data
        for frontend year selector
        '''
        self._years = self._db.years(table=st.session_state.table)

    def _get_months(self):
        '''
        Method to get available months from the cached data
        for frontend month selector
        '''
        self._months = self._db.months(table=st.session_state.table)

    def _get_time_range(self):
        '''
        Method to get available time range from the cached data
        for frontend custom time selector
        '''
        self._time_range = self._db.distinct(
            table=st.session_state.table,
            column='startTime')

    def _setup_table_selector(self):
        '''
        Method to get table selection from
        frontend. Persist to streamlit session state.
        '''
        self._table = st.selectbox(
            'Select data table', ['Consumption', 'Production'],
            index=['consumption', 'elhub'].index(st.session_state.table)
            )

        if self._table == 'Production':
            st.session_state.table = 'elhub'
            st.session_state.column = 'productionGroup'
        else:
            st.session_state.table = 'consumption'
            st.session_state.column = 'consumptionGroup'

    def _setup_timescale_selector(self):
        '''
        Method to get timescale selection from
        frontend. Persist to streamlit session state.
        '''
        self._timescale = st.selectbox(
            'Select time scale', ['Monthly', 'Annual', 'Custom'],
            index=['Monthly', 'Annual', 'Custom'].index(st.session_state.timescale)
            )

        st.session_state.timescale = self._timescale

    def _setup_year_selector(self):
        '''
        Method to get year selection from
        frontend. Persist to streamlit session state.
        '''
        self._year = st.selectbox(
            'Select year', self._years,
            index=self._years.index(st.session_state.year)
            )

        st.session_state.year = self._year
        self._state.update_datetimes(self._year)

    def _setup_month_selector(self):
        '''
        Method to get month selection from
        frontend. Persist to streamlit session state.
        '''
        self._month = st.selectbox(
            'Select month', self._months,
            index=self._months.index(st.session_state.month)
            )

        st.session_state.month = self._month
        self._state.update_datetimes(self._month)

    def _setup_time_range_selector(self):
        '''
        Method to get time range selection from frontend.
        Only updates session state when Execute button is clicked.
        '''
        start_val = st.session_state.get('start_time')
        end_val = st.session_state.get('end_time')

        if not start_val or start_val not in self._time_range:
            start_val = self._time_range[0]
        if not end_val or end_val not in self._time_range:
            end_val = self._time_range[1]

        # Render slider without updating state
        start_time, end_time = st.select_slider(
            'Select time range',
            options=self._time_range,
            value=(start_val, end_val)
        )
        # Execute button only updates state when clicked
        if st.button('Execute', use_container_width=True):
            st.session_state.start_time = start_time
            st.session_state.end_time = end_time
            st.rerun()

    def _setup_area_selector(self):
        '''
        Method to get radio button selection from
        frontend. Persist to streamlit session state.
        '''
        self._area = st.radio(
            'Select price area', self._areas,
            index=self._areas.index(st.session_state.area),
            horizontal=True
            )
        
        self._state.update_area(self._area)

    def _setup_group_selector(self):
        '''
        Method to get pill button selections from
        frontend
        '''
        default = st.session_state.group if st.session_state.group else self._groups

        self._group = st.pills(
            f'Select {st.session_state.column}', self._groups,
            selection_mode=self._group_options,
            default=default,
        )
        if isinstance(self._group, str):
            self._group = [self._group]  # make it a list for consistency

        if st.button('Apply', width='stretch'):
            st.session_state.group = self._group
            st.rerun()

    def _setup_containers(self):
        '''
        Method to setup containers for header layout
        '''
        self._c1, self._c2, self._c3 = st.columns([2, 2, 3])
    
    def render_header(self):
        '''
        Method to render the header components in the correct order
        to preserve logic and dependencies.    
        '''
        with st.sidebar:
            st.header('⚡ Data Settings')
            
            # Section 1: Data Source Selection
            with st.expander('📊 Data Source', expanded=False):
                self._setup_table_selector()
                self._setup_timescale_selector()
            
            # Fetch data based on source selection
            self._get_areas()
            self._get_groups()
            self._get_years()
            self._get_months()
            self._get_time_range()
            
            # Section 2: Geographic Selection
            with st.expander('🗺️ Price Area', expanded=False):
                self._setup_area_selector()
            
            # Section 3: Temporal Selection
            with st.expander('📅 Time Period', expanded=False):
                if self._timescale == 'Monthly':
                    self._setup_month_selector()
                elif self._timescale == 'Custom':
                    self._setup_time_range_selector()
                else:
                    self._setup_year_selector()
            
            # Section 4: Data Categories
            with st.expander('📈 {} Categories'.format(
                st.session_state.column[:-5].capitalize()),
                             expanded=False):
                self._setup_group_selector()