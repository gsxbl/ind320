import streamlit as st
import plotly.graph_objects as go

from modules.db import Mongo
from modules.session import SessionState
from modules.header import Header

class Page4:
    '''
    This class represents the app page.
    
    Most page contents is rendered in the run method.
    Properties are used to mimic global variables,
    making them accessible to all methods.
    '''
    def __init__(self):
        # general page setup
        st.set_page_config(layout='wide')
        
        # setup session state
        SessionState()
        Header()

        # instantiate client
        self._db = Mongo()
        
        # load dataframe from database
        self._load_df()


    def _load_df(self):
        '''
        Method to load dataframe from MongoDB based on session state month
        '''
        # split methods to preserve cache efficiency
        if st.session_state.timescale == 'Monthly':
            self._df = self._db.get_data(
                index=['priceArea', 'productionGroup', 'startTime'],
                timescale='Monthly',
                month=st.session_state.month
            )
        else:
            self._df = self._db.get_data(
                index=['priceArea', 'productionGroup', 'startTime'],
                timescale='Yearly',
                year=st.session_state.year
            )

    def _setup_columns(self):
        '''
        Method to split frontend and set size relation
        '''
        self._c1, self._c2 = st.columns((1,2))

    def _setup_doc(self):
        with st.expander('Data source:'):
            st.markdown(
                'Data has been extracted from [Elhub](https://api.elhub.no), and shows Energy production in Norway in 2021.' \
                '<br> iterate all months with<br>' \
                'curl -X GET "https://api.elhub.no/energy-data/v0/price-areas?dataset=CONSUMPTION_PER_GROUP_MBA_HOUR&startDate=2021-01-01',
                unsafe_allow_html=True
            )

    def _pie_chart(self):
        '''
        Method to filter cached data from database and
        render pie chart to frontend.
        '''
        # Filter from cached full dataframe by area and month
        df = self._df.loc[st.session_state.area]
        df = df.groupby('productionGroup').agg('sum')

        fig = go.Figure()

        fig.add_trace(go.Pie(
            labels=df.index,
            values=df['quantityKwh'] / 1e9, # TWh
            rotation=180,
            )
        )
        # dynamic title based on timescale
        if st.session_state.timescale == 'Monthly':
            fig.update_layout(
                title=f'Production in {st.session_state.area} [{st.session_state.month}] [%, TWh]')
        else:
            fig.update_layout(
                title=f'Production in {st.session_state.area} [{st.session_state.year}] [%, TWh]')

        st.plotly_chart(fig)

    def _line_plot(self):
        '''
        Method to iterate all frontend selected pills
        and adds their contents to a plotly graph object.
        Method renders the figure to frontend using cached data.
        '''
        # instantiate figure
        fig = go.Figure()
        
        S = st.session_state.timescale[0]
        scale = st.session_state.month if S == 'M' else st.session_state.year
        
        # iterate groups and add traces
        for group in st.session_state.group:

            # Filter from cached full dataframe by area, group, and month
            df = self._df.loc[(st.session_state.area, group)]
            df = df[df.index.to_period(S).astype(str) == scale]
            df.sort_index(inplace=True)

            # create trace
            trace = go.Scatter(
                x = df.index,
                y = df['quantityKwh'] / 1e3,
                name=f'{st.session_state.area} - {group}',
                opacity=0.5
            )
            fig.add_trace(trace)

        fig.update_layout(
            title=f'Production in {st.session_state.area} [{scale}] [MWh]',
            yaxis=dict(
                title='Production [MWh]'
            )
        )


        # render to frontend
        st.plotly_chart(fig)

    # --- PAGE CONTENTS ---
    def _setup_contents(self):
        '''
        Method to get setup all contents of the
        frontend. Split into two columns for
        different plots.
        Selection in left column slices the data
        in the right column.
        '''
        # Month selector at top (above charts)
        self._setup_columns()
        
        # left column/container
        with self._c1:
            self._pie_chart()
        
        # right column/container
        with self._c2:
            self._line_plot()
        
        self._setup_doc()

    def run(self):
        '''Main runtime method'''
        self._setup_contents()


if __name__ == '__main__':
    main = Page4()
    main.run()
