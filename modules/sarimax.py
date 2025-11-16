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

    def fit(self, order=(1, 1, 1), seasonal_order=(0, 0, 0, 0)):
        '''Fit the SARIMAX model to the data'''
        self._model = SARIMAX(self._data, order=order,
                              seasonal_order=seasonal_order,
                              exog=self._exog)
        
        self._results = self._model.fit(disp=False)
        self._summary = self._results.summary()

    def forecast(self, start):
        '''Generate forecast from the fitted model'''
        if self._results is None:
            raise ValueError("Model must be fitted before forecasting.")
        
        pred_1 = self._results.get_prediction()
        pred_ci = pred_1.conf_int()
        pred_d = self._results.get_prediction(start=start, dynamic=True)
        pred_d_ci = pred_d.conf_int()

        return pred_1, pred_ci, pred_d, pred_d_ci
    
    @property
    def summary(self):
        '''Return the summary of the fitted model'''
        if self._results is None:
            raise ValueError("Model must be fitted before getting summary.")
        return self._summary