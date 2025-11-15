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

    ### LOAD DATA METHODS ###
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

    ### SELECTOR METHODS ###
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
            i = self._window_size
            st.session_state.setdefault('lag', 0)
            st.session_state.lag = st.slider(
                'Select lag [steps]',
                min_value=-self._max_lag + i,
                max_value=self._max_lag - i,
                value=st.session_state.lag,
                step=1,
                key='lag_slider'
            )
            self._lag = st.session_state.lag

    def _setup_window_size(self):
        '''setup sliding window size slider'''
        hours = (st.session_state.end_time - st.session_state.start_time).total_seconds() // 3600
        self._hours = int(hours)
        with self._c2:
            self._window_size = st.slider(
                'Select Sliding Window Size [hours]', 1, self._hours, self._hours//8)

    def _setup_kind_ui(self):
        '''setup selevtor for kind of weather data'''
        with self._exp:
            self._kind = st.radio(
                'Select Weather Data Type',
                options=self._df_w.columns.tolist(),
                horizontal=True
            )
            st.session_state.kind = self._kind
    
    ### DATA PREPARATION METHODS ###
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

        self._max_lag = max(1, len(self._x) - 2)

    def _lagged_correlation(self):
        '''copute the lagged correlation'''
        self._x.index += self._unit * self._lag

        if self._lag > 0:
            self._corr = np.corrcoef(self._y[:-self._lag], self._x[self._lag:])
        elif self._lag < 0:
            self._corr = np.corrcoef(self._y[abs(self._lag):], self._x[0:len(self._y)-abs(self._lag)])
        else:
            self._corr = np.corrcoef(self._y[self._lag:], self._x[0:len(self._y)-self._lag])
        f"Crosscorrelation: {self._corr[0,1]:.3f}"


    def _rolling_window(self):
        '''setup the rolling window'''
        # convert datetime lag (Timedelta) to integer index shift
        freq_hours = self._unit.total_seconds() / 3600
        self._lag_steps = int(self._lag / freq_hours)

        lagged_weather = self._df[st.session_state.kind].shift(self._lag_steps)

        self._rolling = lagged_weather.rolling(
            window=self._window_size, center=True
            ).corr(self._df['quantityKwh'])

    ### PLOTTING METHODS ###
    def _setup_figure(self):
        '''plot the lagged correlation'''
        self._fig = make_subplots(
            rows=3, cols=1, shared_xaxes=True,
            row_titles=[
                st.session_state.kind.capitalize(),
                f"{st.session_state.column[:-5].capitalize()} (kWh)",
                "Rolling Correlation"
            ])

    def _add_traces(self):
        '''add traces to the figure'''
        # add the weather data
        self._fig.add_trace(
            go.Scatter(
                x=self._index, y=self._x,
                mode='lines', name=st.session_state.kind),
            row=1, col=1
            )
        
        # add the energy data
        self._fig.add_trace(
            go.Scatter(
                x=self._index, y=self._y,
                mode='lines', name=st.session_state.column[:-5].capitalize()),
            row=2, col=1
            )
        # add the rolling correlation
        self._fig.add_trace(
            go.Scatter(
                x=self._index, y=self._rolling,
                mode='lines', name='Rolling Correlation'),
            row=3, col=1
            )
        
        self._fig.update_layout(
            height=800,
            title_text=f'Sliding Window Correlation between '\
                 f'{st.session_state.kind} and {self._y.name} with lag {self._lag} timepoints'
        )

    def _setup_overlay_functions(self):
        '''add overlays to the figure'''
        self._overlay = lambda col, start, i: go.Scatter(
            x=self._df.loc[start-i:start+i].index,
            y=col.loc[start-i:start+i],
            mode="lines",
            line=dict(color="red", width=3),
            showlegend=False
        )

        self._marker = lambda col, start: go.Scatter(
            x=np.array([start]),
            y=np.array([col.loc[start]]),
            mode="markers",
            name="Center",
            marker=dict(color="red", size=15, symbol="star"),
            showlegend=True
        )

    def _add_overlays(self):
        '''render overlays on the figure'''
        options = self._rolling.dropna().index
        if options.empty:
            return

        start = st.session_state.get('center')
        if start not in options:
            start = options[0]

        i = (self._window_size // 2) * self._unit
        x, y = self._df[st.session_state.kind], self._df['quantityKwh']
        z = self._rolling

        off = (self._lag * self._unit)

        # add overlays to the figure
        self._fig.add_trace(self._overlay(x, start+off,i), row=1, col=1)
        self._fig.add_trace(self._overlay(y,start,i), row=2, col=1)
        self._fig.add_trace(self._marker(z,start), row=3, col=1)


    def _render_plot(self):
        '''render the plotly figure'''
        st.plotly_chart(self._fig, width='stretch')

    def _window_slider(self):
        '''slider to select center of sliding window'''
        options = self._rolling.dropna().index

        if options.empty:
            st.warning('No rolling correlation values to display.')
            return
        
        opts = list(options)
        mid_idx = len(opts) // 2

        # keep center aligned with available options
        if st.session_state.get('center') not in options:
            st.session_state.center = opts[mid_idx]

        with self._exp:
            st.select_slider(
                'Select center of sliding window',
                options=list(options),
                value=st.session_state.center,
                key='center'
            )


    def run(self):
        # load data
        self._get_wather_data()
        self._get_energy_data()
        self._match_dataframe_indices()
        
        # preprocess
        self._setup_expander()
        self._setup_kind_ui()
        self._setup_columns()
        self._setup_window_size()
        self._setup_x_y()
        self._setup_lag_ui()

        # correlation
        self._rolling_window()
        self._lagged_correlation()

        # slider (needs rolling data before plotting)
        self._window_slider()

        # plot
        self._setup_figure()
        self._add_traces()
        self._setup_overlay_functions()
        self._add_overlays()
        self._render_plot()
        # debug

if __name__ == '__main__':
    main = SlidingWindow()
    # try:
    #     main.run()  
    # except Exception as e:
    #     st.error(f"An error occurred: {e}. Reset settings and try again.")
    main.run()