#===========================================
# Import Libraries
#===========================================

#Importing Library to Project

import pandas as pd
import os
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import plotly.express as px
import folium
import streamlit as st
from PIL import Image

#===========================================
# Configuration Page
#===========================================

st.set_page_config(page_title='Visão Entregadores', page_icon='🚲', layout="wide")

#===========================================
# Functions
#===========================================
def speed_delivery (df_fd, condicao):
    #Mean Time of Delivery
    media_entregadores_cidade = (
    df_fd.groupby(['City', 'Delivery_person_ID'])['Time_taken(min)']
    .mean()
    .reset_index()
    .round(1)
    .rename(columns={'City': 'Cidade', 'Delivery_person_ID' : 'Entregador','Time_taken(min)' : 'Tempo_de_Entrega'})
    )
    
    if condicao == 'mais rapido':
        entregadores_mais_rapidos_cidade = (
        media_entregadores_cidade
        .sort_values(by=['Cidade', 'Tempo_de_Entrega'], ascending=[True, True])
        .groupby('Cidade')
        .head(10)
        .reset_index(drop=True)
        )
        return entregadores_mais_rapidos_cidade
    
    else:   
        entregadores_mais_lentos_cidade = (
        media_entregadores_cidade
        .sort_values(by=['Cidade', 'Tempo_de_Entrega'], ascending=[True, False])
        .groupby('Cidade')
        .head(10)
        .reset_index(drop=True)
        )
        return entregadores_mais_lentos_cidade

def delivery_weather_rating (df_fd):
    df_fd = df_fd.loc[:,['Weatherconditions', 'Delivery_person_Ratings']]
    
    avaliacao_media_por_clima = (
        df_fd.groupby('Weatherconditions')['Delivery_person_Ratings']
        .agg(
            media_avaliacao_entrega='mean',
            dp_avaliacao_entrega = 'std'
        )
        .reset_index()
        .rename(columns={'Weatherconditions': 'Clima', 'media_avaliacao_entrega' : 'Media_Avaliação', 'dp_avaliacao_entrega' : 'DP_Avaliação' })
        .sort_values(by = 'Media_Avaliação', ascending=False)
    )

    avaliacao_media_por_clima['CV_Avaliacao'] = (avaliacao_media_por_clima['DP_Avaliação'] / avaliacao_media_por_clima['Media_Avaliação']) *100
        
    return avaliacao_media_por_clima

def delivery_traffic_rating (df_fd):
    df_fd = df_fd.loc[:,['Road_traffic_density', 'Delivery_person_Ratings']]
    
    avaliacao_media_por_trafego = (
    df_fd.groupby('Road_traffic_density')['Delivery_person_Ratings']
    .agg(
        media_avaliacao_entrega='mean',
        dp_avaliacao_entrega = 'std'
        )
    .reset_index()
    .rename(columns={'Road_traffic_density': 'Trafego'})
    .sort_values(by = 'media_avaliacao_entrega', ascending=False)
    )

    avaliacao_media_por_trafego['CV_Avaliacao'] = (avaliacao_media_por_trafego['dp_avaliacao_entrega'] / avaliacao_media_por_trafego['media_avaliacao_entrega']) *100

    return avaliacao_media_por_trafego

def delivery_id_rating (df_fd):
    df_fd = df_fd.loc[:,['Delivery_person_Ratings','Delivery_person_ID']]
    
    #GroupBy Delivery Id and Ratings
    avaliacao_media_por_entregador = (
    df_fd.groupby('Delivery_person_ID')['Delivery_person_Ratings']
    .mean()
    .reset_index()
    .rename(columns={'Delivery_person_ID': 'Entregador', 'Delivery_person_Ratings' : 'Avaliação'})
    .sort_values(by = 'Avaliação', ascending=False)
    .round(2)
    )
        
    return avaliacao_media_por_entregador


def quality_fleet_delivery (df_fd):
    media_qualidade_frota = df_fd['Vehicle_condition'].mean().round(3)
        
    if media_qualidade_frota > 3:
        qualidade_frota = "🟢 Excelente"
    elif media_qualidade_frota > 2:
        qualidade_frota = '🟡 Bom'
    elif media_qualidade_frota > 1:
        qualidade_frota = '🟠 Médio'
    else:
        qualidade_frota = '🔴 Ruim'
    
    return media_qualidade_frota, qualidade_frota

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

    df_fd = df_fd.apply (lambda x: x.str.strip() if x.dtype == "object" else x)

    ## 2 - Change type of columns

    df_fd['Delivery_person_Age'] = pd.to_numeric(df_fd['Delivery_person_Age'], errors='coerce').astype('Int64')
    df_fd['Delivery_person_Ratings'] = df_fd['Delivery_person_Ratings'].astype(float)
    df_fd['Order_Date'] = pd.to_datetime(df_fd['Order_Date'], format='%d-%m-%Y')
    df_fd['Time_Orderd'] = pd.to_timedelta(df_fd['Time_Orderd'])
    df_fd['Time_Order_picked'] = pd.to_timedelta(df_fd['Time_Order_picked'])
    df_fd['Time_taken(min)'] = df_fd['Time_taken(min)'].astype(str).str.replace(r'\D', '', regex=True)
    df_fd['Time_taken(min)'] = df_fd['Time_taken(min)'].astype(int)
    df_fd['Week_of_Year'] = df_fd['Order_Date'].dt.strftime( "%U" ).astype('Int64')
    
    ## 3 - Remove NaN
    linhas_selecionadas = (df_fd['Delivery_person_Age'] !='NaN')
    df_fd = df_fd.loc[linhas_selecionadas, :].copy()
    
    linhas_selecionadas = (df_fd['Road_traffic_density'] !='NaN')
    df_fd = df_fd.loc[linhas_selecionadas, :].copy()
    
    linhas_selecionadas = (df_fd['City'] !='NaN')
    df_fd = df_fd.loc[linhas_selecionadas, :].copy()
    
    linhas_selecionadas = (df_fd['Festival'] !='NaN')
    df_fd = df_fd.loc[linhas_selecionadas, :].copy()
    
    linhas_selecionadas = (df_fd['Vehicle_condition'] !='NaN')
    df_fd = df_fd.loc[linhas_selecionadas, :].copy()
    
    #4. Create a columns distancia_km
    # 4.1 -  Conversion of degrees to radians
    lat1 = np.radians(df_fd['Restaurant_latitude'])
    lon1 = np.radians(df_fd['Restaurant_longitude'])
    lat2 = np.radians(df_fd['Delivery_location_latitude'])
    lon2 = np.radians(df_fd['Delivery_location_longitude'])

    # 4.2 Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
    c = 2 * np.arcsin(np.sqrt(a))

    # 4.3 Calculate the distance to earth in km (6371 - Earth radius)
    df_fd['distancia_km'] = (6371 * c).round(2)

    return df_fd

#----------------------------------------- Beginning of the logical structure code --------------------- #

#===========================================
# Select Directory - Load File and Clean dataset
#===========================================

diretorio_atual = os.path.dirname(os.path.abspath(__file__))
caminho_dados = os.path.join(diretorio_atual, '..', 'dataset', 'train.csv')

df = pd.read_csv(caminho_dados)

#Kepping dataset original and create a dataset work (copy)
df_fd = df.copy()

#Clean dataset
df_fd = clean_code(df_fd)

#===========================================
# STEP 2: Create a Sidebar and Header - Streamlit
#===========================================

#1. Create a Header and Sidebar (Filters)

st.header ('Marketplace - Visão do entregador')

diretorio_atual = os.path.dirname(os.path.abspath(__file__))
caminho_logo = os.path.join(diretorio_atual,'..','assets', 'logo.png')
caminho_logo_2 = os.path.join(diretorio_atual,'..','assets', 'logo_gg.png')

image1 = Image.open (caminho_logo)
st.sidebar.image (image1, width = 240)

#2. Return max date and min date

data_minima = df_fd['Order_Date'].min()
data_maxima = df_fd['Order_Date'].max()

#3. Create sidebar

st.sidebar.title('Curry Company')
st.sidebar.markdown('Fast Delivery in Town')
st.sidebar.markdown("""___""")

st.sidebar.markdown('Selecione um intervalo de data')
date_slider = st.sidebar.slider(
    'Ate qual valor ?',
    value= datetime(2022, 4, 13),
    min_value = data_minima,
    max_value = data_maxima
)

st.sidebar.markdown(date_slider)
st.sidebar.markdown("""___""")

#4. Create traffic filter

traffic_options = st.sidebar.multiselect(
    'Quais as condições de transito',
    ['Low','Medium','High','Jam'],
    default = ['Low','Medium','High','Jam']
)

st.sidebar.markdown("""___""")
st.sidebar.markdown('### Powered by GG Solution \nOwner: Guilherme Grandim')
image2 = Image.open (caminho_logo_2)
st.sidebar.image (image2, width = 120)

#5. Slider Date Filter

linhas_selecionadas = df_fd['Order_Date'] < date_slider
df_fd = df_fd.loc[linhas_selecionadas,:]

#6. Traffic Filter

linhas_selecionadas = df_fd['Road_traffic_density'].isin(traffic_options)
df_fd = df_fd.loc[linhas_selecionadas, :]

#===========================================
# STEP 3: Create a Body - Streamlit
#===========================================

#Added Cards on the top of the page
col1, col2, col3 = st.columns(3)

with col1:
    maior_idade = df_fd.loc[:, 'Delivery_person_Age'].max()
    col1.metric('Idade Entregador Mais Velho', maior_idade)

with col2:
    menor_idade = df_fd.loc[:, 'Delivery_person_Age'].min()
    col2.metric('Idade Entregador Mais Novo', menor_idade)

with col3:
    media_qualidade_frota, qualidade_frota = quality_fleet_delivery(df_fd)
    col3.metric('Qualidade da Frota', qualidade_frota, media_qualidade_frota, delta_color = "off")

st.markdown("""___""")

#Added Cointainer with tree charts (one on left and two on right)

col5, col6 = st.columns([1,1])

with col5:
    avaliacao_media_por_entregador = delivery_id_rating (df_fd)
    st.markdown("Avaliação por entregador")
    st.dataframe(avaliacao_media_por_entregador, width=500, height=460)
    
with col6:
    avaliacao_media_por_trafego = delivery_traffic_rating (df_fd)
    st.markdown("Avaliação Média por Trafego")
    st.dataframe(avaliacao_media_por_trafego,  width=600, height=200)
    
    avaliacao_media_por_clima = delivery_weather_rating (df_fd)
    st.markdown("Avaliação por Clima")
    st.dataframe(avaliacao_media_por_clima, width=600, height=200)
       
st.markdown("""___""")

#Added two charts in end of the page

col7, col8 = st.columns(2)

with col7:
    entregadores_mais_rapidos_cidade = speed_delivery (df_fd, 'mais rapido')
    st.markdown("Entregadores Mais Rapidos")
    st.dataframe(entregadores_mais_rapidos_cidade, use_container_width = True)

with col8:
    entregadores_mais_lentos_cidade = speed_delivery (df_fd, 'mais lento')
    st.markdown("Entregadores Mais Lentos")
    st.dataframe(entregadores_mais_lentos_cidade, use_container_width = True)