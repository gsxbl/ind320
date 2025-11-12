import streamlit as st
from modules.session import SessionState
from modules.header import Header

# Page configuration
st.set_page_config(
    page_title='IND320 Streamlit App',
    layout='wide'
)

# Initialize session state and header
SessionState()
with st.spinner('Loading...'):
    Header(render=False)

# Define home page
def home():
    st.title('Welcome to the IND320 Streamlit Application!')
    st.markdown("""
    This application provides various data visualizations and analyses
    based on energy consumption, production, weather data, and snow drift analysis.
    
    Use the sidebar to navigate between different pages and customize your data selections.
    """)

# Define pages structure with tuples (title, path)
pages_structure = {
    "📊 Data": [
        ("Weather Data", "pages/4_page_two.py"),
        ("Page Three", "pages/5_page_three.py"),
        ("Analysis B", "pages/6_new_B.py"),
    ],
    "❄️ Snow": [
        ("Snow Analysis", "pages/9_snow.py"),
    ],
    "🗺️ Maps & Analysis": [
        ("Map Visualization", "pages/1_map.py"),
        ("Charts", "pages/2_charts.py"),
        ("Analysis A", "pages/3_new_A.py"),
    ],
    "🔧 Utilities": [
        ("REPL", "pages/8_repl.py"),
        ("Page Five", "pages/7_page_five.py"),
    ],
}

# Build pages dict for st.navigation
pages = {group: [st.Page(path, title=title) for title, path in pages_list] 
         for group, pages_list in pages_structure.items()}

# Hide default navigation with CSS
st.markdown("""
<style>
    [data-testid="stSidebarNav"] {
        display: none;
    }
</style>
""", unsafe_allow_html=True)

# Create navigation with expandable groups in sidebar
with st.sidebar:
    st.markdown("### 🧭 Navigation")
    
    if st.button("🏠 Home", use_container_width=True):
        st.switch_page(st.Page(home, title="Home"))
    
    st.divider()
    
    for group_name, pages_list in pages_structure.items():
        with st.expander(group_name, expanded=False):
            for page_title, page_path in pages_list:
                if st.button(page_title, use_container_width=True, key=f"nav_{page_path}"):
                    st.switch_page(st.Page(page_path, title=page_title))

# Create navigation (required for st.switch_page to work)
nav = st.navigation([st.Page(home, title="Home")] + [page for pages_list in pages.values() for page in pages_list])
nav.run()