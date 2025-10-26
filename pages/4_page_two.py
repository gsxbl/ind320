import streamlit as st
from modules.fetch import csv_data, agg_first_month

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
        st.header('Weather (dummy)Data ')

        # instantiate and cache data
        self._df = csv_data('data/open-meteo-subset.csv',
                            index_col=0, parse_dates=['time'])

    # --- PAGE CONTENTS ---
    def setup_contents(self):
        # aggreagte the first month
        df = agg_first_month(self._df)

        # # set configuration for linecharts within Dataframe
        for col in df.columns:
            col_cfg = st.column_config.LineChartColumn(col)
            
            # render to frontend
            st.dataframe(df[col], column_config={col:col_cfg})
        
    def run(self):
        self.setup_contents()

if __name__ == '__main__':
    main = Page2()
    main.run()