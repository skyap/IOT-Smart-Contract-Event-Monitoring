import streamlit as st

import time

with st.empty():
    while True:
        st.write(time.time())