import streamlit as st
from modules.fetch import csv_data, agg_first_month

class Main:
    def __init__(self):
        st.set_page_config(layout='wide')
        st.header('Dummypage 2')


    # --- PAGE CONTENTS ---
    def setup_contents(self):
        # get the data, use custom function with caching
        df = csv_data('data/open-meteo-subset.csv', index_col=0, parse_dates=['time'])

        # aggreagte the first month
        df = agg_first_month(df)

        # # set configuration for linecharts within Dataframe
        col_config = {
            col : st.column_config.LineChartColumn(col)
            for col in df.columns
            }
        
        # render dataframe to frontend
        st.dataframe(df, column_config=col_config)
        
    def run(self):
        self.setup_contents()

if __name__ == '__main__':
    main = Main()
    main.run()