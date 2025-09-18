import streamlit as st
import random

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

# container for the random integers
if 'out' not in st.session_state:
    st.session_state.out = 'Ready'

def click():
    # no output exists
    if st.session_state.out == 'Ready':
        st.session_state.out = random.randint(1, 100)
    

    if st.session_state.out > 1:
        i = st.session_state.out
        # output is even
        if i % 2 == 0:
            st.session_state.out //= 2
        
        # output is odd
        elif i % 2 != 0:
            st.session_state.out *= 3
            st.session_state.out += 1
    else:
        st.balloons()
    

def get_label():
    if st.session_state.out == 'Ready':
        return 'Start'
    
    if st.session_state.out == 1:
        return 'Done'

    if st.session_state.out % 2 == 0:
        return 'Half it'
    
    if st.session_state.out % 2 != 0:
        return 'Triple it'



def main():
    out = st.session_state.out
    if out: st.markdown(f'# {out}')
    
    label = get_label()
    # render button
    st.button(label, on_click=click)


main()