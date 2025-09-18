import streamlit as st
import pandas as pd

st.set_page_config(layout='wide')

st.header('Dummypage 2')

df = pd.read_csv('data/open-meteo-subset.csv')
st.dataframe(df)