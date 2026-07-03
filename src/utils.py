#===========================================
# Shared data loading, cleaning and sidebar for the 3 dashboard pages
#===========================================

import os

import numpy as np
import pandas as pd
import streamlit as st
from PIL import Image

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(REPO_ROOT, 'data', 'train.csv')
LOGO_PATH = os.path.join(REPO_ROOT, 'assets', 'logo.png')
LOGO_GG_PATH = os.path.join(REPO_ROOT, 'assets', 'logo_gg.png')

TRAFFIC_OPTIONS = ['Low', 'Medium', 'High', 'Jam']


def clean_code(df_fd):
    """ Essa função tem a responsabilidade de limpar o dataframe

        Tipos de limpeza
        1. Remoção dos espaços das variaveis de texto
        2. Mudança do tipo de colunas
        3. Remoção dos NaN
        4. Formatação da Data
        5. Limpeza da coluna de tempo
        6. Criação da coluna distancia (km) pela formula de Haversine

        Input: dataframe
        Output: dataframe
    """

    ## 1 - Removing white spaces in dataframe

    df_fd = df_fd.apply(lambda x: x.str.strip() if x.dtype == "object" else x)

    ## 2 - Change type of columns

    df_fd['Delivery_person_Age'] = pd.to_numeric(df_fd['Delivery_person_Age'], errors='coerce').astype('Int64')
    df_fd['Delivery_person_Ratings'] = df_fd['Delivery_person_Ratings'].astype(float)
    df_fd['Order_Date'] = pd.to_datetime(df_fd['Order_Date'], format='%d-%m-%Y')
    df_fd['Time_Orderd'] = pd.to_timedelta(df_fd['Time_Orderd'])
    df_fd['Time_Order_picked'] = pd.to_timedelta(df_fd['Time_Order_picked'])
    df_fd['Time_taken(min)'] = df_fd['Time_taken(min)'].astype(str).str.replace(r'\D', '', regex=True)
    df_fd['Time_taken(min)'] = df_fd['Time_taken(min)'].astype(int)
    df_fd['Week_of_Year'] = df_fd['Order_Date'].dt.strftime("%U").astype('Int64')

    ## 3 - Remove NaN
    for coluna in ['Delivery_person_Age', 'Road_traffic_density', 'City', 'Festival', 'Vehicle_condition', 'multiple_deliveries']:
        df_fd = df_fd.loc[df_fd[coluna] != 'NaN', :].copy()
    df_fd['multiple_deliveries'] = pd.to_numeric(df_fd['multiple_deliveries']).astype('Int64')

    #4. Create a columns distancia_km
    # 4.1 -  Conversion of degrees to radians
    lat1 = np.radians(df_fd['Restaurant_latitude'])
    lon1 = np.radians(df_fd['Restaurant_longitude'])
    lat2 = np.radians(df_fd['Delivery_location_latitude'])
    lon2 = np.radians(df_fd['Delivery_location_longitude'])

    # 4.2 Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = np.sin(dlat / 2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2)**2
    c = 2 * np.arcsin(np.sqrt(a))

    # 4.3 Calculate the distance to earth in km (6371 - Earth radius)
    df_fd['distancia_km'] = (6371 * c).round(2)

    return df_fd


@st.cache_data
def load_data():
    """Lê o CSV bruto e devolve o dataframe já limpo. Resultado fica em cache entre reruns."""
    df = pd.read_csv(DATA_PATH)
    return clean_code(df.copy())


def build_sidebar(df_fd):
    """Renderiza o menu lateral (logo, filtro de data, filtro de trafego) comum às 3 páginas
    e devolve o dataframe já filtrado pelos valores escolhidos."""

    image1 = Image.open(LOGO_PATH)
    st.sidebar.image(image1, width=240)

    data_minima = df_fd['Order_Date'].min().date()
    data_maxima = df_fd['Order_Date'].max().date()

    st.sidebar.title('Curry Company')
    st.sidebar.markdown('Fast Delivery in Town')
    st.sidebar.markdown("""___""")

    st.sidebar.markdown('Selecione um intervalo de data')
    date_slider = st.sidebar.slider(
        'Ate qual valor ?',
        value=data_maxima,
        min_value=data_minima,
        max_value=data_maxima
    )

    st.sidebar.markdown(date_slider)
    st.sidebar.markdown("""___""")

    traffic_options = st.sidebar.multiselect(
        'Quais as condições de transito',
        TRAFFIC_OPTIONS,
        default=TRAFFIC_OPTIONS
    )

    st.sidebar.markdown("""___""")
    st.sidebar.markdown('### Powered by GG Solution \nOwner: Guilherme Grandim')
    image2 = Image.open(LOGO_GG_PATH)
    st.sidebar.image(image2, width=120)

    df_fd = df_fd.loc[df_fd['Order_Date'] <= pd.Timestamp(date_slider), :]
    df_fd = df_fd.loc[df_fd['Road_traffic_density'].isin(traffic_options), :]

    return df_fd
