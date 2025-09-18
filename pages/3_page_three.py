import streamlit as st
import plotly.graph_objects as go

from modules.fetch import csv_data

class Page3:
    def __init__(self):
        st.set_page_config(layout='wide')
        st.header('Dummypage 3')

        self._df = csv_data(
            'data/open-meteo-subset.csv', index_col=0,
            parse_dates=['time'])
        
        self._get_months()
    
    def _get_months(self):
        months = self._df.index.to_period("M")
        self._months = months.sort_values().unique()
        
        
    def plot(self):
        if not isinstance(self._column, list):
            self._column = list(self._column)

        fig = go.Figure()
        for col in self._column:
            fig.add_trace(
                go.Scatter(
                    x=self._df.index,
                    y=self._df[col],
                    name=col, yaxis="y1"))
            
            fig.update_layout(
                title=f'Timeseries of Weather data',
                yaxis=dict(
                    title=f'Measured Unit Value'
                )
            )
        st.plotly_chart(fig)

    def slice_data(self):
        start, stop = self._slice
        self._df = self._df[
            (self._df.index.to_period("M")>= start) &
            (self._df.index.to_period("M") <= stop)
            ]

    # --- PAGE CONTENTS ---
    def setup_contents(self):
        self._column = st.multiselect('Columns', self._df.columns)
        self._slice = st.select_slider(
            "Select time range",
            options=self._months,
            value=(self._months[0], self._months[-1])
        )
        
        
    def run(self):
        self.setup_contents()
        self.slice_data()
        self.plot()

if __name__ == '__main__':
    main = Page3()
    main.run()