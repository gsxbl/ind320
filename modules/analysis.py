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
    # Handle NaNs by interpolating
    clean_data = data.interpolate(
        method='linear').fillna(method='bfill').fillna(method='ffill')
    
    # Perform DCT with orthonormal normalization
    f = np.arange(0, clean_data.shape[0])
    dct_res = dct(clean_data, type=1, norm='ortho')
    dct_res[f < cutoff_freq] = 0
    # Perform inverse DCT with matching normalization
    return idct(dct_res, type=1, norm='ortho')

@st.cache_data
def plot_SPC(data, key: str, **kwargs):
    # filtered signals
    highpass = highpass_filter(data[key], cutoff_freq=kwargs.get('cutoff_freq', 30))
    lowpass = data[key] - highpass

    # robust statistics and outlier detection on highpass (SATV)
    m = stats.trim_mean(highpass, kwargs.get('proportioncut', 0.05))
    s = stats.median_abs_deviation(highpass)
    n = kwargs.get('k', 3)
    
    # Thresholds in temperature space: centered at lowpass + m (seasonal trend + offset)
    boundary_upper = lowpass + m + n * s
    boundary_lower = lowpass + m - n * s
    
    # Detect outliers where highpass exceeds bounds
    outliers = np.where(np.abs(highpass - m) > n * s, data[key], np.nan)

     # instantiate figure
    fig = go.Figure()
    boundary = dict(dash='dash', width=0.5, color='grey')

    # plot the original signal
    fig.add_trace(go.Scatter(
        x=data.index, y=data[key],
        mode='lines', name='Original Signal'))

    # plot the outliers with yellow color for outliers
    fig.add_trace(go.Scatter(
        x=data.index, y=outliers,
        mode='lines', name='Outliers', line=dict(color='yellow')))

    # add confidence intervals with dashed lines
    fig.add_trace(go.Scatter(
        x=data.index, y=boundary_upper,
        mode='lines', name='Upper Bound',
        line=boundary))

    fig.add_trace(go.Scatter(
        x=data.index, y=boundary_lower,
        mode='lines', name='Lower Bound',
        line=boundary, fill='tonexty', fillcolor='rgba(255,0,0,0.05)'))

    # plot seasonal trend
    fig.add_trace(go.Scatter(x=data.index, y=lowpass,
                            mode='lines', name='Seasonal Trend'))

    fig.update_layout(title=f'{key} over Time with outliers',
                    xaxis_title='Date',
                    yaxis_title=key)

    return fig, pd.Series(outliers, index=data.index).dropna()

# plot precipitation as function of time with Local Outlier Factor
@st.cache_data
def plot_LOF(data, key:str, **kwargs):
    '''Plot LOF anomalies.
    kwargs:
    contamination: float, optional
        The amount of contamination of the data set, i.e. the proportion of
        outliers in the data set. Used when fitting to define the threshold
        on the decision function. Default is 0.01.
    n_neighbors: int, optional
        Number of neighbors to use by default for k-neighbors queries. Default is 20.
    Returns:
        plotly.graph_objects.Figure, pd.Series
        A plotly figure showing the data with detected anomalies highlighted,
        and
        A series containing the detected outliers.

    '''
    # apply Local Outlier Factor
    lof = LocalOutlierFactor(
        n_neighbors=kwargs.get('n_neighbors', 20),
        contamination=kwargs.get('contamination', 0.01))
    outlier_labels = lof.fit_predict(data[[key]].copy())
    outliers = np.where(outlier_labels == -1, data[key], np.nan)

    # instantiate figure
    fig = go.Figure()

    # plot the original signal
    fig.add_trace(go.Scatter(
        x=data.index, y=data[key],
        mode='lines', name=key))

    # plot the outliers with red color for outliers
    fig.add_trace(go.Scatter(
        x=data.index, y=outliers,
        mode='markers', name='Anomalies', marker=dict(color='red', size=6)))

    fig.update_layout(title=f'{key} over Time with LOF anomalies',
                      xaxis_title='Date',
                      yaxis_title=key)

    return fig, pd.Series(outliers, index=data.index).dropna()

# apply STL decomposition
@st.cache_data
def plot_STL(data, area, group, **kwargs):
    '''
    Defaults:
    period=24*7*4, robust=False, seasonal=7,
    trend=If not provided uses the smallest odd
    integer greater than 1.5 * period / (1 - (1.5 / seasonal))
    '''
    # reorganize the dataframe
    data = data.copy().reset_index().set_index(
        ['priceArea', st.session_state.column, 'startTime']
        ).sort_index()
    
    stl = STL(
        data.loc[area, group]['quantityKwh'], **kwargs)
    result = stl.fit()

    fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
                        subplot_titles=("Observed and Trend", "Seasonal", "Residual"))
    
    fig.add_trace(go.Scatter(x=result.observed.index, y=result.observed,
                            mode='lines', name='Observed'), row=1, col=1)
    fig.add_trace(go.Scatter(x=result.trend.index, y=result.trend,
                            mode='lines', name='Trend', line=dict(color='red')), row=1, col=1)
    
    fig.add_trace(go.Scatter(x=result.seasonal.index, y=result.seasonal,
                            mode='lines', name='Seasonal', line=dict(color='magenta')), row=2, col=1)
    
    fig.add_trace(go.Scatter(x=result.resid.index, y=result.resid,
                            mode='lines', name='Residual', line=dict(color='yellow')), row=3, col=1)
    
    # make plot taller
    fig.update_xaxes(showgrid=True, matches='x')
    fig.update_layout(height=700)
    
    return fig

# plot the STFT spectrogram
@st.cache_data
def plot_STFT(data, area, group, **kwargs):
    db = kwargs.get('db', False)

    f, t, Zxx = stft(
        data.loc[area, group]['quantityKwh'],
        fs=1,
        window='hann',
        nperseg=kwargs.get('nperseg', 31),
        noverlap=kwargs.get('noverlap', 30),
        boundary=None)
    
    # if dB: convert Zxx to dB scale
    if db:
        Zxx = 20 * np.log10(np.abs(Zxx) + 1e-10)
    else:
        Zxx = np.abs(Zxx)

    fig = go.Figure(data=go.Heatmap(
        z=Zxx,
        x=t / 24,  # convert to days
        y=f,
        colorscale='Viridis'))

    fig.update_layout(
        title=f'STFT Spectrogram for {area} - {group}',
        xaxis_title='Time [days]',
        yaxis_title='Frequency [cycles per hour]',
    )
    
    return fig