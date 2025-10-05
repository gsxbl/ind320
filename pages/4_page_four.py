import streamlit as st
import plotly.graph_objects as go

from modules.fetch import Mongo

class Page4:
    '''
    This class represents the app page.
    
    Most page contents is rendered in the run method.
    Properties are used to mimic global variables,
    making them accessible to all methods.
    '''
    def __init__(self):
        # general page setup
        st.set_page_config(layout='wide')
        st.markdown(
            '# Elhub data'
        )

        # instantiate client
        self._db = Mongo()

    def _get_areas(self):
        '''
        Method to get available priceAreas for
        frontend radio selector
        '''
        self._areas = self._db.distinct(column='priceArea')

    def _get_groups(self):
        '''
        Method to get available productionGroups for
        frontend pills selector
        '''
        self._groups = self._db.distinct(column='productionGroup')
    
    def _get_timerange(self):
        '''
        Method to get available time range for
        frontend slider selector
        '''
        self._timerange = self._db.distinct(column='startTime')

    def _setup_columns(self):
        '''
        Method to split frontend and set size relation
        '''
        self._c1, self._c2 = st.columns((1,2))

    def _setup_radio(self):
        '''
        Method to get radio button selection from
        frontend
        '''
        self._area = st.radio('', self._areas,
                              horizontal=True)
    
    def _setup_pills(self):
        '''
        Method to get pill button selections from
        frontend
        '''
        self._group = st.pills(
            '', self._groups,
            selection_mode='multi',
            default=self._groups[0],
            )

    def _setup_slider(self):
        with st.expander('Expand this for a redundant slicer'):
            self._start, self._stop = st.select_slider(
                "Select time range",
                options=self._timerange,
                value=(self._timerange[0], self._timerange[-1])
                )

    def _setup_doc(self):
        with st.expander('Data source:'):
            st.markdown(
                'Data has been extracted from [Elhub](https://api.elhub.no), and shows Energy production in Norway in 2021.' \
                '<br> iterate all months with<br>' \
                'curl -X GET "https://api.elhub.no/energy-data/v0/price-areas?dataset=CONSUMPTION_PER_GROUP_MBA_HOUR&startDate=2021-01-01',
                unsafe_allow_html=True
            )

    def _pie_chart(self):
        '''
        Method to get data from database and
        render pie chart to frontend.
        '''
        

        df = self._db.find(
            query={
                'priceArea': self._area,
                },
            index='startTime'
        )
        df = df.groupby('productionGroup').agg('sum')

        fig = go.Figure()

        fig.add_trace(go.Pie(
            labels=df.index,
            values=df['quantityKwh'] / 1e9, # TWh
            rotation=180,
            )
        )

        fig.update_layout(title=f'Production, {self._area} [%, TWh]')
        
        st.plotly_chart(fig)

    def _line_plot(self):
        '''
        Method to iterate all frontend selected pills
        and adds their contents to a plotly graph object.
        Method renders the figure to frontend.
        '''

        if not isinstance(self._group, list):
            self._group = list(self._group)     

        fig = go.Figure()

        for group in self._group:
            df = self._db.find(
            query={'productionGroup': group,
                   'priceArea': self._area,
                   'startTime': {
                       '$gt': self._start,
                       '$lt': self._stop
                   }},
            index=['priceArea','productionGroup', 'startTime']
            )

            # get the indices to slice the frame - assume only one year of data.
            # indices = df.loc[self._area, group].index.month == 1
            df = df.loc[self._area, group]

            # create trace
            trace = go.Scatter(
                x = df.index,
                y = df['quantityKwh'] / 1e3,
                name=group
            )
            fig.add_trace(trace)

        fig.update_layout(
            title=f'Production in {self._area}',
            yaxis=dict(
                title='Production [MWh]'
            )
        )
        # render to frontend
        st.plotly_chart(fig)

    # --- PAGE CONTENTS ---
    def _setup_contents(self):
        '''
        Method to get setup all contents of the
        frontend. Split into two columns for
        different plots.
        Selection in left column slices the data
        in the right column.
        '''
        # left column
        with self._c1:
            st.markdown('## Pie chart')
            self._setup_radio()
            self._pie_chart()
        
        # right column
        with self._c2:
            st.markdown('## Timeseries')
            self._setup_pills()
            self._setup_slider()
            self._line_plot()
        
        self._setup_doc()

        
    def run(self):
        '''Main runtime method'''
        self._get_areas()
        self._get_groups()
        self._get_timerange()
        self._setup_columns()
        self._setup_contents()


if __name__ == '__main__':
    main = Page4()
    main.run()