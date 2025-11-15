'''Module to handle Sliding Windo Average with lag'''
from operator import index
import streamlit as st
import numpy as np

import plotly.graph_objects as go
from plotly.subplots import make_subplots


from modules.api import OpenMeteo
from modules.db import Mongo
from modules.header import Header
from modules.session import SessionState


class SlidingWindow:
    def __init__(self):
        self._state = SessionState()
        Header()

        self._api = OpenMeteo()
        self._db = Mongo()

    def _get_wather_data(self):
        '''get data from openmeteo api'''
        self._df_w = self._api.get_weather_data(
            **st.session_state.geo,
            start_date=st.session_state.start_time,
            end_date=st.session_state.end_time,
            timescale=st.session_state.timescale
        )
    
    def _get_energy_data(self):
        '''get data from mongodb'''
        self._df_e = self._db.get_data(
            **self._state.kwargs,
            # index=['priceArea', st.session_state.column, 'startTime']
            index=['startTime']
        )

    def _setup_expander(self):
        '''setup expander for lag selection'''
        self._exp = st.expander('Lag Selection', expanded=False)
    
    def _setup_columns(self):
        '''setup columns for x and y axis'''
        with self._exp:
            self._c1, self._c2 = st.columns(2)

    def _setup_lag_ui(self):
        '''set up a single slider to select lag value'''
        with self._c1:
            self._lag = st.slider('Select lag', 0, 10, 0)

    def _setup_sliding_window(self):
        '''setup sliding window size slider'''
        with self._c2:
            self._window_size = st.slider('Select Sliding Window Size', 1, 200, 5)

    def _setup_kind_ui(self):
        '''setup selevtor for kind of weather data'''
        with self._exp:
            self._kind = st.radio(
                'Select Weather Data Type',
                options=self._df_w.columns.tolist(),
                horizontal=True
            )
    def _match_dataframe_indices(self):
        '''merge weather and energy dataframes on time index'''
        # get the shortest index range
        self._index = np.intersect1d(self._df_e.index, self._df_w.index)
        self._df_e = self._df_e.loc[self._index]
        self._df_w = self._df_w.loc[self._index]

    def _setup_x_y(self):
        '''aggregate weather data by selected kind'''
        self._x = self._df_w[st.session_state.kind]
        
        self._df = self._df_e.groupby(
            'startTime')[
                'quantityKwh'].sum().to_frame(name='quantityKwh')

        # add column to self._df
        self._df[st.session_state.kind] = self._x

        self._y = self._df['quantityKwh']

        self._unit = self._x.index[1] - self._x.index[0]

    def _lagged_correlation(self):
        '''copute the lagged correlation'''
        self._x.index += self._unit * self._lag
        self._corr = np.corrcoef(self._y[self._lag:], self._x[0:len(self._y)-self._lag])

    def _rolling_window(self):
        '''setup the rolling window'''
        self._rolling = self._df[st.session_state.kind].rolling(
            window=self._window_size, center=True
            ).corr(self._df['quantityKwh'])


    def _plot(self):
        '''plot the lagged correlation'''
        fig = make_subplots(
            rows=3, cols=1, shared_xaxes=True)

        fig.add_trace(
            go.Scatter(
                x=self._index, y=self._x,
                mode='lines', name=st.session_state.kind),
            row=1, col=1
            )
        fig.add_trace(
            go.Scatter(
                x=self._index, y=self._y,
                mode='lines', name=st.session_state.column[:-5].capitalize()),
            row=2, col=1
            )
        
        fig.add_trace(
            go.Scatter(
                x=self._index, y=self._rolling,
                mode='lines', name='Rolling Correlation'),
            row=3, col=1
            )
        
        fig.update_layout(
            height=800,
            title_text="Sliding Window Correlation with Lag",
        )

        st.plotly_chart(fig, width='stretch')

    def run(self):
        # load data
        self._get_wather_data()
        self._get_energy_data()
        self._match_dataframe_indices()
        
        # preprocess
        self._setup_expander()
        self._setup_kind_ui()
        self._setup_columns()
        self._setup_lag_ui()
        self._setup_sliding_window()
        self._setup_x_y()

        # correlation
        self._rolling_window()
        self._lagged_correlation()

        # plot
        self._plot()
        
        # debug

if __name__ == '__main__':
    main = SlidingWindow()
    main.run()  