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
        Header()
    
        # instantiate client
        self._api = OpenMeteo()

    def _pretty_print_results(self, results: dict):
        """Pretty print analysis results to Streamlit."""
        # Overall statistics metric
        # Seasonal analysis (rotated) and wind rose in same row
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("📊 Overall Statistics")
            st.metric(
                "Overall Average Qt",
                f"{results['overall_avg_tonnes']:.1f} tonnes/m"
            )
            
            st.subheader("📈 Seasonal Analysis")
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
            transposed_df = combined_display.set_index('season').T
            st.dataframe(transposed_df, use_container_width=True)
        
        with col2:
            st.plotly_chart(results['rose_fig'], use_container_width=True)

    def run(self):
        """Execute the REPL analysis and display results."""
        df = self._api.get_weather_data(**self._state.kwargs)
        results = main(df)
        self._pretty_print_results(results)


if __name__ == '__main__':
    app = Snow()
    app.run()