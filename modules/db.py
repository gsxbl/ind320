"""Module to handle data fetching functions"""
import pymongo
import streamlit as st
import pandas as pd
from datetime import datetime

### MONGO DB ###
class Mongo:
    def __init__(self):
        self._client = self._setupMongoClient()
        
    
    @st.cache_resource
    def _setupMongoClient(_self):
        return pymongo.MongoClient(st.secrets["mongo"]["uri"])

    @st.cache_data(ttl=600)
    def find(_self, **kwargs):
        '''Generic find method to get data from database'''
        db = _self._client[kwargs.get('db', 'ind320')]
        collection = db[kwargs.get('table', 'elhub')]

        query = kwargs.get('query', {})
        df = pd.DataFrame(list(collection.find(query)))
        if '_id' in df.columns:
            df.drop(columns=['_id'], inplace=True)

        # if a multiindex is needed
        set_index = kwargs.get('index', None)
        if set_index:
            df = df.set_index(set_index)
        return df
    
    @st.cache_data(ttl=600)
    def get_data(_self, **kwargs):
        '''Generic method to get data from database,
        either by YYYY-MM or YYYY
        '''
        db = _self._client[kwargs.get('db', 'ind320')]
        collection = db[kwargs.get('table', 'elhub')]
        query = {}

        timescale = kwargs.get('timescale', 'Monthly')
        month = kwargs.get('month', '2021-01')
        year = kwargs.get('year', '2021')

        if timescale == 'Monthly':
            month = kwargs.get('month', month)
            year, month = map(int, month.split('-'))
            start = datetime(year, month, 1)
            if month == 12:
                next_month = datetime(year + 1, 1, 1)
            else:
                next_month = datetime(year, month + 1, 1)

            query = {
                'startTime': {
                    '$gte': start,
                    '$lt': next_month
                }
            }
        elif timescale == 'Yearly':
            year = int(kwargs.get('year', year))
            start = datetime(year, 1, 1)
            next_year = datetime(year + 1, 1, 1)

            query = {
                'startTime': {
                    '$gte': start,
                    '$lt': next_year
                }
            }
        return _self.find(query=query, **kwargs)
    
    @st.cache_data(ttl=600)
    def mean_by_area(_self, **kwargs):
        '''method to get mean quantityKwh grouped by priceArea and timescale'''
        db = _self._client[kwargs.get('db', 'ind320')]
        collection = db[kwargs.get('table', 'elhub')]
        
        timescale = kwargs.get('timescale', 'Monthly')
        month = kwargs.get('month', '2021-01')
        year = kwargs.get('year', '2021')

        # build date range query
        if timescale == 'Monthly':
            year, month = map(int, month.split('-'))
            start = datetime(year, month, 1)
            if month == 12:
                next_month = datetime(year + 1, 1, 1)
            else:
                next_month = datetime(year, month + 1, 1)
        elif timescale == 'Yearly':
            year = int(year)
            start = datetime(year, 1, 1)
            next_month = datetime(year + 1, 1, 1)
        
        pipeline = [
            {"$match": {
                "startTime": {
                    "$gte": start,
                    "$lt": next_month
                }
            }},
            {"$group": {
                "_id": "$priceArea",
                "mean": {"$avg": "$quantityKwh"}
            }},
            {"$project": {
                "_id": 0,
                "priceArea": "$_id",
                "mean": 1
            }},
            {"$sort": {"priceArea": 1}}
        ]

        res = list(collection.aggregate(pipeline))
        return pd.DataFrame(res).set_index('priceArea')

    @st.cache_data
    def distinct(_self, **kwargs):
        '''method to get distinct values from a column in the database'''
        db = _self._client[kwargs.get('db', 'ind320')]
        collection = db[kwargs.get('table', 'elhub')]
        column = kwargs.get('column', 'priceArea')
        return collection.distinct(column)
    
    @st.cache_data(ttl=600)
    def months(_self, **kwargs):
        '''method to get available months from the database'''
        db = _self._client[kwargs.get('db', 'ind320')]
        collection = db[kwargs.get('table', 'elhub')]

        pipeline = [
            {"$group": {"_id": {
                "year": {"$year": "$startTime"},
                "month": {"$month": "$startTime"}
            }}},
            {"$project": {"_id": 0, "y": "$_id.year", "m": "$_id.month"}},
            {"$sort": {"y": 1, "m": 1}}
        ]

        res = list(collection.aggregate(pipeline))
        # format as YYYY-MM strings
        return [f"{doc['y']:04d}-{doc['m']:02d}" for doc in res]
    
    @st.cache_data(ttl=600)
    def years(_self, **kwargs):
        '''method to get available years from the database'''
        db = _self._client[kwargs.get('db', 'ind320')]
        collection = db[kwargs.get('table', 'elhub')]

        pipeline = [
            {"$group": {"_id": {"year": {"$year": "$startTime"}}}},
            {"$project": {"_id": 0, "y": "$_id.year"}},
            {"$sort": {"y": 1}}
        ]

        res = list(collection.aggregate(pipeline))
        return [str(doc['y']) for doc in res]
    