import streamlit as st
from modules.session import SessionState
from modules.db import Mongo
from modules.analysis import plot_STFT, plot_STL
from modules.header import Header

class NewA:
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
        Header(group_options='single')

        # instantiate mongo client
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

        st.header(f'Energy {st.session_state.column[:-5].capitalize()} Analysis for {scale}')
        
    def _setup_tabs(self):
        '''
        Method to setup tabs for the page. One tab for STL analysis,
        another for Spectrogram
        '''
        self.t1, self.t2 = st.tabs(['STL Analysis', 'Spectrogram'])

    def _setup_stl_ui(self):
        '''
        Method to setup STL tab UI elements. the period default is dynamic,
        and defaults to a quarter of the data scale - if data length is one year
        default is 24 * 7 * 4, if data length is one month default is 24.
        '''
        if st.session_state.timescale == 'Yearly':
            default_period = 24 * 7 * 4  # roughly a month
        else:
            default_period = 24  # daily


        with st.expander('STL Settings'):
            robust = st.checkbox('Robust', value=False)
            
            period = st.number_input(
                'Period, default = 24 * 7 * 4', min_value=1, value=default_period, step=1
            )
            seasonal = st.number_input(
                'Seasonal, default = 7', min_value=7, value=7, step=2
            )
           # compute trend min
            trend_min = int(1.5 * period / (1 - (1.5 / seasonal)))
            if trend_min % 2 == 0:
                trend_min += 1  # make it odd
            
            trend = st.number_input(
                'Trend, default = odd int > 1.5 * period / (1 - (1.5 / seasonal))',
                min_value=trend_min, value=trend_min, step=2
            )

        self._stl_kwargs = {
            'period': period,
            'robust': robust,
            'seasonal': seasonal,
            'trend': trend
        }

    def _setup_stft_ui(self):
        '''
        Method to setup STFT tab UI elements
        '''
        with st.expander('STFT Settings'):
            self._nperseg = st.number_input(
                'Number of Samples per Segment', min_value=1, value=31, step=1
            )
            self._noverlap = st.number_input(
                'Number of Overlapping Samples', min_value=0, value=30, step=1
            )
    
    def _plot_stl(self):
        '''
        Method to plot STL analysis using cached data
        '''
        if not st.session_state.group:
            st.warning('Please select at least one production group to plot STL analysis.')
            return
        
        fig = plot_STL(
            self._df,
            st.session_state.area,
            st.session_state.group[0],
            **self._stl_kwargs
        )

        st.plotly_chart(fig)

    def _plot_stft(self):
        '''
        Method to plot STFT spectrogram using cached data
        '''
        if not st.session_state.group:
            st.warning('Please select at least one production group to plot STFT spectrogram.')
            return
        
        fig = plot_STFT(
            self._df,
            st.session_state.area,
            st.session_state.group[0],
            nperseg=self._nperseg,
            noverlap=self._noverlap
        )
        st.plotly_chart(fig)

    # --- PAGE CONTENTS ---
    def setup_contents(self):
        '''
        Method to setup page contents inside tabs
        '''
        with self.t1:
            self._setup_stl_ui()
            self._plot_stl()


        with self.t2:
            self._setup_stft_ui()
            self._plot_stft()

    def run(self):
        try:
            self._load_data()
            self._setup_heading()
            self._setup_tabs()
            self.setup_contents()
        except Exception as e:
            st.warning(f"An error occurred while rendering the page: {e}")

if __name__ == '__main__':
    main = NewA()
    main.run()