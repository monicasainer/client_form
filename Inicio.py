import streamlit as st
import pandas as pd
from pathlib import Path
from PIL import Image




current_dir = Path(__file__).parent if "__file__"in locals() else Path.cwd()


st.set_page_config(
    page_title="Formulario Clientes",
    page_icon="🤝",
    layout="wide",
    initial_sidebar_state='expanded'
)

# ## Page configuration
def app():
    st.header('Formulario de clientes')



st.write("")
st.write("")
st.write("")
