import os
import streamlit as st
from PIL import Image

st.set_page_config(
    page_title="Home",
    page_icon="🏡",
    layout = 'wide'
)

diretorio_atual = os.path.dirname(os.path.abspath(__file__))
caminho_logo = os.path.join(diretorio_atual,'assets', 'logo.png')
caminho_logo_2 = os.path.join(diretorio_atual,'assets', 'logo_gg.png')

image1 = Image.open (caminho_logo)
st.sidebar.image (image1, width = 240)

st.sidebar.title('Curry Company')
st.sidebar.markdown('Fast Delivery in Town')
st.sidebar.markdown("""___""")

st.sidebar.markdown('### Powered by GG Solution \nOwner: Guilherme Grandim')
image2 = Image.open (caminho_logo_2)
st.sidebar.image (image2, width = 120)

st.write("# Curry Company Growth Dashboard")

st.markdown(
    """
    Growth Dashboard foi construido para acompanhamento das métricas de crescimento dos Entregadores e Restaurantes.
    ### Como utilizar essa dashboard?
    - Visão Empresa:
        - Visão Gerencial: Métricas gerais de comportamento
        - Visão Tática: Indicadores semanais de crescimento
    - Visão Entregadores:
        - Acompanhamento dos indicadores semanais de crescimento
    - Visão Restaurantes:
        - Indicadores semanais de crescimento dos restaurantes

    ### Ask for Help
    - Head GG Solution: 📩 @gui.grandim or ℹ️ guilherme-grandim
    """)