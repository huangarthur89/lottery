import streamlit as st
import pandas as pd
df = pd.DataFrame({'策略名稱': ['A', 'B'], '第 1 球': [1, 2], '第 2 球': [3, 4]})
styled = df.style.set_properties(**{'text-align': 'center'})
styled = styled.set_table_styles([{'selector': 'th', 'props': [('text-align', 'center')]}])
st.markdown(styled.hide(axis="index").to_html(), unsafe_allow_html=True)
