import streamlit as st

class Page3:
    def __init__(self):
        st.set_page_config(layout='wide')

        st.header("These aren't the droids you're looking for")
        st.image(''.join(['https://media4.giphy.com/media/',
                 'v1.Y2lkPTc5MGI3NjExa2s3eXN2cnFlc3pjZnkyMnU4Z',
                 'm1laDZ1ZDlmZ2dhMXkzcWxrenlpZyZlcD12MV9pbnRlcm',
                 '5hbF9naWZfYnlfaWQmY3Q9Zw/4560Nv2656Gv0Lvp9F/giphy.gif']),
                 width='stretch')

if __name__ == '__main__': 
    Page3()