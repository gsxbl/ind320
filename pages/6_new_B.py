import streamlit as st
import modules
from modules.session import SessionState

from modules.api import OpenMeteo
from modules.geo import GeoPos
from modules.analysis import plot_SPC, plot_LOF

class NewB:
    '''
    This class represents the app page.
    
    Most page contents is rendered in the run method.
    Properties are used to mimic global variables,
    making them accessible to all methods.
    '''
    def __init__(self):
        # general page setup
        st.set_page_config(layout='wide')
        SessionState()

        # instantiate and cache data
        self._api = OpenMeteo()
        self._loc = GeoPos()

    def _set_header(self):
        '''
        Method to set the page header.
        '''
        st.header(f'Weather Analysis for {st.session_state.city}')

    def _get_data(self):
        '''
        Method to get data from API based on
        selected area in session state
        '''
        self._df = self._api.get_weather_data(
            **self._loc(st.session_state.area))

    def _setup_selector(self):
        '''
        Method to setup column selector for
        frontend. selection is persisted to
        streamlit session state.
        '''
        self._column = st.radio(
            '', self._df.columns,
            index=self._df.columns.get_loc(st.session_state.kind),
            horizontal=True
        )
        st.session_state.kind = self._column  
    
    def _setup_tabs(self):
        '''
        Method to setup tabs for the page;
        one tab for Outlier/SPC,
        another for Anomaly/LOF
        '''
        self.t1, self.t2 = st.tabs(['Outlier/SPC', 'Anomaly/LOF'])

    def _setup_spc_ui(self):
        '''
        Method to setup SPC tab UI elements
        '''
        with st.expander('SPC Settings'):
            self._cf = st.number_input(
                'Cutoff Frequency', value=30, key='cutoff_freq')
            
            self._pcut = st.number_input(
                'Proportion Cut', value=0.05, key='proportioncut')
            
            self._k = st.number_input(
                'k standard deviations', value=3, key='k')

    def _setup_lof_ui(self):
        '''
        Method to setup LOF tab UI elements
        '''
        with st.expander('LOF Settings'):
            self.cont = st.number_input(
                'Contamination', value=0.01, key='contamination')
            
            self.n_neighbors = st.number_input(
                'Number of Neighbors', value=3, key='n_neighbors')

    # --- PAGE CONTENTS ---
    def setup_contents(self):
        '''Method to setup page contents in tabs'''

        # use tab one
        with self.t1:
            self._setup_spc_ui()
            fig, self._outliers = plot_SPC(self._df, st.session_state.kind,
                                            cutoff_freq=self._cf,
                                            proportioncut=self._pcut,
                                            k=self._k)
            # render plotly figure
            st.plotly_chart(fig)
            st.dataframe(self._outliers.describe().T, width=200)
        
        # use tab two
        with self.t2:
            self._setup_lof_ui()
            fig, self._anomalies = plot_LOF(self._df, st.session_state.kind,
                                            contamination=self.cont,
                                            n_neighbors=self.n_neighbors)
            # render plotly figure
            st.plotly_chart(fig)
            st.dataframe(self._anomalies.describe().T, width=200)

    def run(self):
        self._set_header()
        self._get_data()
        self._setup_selector()
        self._setup_tabs()
        self.setup_contents()

if __name__ == '__main__':
    main = NewB()
    main.run()