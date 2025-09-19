import streamlit as st
import plotly.graph_objects as go

from modules.fetch import csv_data

class Page3:
    '''
    This class represents the app page.
    
    Most page contents is rendered in the run method.
    Properties are used to mimic global variables,
    making them accessible to all methods.
    '''
    def __init__(self):
        # general page setup
        st.set_page_config(layout='wide')
        st.header('Dummypage 3')

        # instantiate and cache data
        self._df = csv_data(
            'data/open-meteo-subset.csv', index_col=0,
            parse_dates=['time'])
        
        # extract months
        self._get_months()
    
    def _get_months(self):
        '''
        This method extracts and sorts the available
        months in the dataset and creates the property
        self._months. Method is run once in the constructor.
        '''
        months = self._df.index.to_period("M")
        self._months = months.sort_values().unique()
        
        
    def plot(self):
        '''
        Method to iterate all frontend selected columns
        and adds their contents to a plotly graph object.
        Method renders the figure to frontend.
        '''
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
        self._column = st.multiselect('Columns', self._df.columns)
        self._slice = st.select_slider(
            "Select time range",
            options=self._months,
            value=(self._months[0], self._months[-1])
        )
        
        
    def run(self):
        '''Main runtime method'''
        self.setup_contents()
        self.slice_data()
        self.plot()

if __name__ == '__main__':
    main = Page3()
    main.run()