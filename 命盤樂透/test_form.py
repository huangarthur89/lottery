import streamlit as st

with st.form("my_form"):
    st.write("Inside form")
    c = st.checkbox("Check me")
    submitted = st.form_submit_button("Submit")

if submitted:
    st.write("Submitted", c)
