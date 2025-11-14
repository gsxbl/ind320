import streamlit as st
import json
from streamlit_folium import st_folium
import folium
from shapely.geometry import shape, Point
from modules.session import SessionState
from modules.header import Header
from modules.db import Mongo


class MapApp:
    def __init__(self):
        st.set_page_config(layout='wide')
        self._state = SessionState()
        Header()

        self._lat, self._lon = st.session_state.last_clicked
        if 'map_zoom' not in st.session_state:
            st.session_state.map_zoom = 5

        self._db = Mongo()
        self._geo = self._load_geojson()
        self._mutate_geojson()

    def _setup_header(self):
        st.header('Energy Map Visualization')
        st.subheader(f'Period: {st.session_state.start_time.date()} to {st.session_state.end_time.date()}')

    @st.cache_data
    def _load_geojson(_self):
        """Load GeoJSON data for map visualization."""
        with open('data/file.geojson', 'r') as f:
            return json.load(f)

    def _load_data(self):
        """Load data points from the database."""
        self._df = self._db.mean_by_area(
            table=st.session_state.table,
            column=st.session_state.column,
            group=st.session_state.group,
            month=st.session_state.month,
            year=st.session_state.year,
            start_time=st.session_state.start_time,
            end_time=st.session_state.end_time,
            timescale=st.session_state.timescale,
            area=st.session_state.area)
        
        # set values for TWh
        self._df['mean'] /= 1000000
        self._df.reset_index(inplace=True)

    def _mutate_geojson(self):
        """Remove spaces from GeoJSON area identifiers."""
        for feature in self._geo['features']:
            area = feature['properties']['ElSpotOmr']
            feature['properties']['ElSpotOmr'] = area.replace(' ', '')

    def _setup_containers(self):
        """Setup Streamlit containers for layout."""
        self._c1, self._c2 = st.columns([3, 1])
        
    def _setup_map(self):
        """Render map visualization using loaded GeoJSON and data."""
        lat = st.session_state.geo['latitude']
        lon = st.session_state.geo['longitude']
        if st.session_state.last_clicked != (0, 0):
            lat, lon = st.session_state.last_clicked
        zoom = st.session_state.map_zoom
        self._m = folium.Map(location=[lat, lon], zoom_start=zoom)

        folium.Choropleth(
            geo_data=self._geo,
            name='choropleth',
            data=self._df,
            columns=['priceArea', 'mean'],
            key_on='properties.ElSpotOmr',
            fill_color='plasma',
            fill_opacity=0.7,
            line_opacity=0.2,
            legend_name='Mean Value (TWh)',
        ).add_to(self._m)

        if not st.session_state.selection:
            return
        else:
            # outline ElSpotOmr == sel
            folium.GeoJson(
                data={
                    "type": "FeatureCollection",
                    "features": [
                        feature for feature in self._geo['features']
                        if feature['properties']['ElSpotOmr'] == st.session_state.area
                    ]
                },
                style_function=lambda feature: {
                    'fillColor': 'black',
                    'color': 'black',
                    'weight': 3,
                    'dashArray': '5, 5'
                },
                name='Selected Area Outline',
            ).add_to(self._m)

    def _render_map(self):
        """Render map visualization using loaded GeoJSON and data."""
        # render map in container1
        with self._c1:
            self._map = st_folium(self._m, width=700, height=500)
        if self._map and self._map.get('zoom') is not None:
            st.session_state.map_zoom = self._map['zoom']

    def _render_info(self):
        """Show selection info next to the map."""
        with self._c2:
            st.subheader('Selection')
            area = st.session_state.area
            st.write(f"priceArea: {area or 'n/a'}")

            lat, lon = st.session_state.last_clicked
            if (lat, lon) == (0, 0):
                st.write('clicked location: n/a')
            else:
                st.write(f"clicked location: {lat:.4f}, {lon:.4f}")

            if area:
                mean = self._df.loc[self._df['priceArea'] == area, 'mean']
            else:
                mean = []

            if hasattr(mean, 'empty') and not mean.empty:
                st.write(f"meanTwh: {mean.iloc[0]:.2f}")
            else:
                st.write('meanTwh: n/a')

    def _get_clicked_coords(self):
        """Handle clicks and refresh state immediately."""
        click = self._map.get('last_clicked') if self._map else None
        if click is None:
            return

        self._lat = click['lat']
        self._lon = click['lng']
        if (self._lat, self._lon) == st.session_state.last_clicked:
            return

        st.session_state.last_clicked = (self._lat, self._lon)

        point = Point(self._lon, self._lat)

        for feature in self._geo['features']:
            polygon = shape(feature['geometry'])
            if polygon.contains(point):
                self._state.update_area(feature['properties']['ElSpotOmr'])
                st.session_state.selection = st.session_state.area
                break
            else:
                st.session_state.selection = None

        st.rerun()
    
    def _place_pin_on_map(self):
        """Place a pin on the map at the specified coordinates."""
        if st.session_state.last_clicked == (0, 0):
            return
        self._lat, self._lon = st.session_state.last_clicked
        folium.Marker(
            location=[self._lat, self._lon],
            popup="Clicked Location",
            icon=folium.Icon(color='red', icon='info-sign')
        ).add_to(self._m)

    def run(self):
        self._setup_header()
        self._setup_containers()
        self._load_data()
        self._setup_map()
        self._place_pin_on_map()
        self._render_map()
        self._render_info()
        self._get_clicked_coords()



if __name__ == "__main__":
    app = MapApp()
    app.run()