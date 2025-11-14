import streamlit as st


class StreamlitSettings:
    """Minimal utilities page to tweak Streamlit config."""

    def __init__(self):
        title = st.session_state.get('app_title', 'IND320 Streamlit App')
        layout = st.session_state.get('app_layout', 'wide')
        sidebar = st.session_state.get('app_sidebar', 'auto')
        st.set_page_config(
            page_title=title,
            layout=layout,
            initial_sidebar_state=sidebar
        )

    def _render_form(self):
        defaults = {
            'title': st.session_state.get('app_title', 'IND320 Streamlit App'),
            'layout': st.session_state.get('app_layout', 'wide'),
            'sidebar': st.session_state.get('app_sidebar', 'auto'),
        }
        layout_options = ['centered', 'wide']
        sidebar_options = ['auto', 'expanded', 'collapsed']

        with st.form('streamlit_settings', clear_on_submit=False):
            title = st.text_input('Page title', defaults['title'])
            layout_idx = layout_options.index(defaults['layout']) if defaults['layout'] in layout_options else 1
            layout = st.selectbox('Layout', layout_options, index=layout_idx)
            sidebar_idx = sidebar_options.index(defaults['sidebar']) if defaults['sidebar'] in sidebar_options else 0
            sidebar = st.selectbox('Sidebar state', sidebar_options, index=sidebar_idx)
            submitted = st.form_submit_button('Save settings', use_container_width=True)

        if submitted:
            st.session_state.app_title = title or 'IND320 Streamlit App'
            st.session_state.app_layout = layout
            st.session_state.app_sidebar = sidebar
            st.rerun()

    def run(self):
        st.title('Streamlit Settings')
        st.caption('Adjust page layout and title. Changes apply immediately after saving.')
        self._render_form()


if __name__ == '__main__':
    StreamlitSettings().run()
