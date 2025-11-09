import pandas as pd
import streamlit as st
from modules.api import OpenMeteo, GeoPos
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
        SessionState()

        # instantiate and cache data
        self._api = OpenMeteo()
        self._loc = GeoPos()

    def _set_header(self):
        '''
        Method to set the page header.
        '''
        
        st.header(f'Weather Data for {(st.session_state.city)}')
        st.subheader(f'Period: {st.session_state.month}')

    ### LINE CHART COLUMN HELPER ###
    def agg_month(self, df:pd.DataFrame, month:str):
        '''
        Method to aggregate dataframe by month.
        '''
        df = df.loc[month]
        df = df.groupby(df.index.month).agg(list)
        df.index.name = 'Month'
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
            **self._loc(st.session_state.area),
        )
        # aggregate data by month
        df = self.agg_month(self._df, st.session_state.month)

        # set configuration for linecharts within Dataframe
        for col in df.columns:
            col_cfg = st.column_config.LineChartColumn(col)
            
            # render to frontend
            st.dataframe(df[col], column_config={col:col_cfg})
        
    def run(self):
        self.setup_contents()

if __name__ == '__main__':
    main = Page2()
    main.run()