import pandas as pd
import streamlit as st
from modules.api import OpenMeteo
from modules.geo import GeoPos
from modules.header import Header
from modules.session import SessionState

class Page2:
    '''
    This class represents the app page.
    
    Most page contents is rendered in the run method.
    Properties are used to mimic global variables,
    making them accessible to all methods.
    '''
    def __init__(self):
        # general page setup
        st.set_page_config(layout='wide')
        self._state = SessionState()
        Header()

        # instantiate and cache data
        self._api = OpenMeteo()
        self._loc = GeoPos()

    def _set_header(self):
        '''
        Method to set the page header.
        '''
        st.header(f'Weather Data for {(st.session_state.city)}')
        if st.session_state.timescale == 'Custom':
            st.subheader(
                f'Period: {st.session_state.start_time} to {st.session_state.end_time}')
        elif st.session_state.timescale == 'Annual':
            st.subheader(f'Period: {st.session_state.year}')
        elif st.session_state.timescale == 'Monthly':
            st.subheader(f'Period: {st.session_state.month}')

    ### LINE CHART COLUMN HELPER ###
    def agg_month(self, df:pd.DataFrame):
        '''
        Method to group dataframe by month.
        '''
        return df
        

    # --- PAGE CONTENTS ---
    def setup_contents(self):
        '''
        Method to setup page contents.
        '''
        # render header
        self._set_header()
        
        # get weather data
        self._df = self._api.get_weather_data(
            **self._state.kwargs
        )
        # aggregate data by month
        df = self.agg_month(self._df)
        # iterate each column and plot values as linechart
        for col in df.columns:
            # Create dataframe with single column containing list of values
            chart_df = pd.DataFrame({col: [df[col].values]})
            col_cfg = st.column_config.LineChartColumn(col)
            
            # render to frontend
            st.dataframe(chart_df, column_config={col: col_cfg}, 
                         hide_index=True)
        
    def run(self):
        self.setup_contents()

if __name__ == '__main__':
    main = Page2()
    main.run()