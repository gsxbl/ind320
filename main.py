import streamlit as st
import random

st.set_page_config(
    page_title='Entry Point',
    page_icon='❂'
)

with st.expander('Task description'):
    st.markdown(
        '''
        1. Create a streamlit app with a single button and a single output.
        2. On first time startup:
        \t - The button should show the label “Start”.
        \t - The output should say “Ready”
        \t - When the button is pressed:
        \t \t - A random integer between 1 and 100 is sampled and cached.
        \t \t - The button label is changed to “Next”.
        \t \t - The output should show the integer.
        3. On subsequent button presses:
        \t - If the integer is even, divide it by 2 and update the output and cache.
        \t - If the integer is odd, multiply by 3 and add 1, then update the output and cache.
        \t - The Collatz conjecture says that after clicking the button a sufficient amount of times, the integer will reach 1, no matter what the starting point was.
        4. Extra: Let the button say “Half it” and “Triple and add one” based on the current integer shown.
        '''
    )

def init():
    if 'label' not in st.session_state:
        st.session_state.label = 'Start'
    
    if 'out' not in st.session_state:
        st.session_state.out = 'Ready'

def run():
    init()

    if st.button(st.session_state.label):
        pass