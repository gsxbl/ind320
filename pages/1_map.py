import streamlit as st
import json
import plotly.graph_objects as go
from modules.session import SessionState
from modules.header import Header
from modules.db import Mongo


class MapApp:
    def __init__(self):
        # initial setup
        SessionState()
        Header()
        
        st.set_page_config(
            page_title='IND320 Streamlit App',
            layout='wide'
        )
        # instantiate client
        self._db = Mongo()
        # load geojson
        self._geojson = self._load_geojson()


    def _load_geojson(_self):
        """Load price areas GeoJSON."""
        with open('data/file.geojson', 'r') as f:
            return json.load(f)
        
    def _load_data(self):
        '''
        Load data from MongoDB based on session state.
        '''
        self._df = self._db.mean_by_area(
            timescale=st.session_state.timescale,
            groups=st.session_state.group,
            column=st.session_state.column,
            year=st.session_state.year,
            month=st.session_state.month,
            table=st.session_state.table,
            start_time=st.session_state.start_time,
            end_time=st.session_state.end_time,
            index=['priceArea', st.session_state.column, 'startTime']
        )

        self._data = self._df['mean'].to_dict()
        self._df.reset_index(inplace=True)


    def _map(self):
        
        fig = go.Figure()

        # --- Best Practice: Create a temporary copy for plotting ---
        # This avoids modifying the original self._df on every rerun.
        df_plot = self._df.copy()
        df_plot['priceArea'] = df_plot['priceArea'].map(lambda x: x[:2] + ' ' + x[2:])

        # Use Choroplethmapbox for a detailed base map
        fig.add_trace(go.Choroplethmapbox(
            geojson=self._geojson,
            locations=df_plot['priceArea'],
            z=df_plot['mean'],
            featureidkey='properties.ElSpotOmr',
            colorscale='Viridis',
            colorbar_title='Mean Value',
            marker_line_color='white',
            marker_opacity=0.6,
            hovertemplate='<b>%{location}</b><br>Mean: %{z:.3f}<extra></extra>'
        ))

               # --- 2. Add the Highlight Layer ---
        selected_area = st.session_state.get('area')

        if selected_area:
            # Format the selected area name to match the GeoJSON property (e.g., 'NO1' -> 'NO 1')
            selected_area_formatted = selected_area[:2] + ' ' + selected_area[2:]

            # Find the geometry for the selected area
            for feature in self._geojson['features']:
                if feature.get('properties', {}).get('ElSpotOmr') == selected_area_formatted:
                    geom = feature.get('geometry', {})
                    lons, lats = [], []
                    
                    # Extract coordinates, handling both Polygon and MultiPolygon
                    if geom.get('type') == 'Polygon':
                        coords_list = geom.get('coordinates', [])
                    elif geom.get('type') == 'MultiPolygon':
                        # Flatten the list of polygons into a single list of rings
                        coords_list = [ring for poly in geom.get('coordinates', []) for ring in poly]
                    else:
                        coords_list = []

                    for ring in coords_list:
                        lons.extend([coord[0] for coord in ring])
                        lats.extend([coord[1] for coord in ring])
                        lons.append(None) # Add a break between polygon rings
                        lats.append(None)

                    # Add the highlight trace on top
                    fig.add_trace(go.Scattermapbox(
                        lon=lons,
                        lat=lats,
                        mode='lines',
                        fill='none',
                        line=dict(width=4, color='#f401e0'), # Bright highlight color
                        hoverinfo=None # Disable hover for the highlight line
                    ))
                    break # Stop searching once the area is found and drawn

        lat, lon = st.session_state.geo['latitude'], st.session_state.geo['longitude']
        fig.update_layout(
            mapbox_style="open-street-map",
            mapbox_center={"lat": lat, "lon": lon},
            mapbox_zoom=5,

            height=800,
            margin={"r": 0, "t": 0, "l": 0, "b": 0}
        )

        st.plotly_chart(fig, use_container_width=True)

    def _setup_map(self):
        with st.spinner('Loading map...'):
            self._map()

    def run(self):
        self._load_data()
        self._setup_map()

if __name__ == '__main__':
    main = MapApp()
    main.run()