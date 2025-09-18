"""Module to handle data fetching functions"""
import streamlit as st
import pandas as pd

@st.cache_data
def csv_data(path:str, **kwargs):
    '''This function should cache the data in streamlit'''
    return pd.read_csv(path, **kwargs)

@st.cache_data
def agg_first_month(df:pd.DataFrame):
    minyear = df.index.year.min()
    minmonth = df.loc[f"{minyear}"].index.month.min()
    df = df.loc[f"{minyear}-{minmonth:02d}"]
    df = df.groupby(df.index.month).agg(list)
    return df