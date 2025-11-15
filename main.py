import streamlit as st
from modules.session import SessionState
from modules.header import Header


class Main:
    """Main landing page wrapped in a class for consistency."""

    def __init__(self):
        self._configure_page()
        SessionState()
        with st.spinner('Loading...'):
            Header(render=False)

        self._pages_structure = {
            "📊 Wheather": [
                ("Line Chart Columns", "pages/4_line_chart.py"),
                ("Historical", "pages/5_historical.py"),
                ("Anomaly analysis", "pages/6_anomalies.py"),
            ],
            "🗺️ Energy": [
                ("Charts", "pages/2_charts.py"),
                ("Frequency Analysis", "pages/3_frequency_analysis.py"),
                ("Correlations", "pages/9_correlation.py"),
            ],
            "❄️ Snow": [
                ("Map Visualization", "pages/1_map.py"),
                ("Snow Analysis", "pages/8_snow.py"),
            ],
            "🔧 Utilities": [
                ("Settings", "pages/10_settings.py"),
                ("Droids", "pages/7_page_five.py"),
            ],
        }

        self._pages = self._create_pages()
        self._home_page = st.Page(self._home, title="Home")

    def _configure_page(self):
        title = st.session_state.get('app_title', 'IND320 Streamlit App')
        layout = st.session_state.get('app_layout', 'wide')
        sidebar_state = st.session_state.get('app_sidebar', 'auto')
        st.set_page_config(
            page_title=title,
            layout=layout,
            initial_sidebar_state=sidebar_state
        )

    def _create_pages(self):
        pages = {}
        for group, items in self._pages_structure.items():
            pages[group] = [st.Page(path, title=title) for title, path in items]
        return pages

    def _home(self):
        st.title(f'Welcome to the {st.session_state.get("app_title", "IND320 Streamlit App")} Application!')
        st.markdown(
            """
            This application provides various data visualizations and analyses
            based on energy consumption, production, weather data, and snow drift analysis.
            
            Mainly created by the author, with help from
            - GPT-5.1-Codex
            - Claude Haiku 4.5
            - Gemini 2.5 Pro.
            
            Some code snippets and ideas were heavily inspired by the
            [IND320 course material](https://khliland.github.io/IND320/0_General/Introduction.html).

            Code structure and layout by author.
            Certain rearrangements and refactoring assisted by AI.

            ### Use the 
            ##  <- sidebar
            ### to navigate between different pages and customize your data selections.
            """
        )

    def _hide_default_nav(self):
        st.markdown(
            """
            <style>
                [data-testid="stSidebarNav"] {
                    display: none;
                }
            </style>
            """,
            unsafe_allow_html=True
        )

    def _render_sidebar(self):
        with st.sidebar:
            st.markdown("### 🧭 Navigation")

            if st.button("🏠 Home", width='stretch'):
                st.switch_page(self._home_page)

            st.divider()

            for group_name, items in self._pages_structure.items():
                with st.expander(group_name, expanded=False):
                    for (title, path), page in zip(items, self._pages[group_name]):
                        if st.button(title, width='stretch', key=f"nav_{path}"):
                            st.switch_page(page)

    def _all_pages(self):
        return [page for group in self._pages.values() for page in group]

    def run(self):
        self._hide_default_nav()
        self._render_sidebar()
        nav = st.navigation([self._home_page] + self._all_pages())
        nav.run()


if __name__ == '__main__':
    main = Main()
    main.run()