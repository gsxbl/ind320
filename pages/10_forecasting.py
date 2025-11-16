'''This page will implement forecasting functionalities.'''
import streamlit as st
import numpy as np
import plotly.graph_objects as go

from statsmodels.tsa.statespace.sarimax import SARIMAX

from modules.api import OpenMeteo
from modules.db import Mongo
from modules.header import Header
from modules.session import SessionState
from modules.sarimax import SarimaxModel

class Forecast:
    def __init__(self):
        # general setup
        st.set_page_config(layout='wide')
        self._state = SessionState()
        Header()

        self._api = OpenMeteo()
        self._db = Mongo()

        self._sarimax = SarimaxModel(data=None)

    def _get_energy_data(self):
        '''get data from mongodb'''
        self._df_e = self._db.get_data(
            **self._state.kwargs,
            index=['priceArea', st.session_state.column, 'startTime']
        )

    def _get_weather_data(self):
        '''get data from openmeteo api'''
        self._df_w = self._api.get_weather_data(
            **st.session_state.geo,
            start_date=st.session_state.start_time,
            end_date=st.session_state.end_time,
            timescale=st.session_state.timescale
        )
    
    def _slice_data(self):
        '''slice data for the selected area and group'''
        self._df_e = self._df_e.loc[
            st.session_state.area,
            st.session_state.group[4]
            ]['quantityKwh']
          
    ### DATA PREPARATION METHODS ###
    def _match_dataframe_indices(self):
        '''merge weather and energy dataframes on time index'''
        # get the shortest index range
        self._index = np.intersect1d(self._df_e.index, self._df_w.index)
        self._df_e = self._df_e.loc[self._index]
        self._df_w = self._df_w.loc[self._index]
    
    def _setup_containers(self):
        """Setup Streamlit containers for layout."""
        with st.expander('Forecast Settings', expanded=False):
            self._c1, self._c2 = st.columns([3, 1])
            self._c3 = st.columns(6)
    
    def _setup_forecast_settings(self):
        '''setup forecast settings'''
        with self._c1:
            self._mid = len(self._df_e)//2
            opt = st.select_slider(
                'Select forecast starting point',
                options=self._df_e.index,
                value=self._df_e.index[self._mid]
            )
        with self._c2:

            # find index of opt
            self._mid = self._df_e.index.get_loc(opt)

            st.session_state.forecast_start = str(opt)

            st.session_state.forecast_horizon = st.number_input(
                'Forecast Horizon (in number of periods)', min_value=1, max_value=365, value=12, step=1
            )

        with self._c3[0]:
            st.number_input(
                'AR Order (p)', min_value=0, max_value=5, value=1, step=1, key='ar_order'
            )
        with self._c3[1]:
            st.number_input(
                'Differencing Order (d)', min_value=0, max_value=2, value=1, step=1, key='diff_order'
            )
        with self._c3[2]:
            st.number_input(
                'MA Order (q)', min_value=0, max_value=5, value=1, step=1, key='ma_order'
            )
        with self._c3[3]:
            st.number_input(
                'Seasonal AR Order (P)', min_value=0, max_value=2, value=1, step=1, key='sar_order'
            )
        with self._c3[4]:
            st.number_input(
                'Seasonal Differencing Order (D)', min_value=0, max_value=1, value=1, step=1, key='sdiff_order'
            )
        with self._c3[5]:
            st.number_input(
                'Seasonal MA Order (Q)', min_value=0, max_value=2, value=1, step=1, key='sma_order'
            )

    def _add_data(self):
        '''add exogenous data to sarimax model'''
        self._sarimax.add_data(self._df_e)
        self._sarimax.add_exogenous(self._df_w)

    def _fit_sarimax_model(self):
        '''fit SARIMAX model'''
        self._sarimax.fit(order=(1, 1, 1), seasonal_order=(1, 1, 1, 12))

    def _train_sarimax_model(self):
        '''train SARIMAX model'''
        p1, p_ci, p_d, p_d_ci = self._sarimax.forecast(
            start=st.session_state.forecast_start)
        
        # assign predictions and confidence intervals
        self._pred_1, self._pred_ci = p1, p_ci
        self._pred_d, self._pred_d_ci = p_d, p_d_ci
    
    def _setup_figure(self):
        self._fig = go.Figure()

        # Observed series
        self._fig.add_trace(go.Scatter(
            x=self._df_e.index,
            y=self._df_e.values,
            name="Observed",
            mode="lines",
            line=dict(color="blue")
        ))

    def _add_onestep_trace(self):
        '''add forecast traces to figure'''
        # One-step forecast
        forecast_idx = self._pred_1.predicted_mean.index
        forecast_vals = self._pred_1.predicted_mean.values
        ci = self._pred_1.conf_int()

        # One-step CI band
        self._fig.add_trace(go.Scatter(
            x=list(ci.index) + list(ci.index[::-1]),
            y=list(ci.iloc[:, 1]) + list(ci.iloc[:, 0][::-1]),
            fill="toself",
            fillcolor="rgba(255,0,0,0.15)",
            line=dict(color="rgba(255,0,0,0)"),
            hoverinfo="skip",
            showlegend=False
        ))

        self._fig.add_trace(go.Scatter(
            x=forecast_idx,
            y=forecast_vals,
            name="One-step forecast",
            mode="lines",
            line=dict(color="red")
        ))

    def _add_dynamic_trace(self):
        # Dynamic forecast
        dyn_idx = self._pred_d.predicted_mean.index
        dyn_vals = self._pred_d.predicted_mean.values
        ci_dyn = self._pred_d.conf_int()

        # Dynamic CI band
        self._fig.add_trace(go.Scatter(
            x=list(ci_dyn.index) + list(ci_dyn.index[::-1]),
            y=list(ci_dyn.iloc[:, 1]) + list(ci_dyn.iloc[:, 0][::-1]),
            fill="toself",
            fillcolor="rgba(0,128,0,0.15)",
            line=dict(color="rgba(0,128,0,0)"),
            hoverinfo="skip",
            showlegend=False
        ))

        self._fig.add_trace(go.Scatter(
            x=dyn_idx,
            y=dyn_vals,
            name="Dynamic forecast",
            mode="lines",
            line=dict(color="green")
        ))

    def _update_layout(self):
        self._fig.update_layout(
            xaxis_title="Date",
            yaxis_title="kWh",
            template="plotly_white",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            height=800,
        )

        self._fig.update_xaxes(
            range=[self._df_e.index[self._mid-24], self._df_e.index[self._mid + st.session_state.forecast_horizon + 24]],
            rangeslider_visible=True)
        
        self._fig.update_yaxes(
            range=[
                min(self._df_e.min(), self._pred_1.predicted_mean.min()) * 0.9,
                max(self._df_e.max(), self._pred_1.predicted_mean.max()) * 1.1
            ],
            fixedrange=False,
            rangemode="tozero")

        st.plotly_chart(self._fig)
    
    def _summary(self):
        '''display model summary'''
        with st.expander('Model Summary', expanded=False):
            st.text(self._sarimax.summary.as_text())

    def run(self):
        ### load and prepare data
        self._get_energy_data()
        self._get_weather_data()
        self._slice_data()
        self._match_dataframe_indices()

        ### setup and train model
        self._setup_containers()
        self._setup_forecast_settings()
        self._add_data()
        with st.spinner('Fitting SARIMAX model...'):
            self._fit_sarimax_model()
            self._train_sarimax_model()
        
        ### setup and display figure
        self._setup_figure()
        self._add_onestep_trace()
        self._add_dynamic_trace()
        self._update_layout()
        
        ### display model summary
        self._summary()

        ### DEBUG
        # self._df_e

if __name__ == '__main__':
    main = Forecast()
    main.run()