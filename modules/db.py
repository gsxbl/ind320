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
        either by YYYY-MM, YYYY or startTime and endTime range
        '''
        # db = _self._client[kwargs.get('db', 'ind320')]
        # collection = db[kwargs.get('table', 'elhub')]
        query = {}

        timescale = kwargs.get('timescale', 'Monthly')
        month = kwargs.get('month', None)
        year = kwargs.get('year', None)
        start_time = kwargs.get('start_time', None)
        end_time = kwargs.get('end_time', None)

        index = kwargs.get('index', None)

        if timescale == 'Monthly':
            # compute next month as datetime
            if month.month == 12:
                next_month = datetime(month.year + 1, 1, 1)
            else:
                next_month = datetime(month.year, month.month + 1, 1)
            query = {
                'startTime': {
                    '$gte': month,
                    '$lt': next_month
                }
            }
        elif timescale == 'Annual':
            # compute next year as datetime
            if not isinstance(year, datetime):
                year = datetime(year, 1, 1)
            next_year = datetime(year.year + 1, 1, 1)

            query = {
                'startTime': {
                    '$gte': year,
                    '$lt': next_year
                }
            }

        elif timescale == 'Custom':
            query = {
                'startTime': {
                    '$gte': start_time,
                    '$lte': end_time
                }
            }
        return _self.find(query=query, index=index)
    
    @st.cache_data(ttl=600)
    def mean_by_area(_self, **kwargs):
        table = kwargs.get('table', 'elhub')
        group = kwargs.get('group', None)

        db = _self._client[kwargs.get('db', 'ind320')]
        collection = db[table]

        if not group:
            st.write('No groups selected, returning zeros dataframe.')
            all_areas = _self.distinct(table=table, column='priceArea')
            df_zeros = pd.DataFrame({
                'priceArea': all_areas,
                'mean': 0
            })
            return df_zeros.set_index('priceArea')
        
        timescale = kwargs.get('timescale', 'Monthly')
        month = kwargs.get('month', '2021-01')
        year = kwargs.get('year', '2021')

        # build date range query
        if timescale == 'Monthly':
            start = month
            if month.month == 12:
                stop = datetime(month.year + 1, 1, 1)
            else:
                stop = datetime(month.year, month.month + 1, 1)
        elif timescale == 'Annual':
            start = year
            stop = datetime(year.year + 1, 1, 1)
        else:
            start = kwargs.get('start_time', None)
            stop = kwargs.get('end_time', None)

        # --- Build the aggregation pipeline ---
        pipeline = []
        
        # 1. Initial Match Stage (Time and optional Group filter)
        match_stage = {"startTime": {"$gte": start, "$lt": stop}}
        if group:
            group_col = kwargs.get('column', 'consumptionGroup')
            match_stage[group_col] = {"$in": group if isinstance(group, list) else [group]}

        pipeline.append({"$match": match_stage})

        # 2. Group by priceArea and calculate total quantity and unique days
        pipeline.append({
            "$group": {
                "_id": "$priceArea",
                "totalQuantity": {"$sum": "$quantityKwh"},
                "uniqueDays": {"$addToSet": {"$dateToString": {"format": "%Y-%m-%d", "date": "$startTime"}}}
            }
        })

        # 3. Project the final result, calculating the mean daily value
        pipeline.append({
            "$project": {
                "_id": 0,
                "priceArea": "$_id",
                "mean": {
                    "$cond": [
                        {"$eq": [{"$size": "$uniqueDays"}, 0]}, # Avoid division by zero
                        0,
                        {"$divide": ["$totalQuantity", {"$size": "$uniqueDays"}]}
                    ]
                }
            }
        })

        # 4. Final Sort
        pipeline.append({"$sort": {"priceArea": 1}})

        res = list(collection.aggregate(pipeline))
        if not res:
            return pd.DataFrame() # Return empty DataFrame if no results
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
        '''method to get available months from the database as datetime objects'''
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
        # format as datetime
        return [datetime(year=doc['y'], month=doc['m'], day=1) for doc in res]

    @st.cache_data(ttl=600)
    def years(_self, **kwargs):
        '''method to get available years from the database as datetime objects'''
        db = _self._client[kwargs.get('db', 'ind320')]
        collection = db[kwargs.get('table', 'elhub')]

        pipeline = [
            {"$group": {"_id": {"year": {"$year": "$startTime"}}}},
            {"$project": {"_id": 0, "y": "$_id.year"}},
            {"$sort": {"y": 1}}
        ]

        res = list(collection.aggregate(pipeline))
        return [datetime(year=doc['y'], month=1, day=1) for doc in res]