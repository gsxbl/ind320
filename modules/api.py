"""Module to handle API requests with caching."""
import openmeteo_requests
import pandas as pd
import requests
import streamlit as st

class OpenMeteo:
    """Client for Open-Meteo weather API with Streamlit caching."""
    
    def __init__(self):
        self._client = self._setup_client()
    
    @st.cache_resource
    def _setup_client(_self):
        """Initialize Open-Meteo client with session for connection pooling."""
        session = requests.Session()
        return openmeteo_requests.Client(session=session)
    
    @st.cache_data(show_spinner=False)
    def get_weather_data(_self, **kwargs):
        """
        Fetch weather data from Open-Meteo API.
        
        Args:
            latitude (float): Default 52.52 (Bergen)
            longitude (float): Default 13.41 (Bergen)
            hourly (list): Variables to fetch
            start_date (str): Start date (YYYY-MM-DD)
            end_date (str): End date (YYYY-MM-DD)
            models (str): Weather model (default 'era5')
            wind_speed_unit (str): Wind speed unit (default 'ms')
        
        Returns:
            pd.DataFrame: Weather data with date index
        """
        # Base URL
        url = "https://archive-api.open-meteo.com/v1/archive"
        
        # set default parameters if not provided
        kwargs['latitude'] = kwargs.get('latitude', 52.52)
        kwargs['longitude'] = kwargs.get('longitude', 13.41)
        kwargs['hourly'] = ["temperature_2m", "precipitation", "wind_speed_10m",
                            "wind_gusts_10m", "wind_direction_10m"]
        kwargs['start_date'] = kwargs.get('start_date', '2021-01-01')
        kwargs['end_date'] = kwargs.get('end_date', '2021-12-31')
        kwargs['models'] = kwargs.get('models', 'era5')
        kwargs['wind_speed_unit'] = kwargs.get('wind_speed_unit', 'ms')
        
        # Make API call
        response = _self._client.weather_api(url, params=kwargs)[0].Hourly()
        
        # Build date range
        data = {
            "date": pd.date_range(
                start=pd.to_datetime(response.Time(), unit="s"),
                end=pd.to_datetime(response.TimeEnd(), unit="s"),
                freq=pd.Timedelta(seconds=response.Interval()),
                inclusive="left"
            )
        }
        
        # Populate data for each hourly variable
        for i, kind in enumerate(kwargs.get("hourly", [])):
            data[kind] = response.Variables(i).ValuesAsNumpy()
        
        return pd.DataFrame(data).set_index('date')
