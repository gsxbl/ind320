import streamlit as st
from modules.api import OpenMeteo
from modules.session import SessionState
from modules.header import Header
from modules.Snow_drift import main


class Snow:
    def __init__(self):
        # initial setup
        st.set_page_config(layout='wide')
        self._state = SessionState()
        Header(choices={
            'group': False,
            'source': False
        })
    
        # instantiate client
        self._api = OpenMeteo()

    def _pretty_print_results(self, results: dict):
        """Pretty print analysis results to Streamlit."""
        # Overall statistics metric
        # Seasonal analysis (rotated) and wind rose in same row
        col1, col2 = st.columns([1, 1])
        if st.session_state.get('timescale') == 'Monthly':
            period = f"{st.session_state.month.strftime('%B %Y')}"
        else:
            period = f"{self._state.kwargs['start_date']} - {self._state.kwargs['end_date']}"
        
        with col1:
            st.subheader(f"📊 {st.session_state.city}, {period}")
            st.metric(
                "Overall Average Qt",
                f"{results['overall_avg_tonnes']:.1f} tonnes/m"
            )
            
            st.subheader(f"📈 Fence Recommendations")
            combined_df = results['yearly_summary']
            fence_df = results['fence_results']
            
            # Merge on season column
            combined_display = combined_df.merge(fence_df, on='season', how='left')
            
            # Format numeric columns
            combined_display['Qt (tonnes/m)'] = combined_display['Qt (tonnes/m)'].apply(lambda x: f"{x:.1f}")
            for col in combined_display.columns:
                if col not in ['season', 'Control', 'Qt (tonnes/m)'] and '(m)' in col:
                    combined_display[col] = combined_display[col].apply(lambda x: f"{x:.1f}")
            
            # Transpose for vertical display, set index as column headers
            df = combined_display.set_index('season')
            if st.session_state.get('timescale') == 'Monthly':
                df.index = [period]
                
            st.dataframe(df.T, width='stretch')
        
        with col2:
            st.plotly_chart(results['rose_fig'], width='stretch')

    def run(self):
        """Execute the REPL analysis and display results."""
        if st.session_state.last_clicked == (0, 0):
            st.warning("Please select a location on the map in the Map Visualization tab.")
            return
        
        df = self._api.get_weather_data(
            latitude=st.session_state.last_clicked[0],
            longitude=st.session_state.last_clicked[1],
            start_date=self._state.kwargs['start_date'],
            end_date=self._state.kwargs['end_date']
        )
        results = main(df)
        self._pretty_print_results(results)


if __name__ == '__main__':
    try:
        main = Snow()
        main.run()
    except Exception as e:
        st.error(f"An error occurred: {e}")