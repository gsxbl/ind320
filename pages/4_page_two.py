import streamlit as st
from modules.api import OpenMeteo, GeoPos
from modules.fetch import agg_month

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
        st.header('Weather Data')

        # instantiate and cache data
        self._api = OpenMeteo()
        self._loc = GeoPos()


    # --- PAGE CONTENTS ---
    def setup_contents(self):
        # get weather data
        self._df = self._api.get_weather_data(
            **self._loc('Oslo')
        )
        # aggregate data by month
        df = agg_month(self._df)

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