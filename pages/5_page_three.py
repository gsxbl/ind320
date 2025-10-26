import streamlit as st
import plotly.graph_objects as go

from modules.api import GeoPos, OpenMeteo
from modules.session import SessionState

class Page3:
    '''
    This class represents the app page.
    
    Most page contents is rendered in the run method.
    Properties are used to mimic global variables,
    making them accessible to all methods.
    '''
    def __init__(self):
        # setup session state
        SessionState()

        # general page setup
        st.set_page_config(layout='wide')

        # instantiate and cache data
        self._api = OpenMeteo()
        self._loc = GeoPos()
        
        # extract months
        self._get_data()
        self._get_months()

    def _get_data(self):
        '''
        This method fetches and caches the dataset
        to the self._df property.
        '''
        self._df = self._api.get_weather_data(
            **self._loc(st.session_state.area),
        )
        
    def _get_months(self):
        '''
        This method extracts and sorts the available
        months in the dataset and creates the property
        self._months. Method is run once in the constructor.
        '''
        months = self._df.index.to_period("M")
        self._months = months.sort_values().unique()
    
    def _set_header(self):
        '''
        Method to set the page header.
        '''
        st.header(f'Weather Data for {self._loc(st.session_state.area, True)}')
    
    def _setup_kind_selector(self):
        '''
        Method to setup column selector for
        frontend. selection is persisted to
        streamlit session state.
        '''
        self._column = st.radio(
            'Columns', self._df.columns, index=self._df.columns.get_loc(st.session_state.kind),
            horizontal=True
        )
        st.session_state.kind = self._column
    

    def plot(self):
        '''
        Method to plot frontend selected column
        as a plotly graph figure to frontend.
        '''

        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=self._df.index,
                y=self._df[self._column],
                name=self._column, yaxis="y1"))
        
        fig.update_layout(
            title=f'Timeseries of Weather data',
            yaxis=dict(
                title=f'Measured Unit Value'
            )
            )
        st.plotly_chart(fig)

    def slice_data(self):
        '''
        Method to get slicer information from the
        self._slice property and slice the self._df property
        accordingly.
        '''
        start, stop = self._slice
        
        # slice the dataframe
        self._df = self._df[
            (self._df.index.to_period("M")>= start) &
            (self._df.index.to_period("M") <= stop)
            ]

    # --- PAGE CONTENTS ---
    def setup_contents(self):
        '''
        Method to get user inputs from the frontend.
        Column selector is rendered and stored in the 
        self._column propery.
        Slicer is rendered and input stored in the
        self._slice property.
        Relies heavily on contents of self._df.
        '''

        self._slice = st.select_slider(
            "Select time range",
            options=self._months,
            value=(self._months[0], self._months[-1])
        )
        
    def run(self):
        '''Main runtime method'''
        
        self._set_header()
        self._setup_kind_selector()
        self.setup_contents()
        self.slice_data()
        self.plot()

if __name__ == '__main__':
    main = Page3()
    main.run()