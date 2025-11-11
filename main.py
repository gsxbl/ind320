import streamlit as st
from modules.session import SessionState
from modules.header import Header



class Main:
    def __init__(self):
        # initial setup
        SessionState()
        with st.spinner('Loading...'):
            Header(render=False)
        
        st.set_page_config(
            page_title='IND320 Streamlit App',
            layout='wide'
        )
    
    def _welcome_message(self):
        st.title('Welcome to the IND320 Streamlit Application!')
        st.markdown("""
        This application provides various data visualizations and analyses
        based on energy consumption, production, weather data, and snow drift analysis.
        
        Use the sidebar to navigate between different pages and customize your data selections.
        """)

    # provide buttons to navigate to different pages
    def _link_pages(self):
        st.header('Navigate to Pages')
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button('📍 Map Visualization', use_container_width=True):
                st.switch_page('pages/1_map.py')
        
        with col2:
            if st.button('🌡️ Weather Data', use_container_width=True):
                st.switch_page('pages/4_page_two.py')
        
        with col3:
            if st.button('⛷️ Snow Analysis', use_container_width=True):
                st.switch_page('pages/9_snow.py')

    def run(self):
        self._welcome_message()
        self._link_pages()

if __name__ == '__main__':
    main = Main()
    main.run()