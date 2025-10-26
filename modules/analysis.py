'''Module for data analysis functions.'''
import streamlit as st
import numpy as np
import pandas as pd

from scipy.signal import stft
from scipy.fft import dct, idct
import scipy.stats as stats

from sklearn.neighbors import LocalOutlierFactor
from statsmodels.tsa.seasonal import STL

import plotly.graph_objects as go
from plotly.subplots import make_subplots

def highpass_filter(data, cutoff_freq):
    # Perform DCT
    f = np.arange(0, data.shape[0])
    dct_res = dct(data, type=1, norm='forward')
    dct_res[f < cutoff_freq] = 0
    # Perform inverse DCT
    return idct(dct_res, type=1, norm='forward')

def plot_robust(data, key:str, **kwargs):
    # filtered signals
    highpass = highpass_filter(data[key], cutoff_freq=kwargs.get('cutoff_freq', 30))
    lowpass = data[key] - highpass

    # robust statistics and outlier detection
    m = stats.trim_mean(highpass, kwargs.get('proportioncut', 0.05))
    s = stats.median_abs_deviation(highpass)
    n = kwargs.get('k', 3)
    # print(f"Robust mean: {m}, Robust std: {s}")
    outliers = np.where(np.abs(highpass - m) > n * s, data[key], np.nan)

    # instantiate figure
    fig = go.Figure()
    boundary = dict(dash='dash', width=0.5, color='grey')

    # plot the original signal
    fig.add_trace(go.Scatter(
        x=data['date'], y=data[key],
        mode='lines', name='Original Signal'))

    # plot the outliers with yellow color for outliers
    fig.add_trace(go.Scatter(
        x=data['date'], y=outliers,
        mode='lines', name='Outliers', line=dict(color='yellow')))

    # add confidence intervals with dashed lines
    fig.add_trace(go.Scatter(
        x=data['date'], y=lowpass - m + n*s,
        mode='lines', name='Lower Bound',
        line=boundary))

    fig.add_trace(go.Scatter(
        x=data['date'], y=lowpass - m - n*s,
        mode='lines', name='Upper Bound',
        line=boundary, fill='tonexty', fillcolor='rgba(255,0,0,0.05)'))

    # plot seasonal trend
    fig.add_trace(go.Scatter(x=data['date'], y=lowpass,
                            mode='lines', name='Seasonal Trend'))

    fig.update_layout(title=f'{key} over Time with outliers',
                    xaxis_title='Date',
                    yaxis_title=key)

    return fig, pd.Series(outliers, index=data['date']).dropna()

# plot precipitation as function of time with Local Outlier Factor
def plot_LOF(data, key:str, **kwargs):
    # apply Local Outlier Factor
    lof = LocalOutlierFactor(
        n_neighbors=40,
        contamination=kwargs.get('contamination', 0.01))
    outlier_labels = lof.fit_predict(data[[key]].copy())
    outliers = np.where(outlier_labels == -1, data[key], np.nan)

    # instantiate figure
    fig = go.Figure()

    # plot the original signal
    fig.add_trace(go.Scatter(
        x=data['date'], y=data[key],
        mode='lines', name=key))

    # plot the outliers with red color for outliers
    fig.add_trace(go.Scatter(
        x=data['date'], y=outliers,
        mode='markers', name='Anomalies', marker=dict(color='red', size=6)))

    fig.update_layout(title=f'{key} over Time with LOF anomalies',
                      xaxis_title='Date',
                      yaxis_title=key)

    return fig, pd.Series(outliers, index=data['date']).dropna()

# apply STL decomposition
@st.cache_data
def plot_STL(data, area, group, **kwargs):
    '''
    Defaults:
    period=24*15, robust=False, seasonal=7,
    trend=If not provided uses the smallest odd
    integer greater than 1.5 * period / (1 - 1.5 / seasonal)
    '''
    # reorganize the dataframe
    data = data.copy().reset_index().set_index(
        ['priceArea', 'productionGroup', 'startTime']
        ).sort_index()
    
    stl = STL(
        data.loc[area, group]['quantityKwh'], **kwargs)
    result = stl.fit()

    fig = make_subplots(rows=4, cols=1, shared_xaxes=True,
                        subplot_titles=("Observed", "Trend", "Seasonal", "Residual"))
    fig.add_trace(go.Scatter(x=result.observed.index, y=result.observed,
                            mode='lines', name='Observed'), row=1, col=1)
    fig.add_trace(go.Scatter(x=result.trend.index, y=result.trend,
                            mode='lines', name='Trend'), row=2, col=1)
    fig.add_trace(go.Scatter(x=result.seasonal.index, y=result.seasonal,
                            mode='lines', name='Seasonal'), row=3, col=1)
    fig.add_trace(go.Scatter(x=result.resid.index, y=result.resid,
                            mode='lines', name='Residual'), row=4, col=1)
    
        # make plot taller
    fig.update_layout(height=700)
    
    return fig

# plot the STFT spectrogram
@st.cache_data
def plot_STFT(data, area, group, **kwargs):
    f, t, Zxx = stft(
        data.loc[area, group]['quantityKwh'],
        fs=1,
        window='hann',
        nperseg=kwargs.get('nperseg', 256),
        noverlap=kwargs.get('noverlap', 128),
        boundary=None)

    fig = go.Figure(data=go.Heatmap(
        z=np.abs(Zxx),
        x=t / 24,
        y=f,
        colorscale='Viridis'))

    fig.update_layout(
        title=f'STFT Spectrogram for {area} - {group}',
        xaxis_title='Time [days]',
        yaxis_title='Frequency [cycles per day]')
    

    
    return fig