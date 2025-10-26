import streamlit as st
from modules.session import SessionState
from modules.db import Mongo
from modules.analysis import plot_STFT, plot_STL

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
        SessionState()

        st.markdown('''
                - Add necessary UI elements and plots to both
            ''')
        # instantiate and cache data
        self._db = Mongo()
        
        # fetch data from db
        self._df = self._db.get_full_data()
        self._set_multiindex()

    def _get_groups(self):
        '''
        Method to get available productionGroups for
        frontend pills selector
        '''
        self._groups = self._df.index.get_level_values('productionGroup').unique()

    def _set_multiindex(self):
        '''
        Method to set multiindex for the dataframe
        '''
        self._df = self._df.reset_index().set_index(
            ['priceArea', 'productionGroup', 'startTime']
            ).sort_index()

    def _setup_group_selector(self):
        '''
        Method to get pill button selections from
        frontend
        '''
        self._group = st.radio(
            '', self._groups,
            index=0,
            horizontal=True
        )

    def _setup_tabs(self):
        '''
        Method to setup tabs for the page. One tab for STL analysis,
        another for Spectrogram
        '''
        self.t1, self.t2 = st.tabs(['STL Analysis', 'Spectrogram'])

    def _setup_stl_ui(self):
        '''
        Method to setup STL tab UI elements
        '''
        with st.expander('STL Settings'):
            self._period = st.number_input(
                'Period', min_value=1, value=24*28, step=1
            )
            self._robust = st.checkbox('Robust', value=True)

    def _setup_stft_ui(self):
        '''
        Method to setup STFT tab UI elements
        '''
        with st.expander('STFT Settings'):
            self._nperseg = st.number_input(
                'Number of Samples per Segment', min_value=1, value=256, step=1
            )
            self._noverlap = st.number_input(
                'Number of Overlapping Samples', min_value=0, value=128, step=1
            )
    
    # --- PAGE CONTENTS ---
    def setup_contents(self):
        

        # 2DO : rewrite so that STL dosn't load everytime when viewing STFT tab
        with self.t1:
            self._setup_stl_ui()
            fig = plot_STL(self._df, st.session_state.area, self._group,
                            period=self._period, robust=self._robust)
            st.plotly_chart(fig)


        with self.t2:
            self._setup_stft_ui()
            fig = plot_STFT(self._df, st.session_state.area, self._group,
                             nperseg=self._nperseg, noverlap=self._noverlap)
            st.plotly_chart(fig)

    def run(self):
        st.header(f'Production analysis for {st.session_state.area}')
        self._get_groups()
        self._setup_group_selector()
        self._setup_tabs()
        self.setup_contents()

if __name__ == '__main__':
    main = NewA()
    main.run()