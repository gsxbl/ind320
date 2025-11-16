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
        self._state = SessionState()
        with st.spinner('Loading...'):
            Header()

        # instantiate client
        self._db = Mongo()

    def _load_data(self):
        '''
        Load data from MongoDB based on session state.
        '''
        self._df = self._db.get_data(
            **self._state.kwargs,
            index=['priceArea', st.session_state.column, 'startTime']
        )

    def _setup_heading(self):
        '''
        Method to setup page heading
        '''
        if st.session_state.timescale == 'Monthly':
            scale = st.session_state.month
        elif st.session_state.timescale == 'Annual':
            scale = st.session_state.year
        else:
            scale = f"{st.session_state.start_time.date()} to {st.session_state.end_time.date()}"

        st.header(f'Energy {st.session_state.column[:-5].capitalize()} Charts for {scale}')

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
        df = df.groupby(st.session_state.column).agg('sum')

        fig = go.Figure()

        fig.add_trace(go.Pie(
            labels=df.index,
            values=df['quantityKwh'] / 1e9, # TWh
            rotation=180,
            )
        )

        st.plotly_chart(fig)

    def _line_plot(self):
        '''
        Method to iterate all frontend selected pills
        and adds their contents to a plotly graph object.
        Method renders the figure to frontend using cached data.
        '''
        if not st.session_state.group:
            st.warning('Please select at least one {} group to plot line chart.'.format(
                st.session_state.column[:-5].capitalize()))
            return
        # instantiate figure
        fig = go.Figure()
        
        # S = st.session_state.timescale[0]
        # scale = st.session_state.month if S == 'M' else st.session_state.year
        
        # iterate groups and add traces
        for group in st.session_state.group:
    
            # Filter from cached full dataframe by area, group, and month
            df = self._df.loc[(st.session_state.area, group)]
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
            yaxis=dict(
                title=f'{st.session_state.column[:-5]} [MWh]'
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
        self._setup_heading()
        self._load_data()
        self._setup_contents()



if __name__ == '__main__':
    try:
        main = Page4()
        main.run()
    except Exception as e:
        st.error(f"An error occurred: {e}")