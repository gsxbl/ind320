'''module for SARIMAX forecasting calculations'''
import streamlit as st
from statsmodels.tsa.statespace.sarimax import SARIMAX


class SarimaxModel:
    '''Class to handle SARIMAX model fitting and forecasting'''
    def __init__(self, data):
        self._data = data
        self._exog = None
        
        self._model = None
        self._results = None


    def add_data(self, data):
        '''Add data to the SARIMAX model'''
        self._data = data
    
    def add_exogenous(self, exog):
        '''Add exogenous variables to the SARIMAX model'''
        self._exog = exog

    @st.cache_data
    def fit(_self, order=(1, 1, 1), seasonal_order=(0, 0, 0, 0)):
        '''Fit the SARIMAX model to the data'''
        _self._model = SARIMAX(_self._data, order=order, seasonal_order=seasonal_order)
        _self._results = _self._model.fit(disp=False)

    @st.cache_data
    def forecast(_self, start):
        '''Generate forecast from the fitted model'''
        if _self._results is None:
            raise ValueError("Model must be fitted before forecasting.")
        
        pred_1 =_self._results.get_prediction()
        pred_ci = pred_1.conf_int()
        pred_d = _self._results.get_prediction(start=start, dynamic=True)
        pred_d_ci = pred_d.conf_int()

        return pred_1, pred_ci, pred_d, pred_d_ci