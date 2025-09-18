import streamlit as st
import random

class Main:
    def __init__(self):
        
        st.set_page_config(
            page_title='Ind320 - CA1 - gsxbl',
            page_icon='❂',
            layout='wide'
        )

        with st.expander('Task description, CA1'):
            st.markdown(
                '''
                ### Streamlit app
                1. Create a Streamlit app including:
                    - requirements.txt (for package dependencies)
                    - Four pages (with dummy headers and test contents for now)
                2. The front/home page should have a sidebar menu with navigation options to the other pages.
                3. On the second page:
                    - A table showing the imported data (see below). Use the row-wise LineChartColumn() to display the first month of the data series.
                4. On the third page:
                    - A plot of the imported data (see below), including header, axis titles and other relevant formatting.
                    - A drop-down menu (st.selectbox) choosing any single column in the CSV or all columns together.
                    - A selection slider (st.select_slider) to select a subset of the months. Defaults should be the first month.
                    - Data should be read from a local CSV-file (open-meteo-subset.csv), using caching for app speed.
                '''
            )
            
        self._keys = [f"Task {i}" for i in range(4)]

    # Reusable callback
    def show_balloons(self):
        # Loop over all checkbox keys
        for key in self._keys:
            if st.session_state.get(key, False):
                st.balloons()

    def checkboxes(self):
        # List of checkbox keys
        # Create 5 checkboxes with same callback
        for i, key in enumerate(self._keys, start=1):
            st.checkbox(f"Task {i}", key=key, on_change=self.show_balloons)

    def run(self):
        self.checkboxes()

if __name__ == '__main__':
    main = Main()
    main.run()

    