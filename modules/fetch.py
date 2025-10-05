"""Module to handle data fetching functions"""
import pymongo
import streamlit as st
import pandas as pd

### CSV / LOCAL DATA ###
@st.cache_data
def csv_data(path:str, **kwargs):
    '''This function should cache the data in streamlit'''
    return pd.read_csv(path, **kwargs)


### LINE CHART COLUMN HELPER ###
@st.cache_data
def agg_first_month(df:pd.DataFrame):
    minyear = df.index.year.min()
    minmonth = df.loc[f"{minyear}"].index.month.min()
    df = df.loc[f"{minyear}-{minmonth:02d}"]
    df = df.groupby(df.index.month).agg(list)
    return df


### MONGO DB ###
class Mongo:
    def __init__(self):
        self._setupMongoClient()
    
    @st.cache_resource
    def _setupMongoClient(self):
        self._client = pymongo.MongoClient(st.secrets["mongo"]["uri"])

    @st.cache_data(ttl=600)
    def find(self, **kwargs): 
        db = self._client[kwargs.get('db', 'ind320')]
        collection = db[kwargs.get('table', 'elhub')]

        query = kwargs.get('query', {})
        df = pd.DataFrame(list(collection.find(query)))
        df.drop(columns=['_id'], inplace=True)

        # if a multiindex is needed
        set_index = kwargs.get('index', None)
        if set_index:
            df = df.set_index(set_index)

        return df