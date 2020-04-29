import streamlit as st
import pandas as pd
import altair as alt
import numpy as np

def principal():
    st.title('Dashboard Teste')
    df = pd.DataFrame(np.random.randn(200, 3), columns=['a', 'b', 'c'])
    c = alt.Chart(df).mark_circle().encode(x='a', y='b', size='c', color='c')
    st.altair_chart(c)


if __name__ == "__main__":
    principal()
