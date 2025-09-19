import streamlit as st
from modules.fetch import csv_data, agg_first_month

class Page2:
    def __init__(self):
        st.set_page_config(layout='wide')
        st.header('Dummypage 2')

        self._df = csv_data('data/open-meteo-subset.csv', index_col=0, parse_dates=['time'])

    # --- PAGE CONTENTS ---
    def setup_contents(self):
        # get the data, use custom function with caching

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