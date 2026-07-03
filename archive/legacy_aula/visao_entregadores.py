#===========================================
# STEP 1: Loading libray and files to working directory
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

#Select Directory and Load File
os.chdir('D:/repos/projetos/curry_company/dataset')
df = pd.read_csv('train.csv')

#Show Types in Datasate
#print(df.dtypes)

#Kepping dataset original and create a dataset work (copy)
df_fd = df.copy()

#===========================================
# STEP 2: Clean dataset (remove trim and change types of columns)
#===========================================

## 1.1 - Removing white spaces in dataframe

df_fd = df_fd.apply (lambda x: x.str.strip() if x.dtype == "object" else x)

## 1.2 - Checking the columns

# for col in df_fd.select_dtypes(include=['object']).columns:
#     tem_espacos = df_fd[col].str.strip() != df_fd[col]
#     if tem_espacos.any():
#         print(f"✗ {col}: ainda tem espaços")
#     else:
#         print(f"✓ {col}: OK")

## 2 - Change type of columns

df_fd['Delivery_person_Age'] = pd.to_numeric(df_fd['Delivery_person_Age'], errors='coerce').astype('Int64')
df_fd['Delivery_person_Ratings'] = df_fd['Delivery_person_Ratings'].astype(float)
df_fd['Order_Date'] = pd.to_datetime(df_fd['Order_Date'], format='%d-%m-%Y')
df_fd['Time_Orderd'] = pd.to_timedelta(df_fd['Time_Orderd'])
df_fd['Time_Order_picked'] = pd.to_timedelta(df_fd['Time_Order_picked'])
df_fd['Time_taken(min)'] = df_fd['Time_taken(min)'].astype(str).str.replace(r'\D', '', regex=True)
df_fd['Time_taken(min)'] = df_fd['Time_taken(min)'].astype(int)
df_fd['Week_of_Year'] = df_fd['Order_Date'].dt.strftime( "%U" ).astype('Int64')

#2. Create a columns distancia_km
# 2.1 -  Conversion of degrees to radians
lat1 = np.radians(df_fd['Restaurant_latitude'])
lon1 = np.radians(df_fd['Restaurant_longitude'])
lat2 = np.radians(df_fd['Delivery_location_latitude'])
lon2 = np.radians(df_fd['Delivery_location_longitude'])

# 2.2 Haversine formula
dlat = lat2 - lat1
dlon = lon2 - lon1

a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
c = 2 * np.arcsin(np.sqrt(a))

# 2.3 Calculate the distance to earth in km (6371 - Earth radius)
df_fd['distancia_km'] = (6371 * c).round(2)

#3 Retorna o menor e maior valor de data

data_minima = df_fd['Order_Date'].min()
data_maxima = df_fd['Order_Date'].max()

#===========================================
# STEP 3: Create a Sidebar and Header - Streamlit
#===========================================

# Create page widescreen

st.set_page_config(layout="wide")

#1. Create a Header and Sidebar (Filters)

st.header ('Marketplace - Visão Entregadores')

image_path = 'D:/repos/projetos/curry_company/logo.png'
image = Image.open (image_path)
st.sidebar.image (image, width=120)

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

traffic_options = st.sidebar.multiselect(
    'Quais as condições de transito',
    ['Low','Medium','High','Jam'],
    default = ['Low']
)

st.sidebar.markdown("""___""")
st.sidebar.markdown('### Powered by GG Solution \nOwner: Guilherme Grandim')

#Slider Filter Date

linhas_selecionadas = df_fd['Order_Date'] < date_slider
df_fd = df_fd.loc[linhas_selecionadas,:]

#Traffic Filter

linhas_selecionadas = df_fd['Road_traffic_density'].isin(traffic_options)
df_fd = df_fd.loc[linhas_selecionadas,:]

#===========================================
# STEP 4: Create a Body - Streamlit
#===========================================

#Added Cards on the top of the page
col1, col2, col3 = st.columns(3)

with col1:
    maior_idade = df_fd.loc[:, 'Delivery_person_Age'].max()
    col1.metric('Mais Velho', maior_idade)

with col2:
    menor_idade = df_fd.loc[:, 'Delivery_person_Age'].min()
    col2.metric('Mais Novo', menor_idade)

with col3:
    media_qualidade_frota = df_fd['Vehicle_condition'].mean().round(3)
    
    if media_qualidade_frota > 3:
        qualidade_frota = "🟢 Excelente"
    elif media_qualidade_frota > 2:
        qualidade_frota = '🟡 Bom'
    elif media_qualidade_frota > 1:
        qualidade_frota = '🟠 Médio'
    else:
        qualidade_frota = '🔴 Ruim'

    col3.metric('Qualidade da Frota', qualidade_frota, media_qualidade_frota, delta_color = "off")

st.markdown("""___""")

#Added Cointainer with tree charts (one on left and two on right)

col5, col6 = st.columns([1,1])

with col5:
    st.markdown("Avaliação por entregador")
    
    #Remove NaN
    valores_remocao = ['NaN','conditions NaN', 'nan']
    df_limpo = df_fd[~df_fd['Vehicle_condition'].isin(valores_remocao)]
    df_limpo = df_fd.loc[:,['Delivery_person_Ratings','Delivery_person_ID']]
    
    #GroupBy Delivery Id and Ratings
    avaliacao_media_por_entregador = (
    df_limpo.groupby('Delivery_person_ID')['Delivery_person_Ratings']
    .mean()
    .reset_index()
    .rename(columns={'Delivery_person_ID': 'Entregador', 'Delivery_person_Ratings' : 'Avaliação'})
    .sort_values(by = 'Avaliação', ascending=False)
    .round(2)
    )
    
    st.dataframe(avaliacao_media_por_entregador, width=500, height=460)
    
with col6:
    st.markdown("Avaliação Média por Trafego")
    
    #Remove NaN
    valores_remocao = ['NaN','conditions NaN', 'nan']
    df_limpo = df_fd[~df_fd['Road_traffic_density'].isin(valores_remocao)]
    
    #Groupby Traffic and Ratings
    avaliacao_media_por_trafego = (
        df_limpo.groupby('Road_traffic_density')['Delivery_person_Ratings']
        .agg(
            media_avaliacao_entrega='mean',
            dp_avaliacao_entrega = 'std'
        )
        .reset_index()
        .rename(columns={'Road_traffic_density': 'Trafego'})
        .sort_values(by = 'media_avaliacao_entrega', ascending=False)
    )

    #Coeficiente of Variation
    avaliacao_media_por_trafego['CV_Avaliacao'] = (avaliacao_media_por_trafego['dp_avaliacao_entrega'] / avaliacao_media_por_trafego['media_avaliacao_entrega']) *100
    
    st.dataframe(avaliacao_media_por_trafego,  width=600, height=200)
    
    #PreProcessamento
    st.markdown("Avaliação por Clima")
    
    #Remove NaN
    valores_remocao = ['NaN','conditions NaN', 'nan']
    df_limpo = df_fd[~df_fd['Weatherconditions'].isin(valores_remocao)]

    #Agrupamento das variaveis e avaliação
    avaliacao_media_por_clima = (
        df_limpo.groupby('Weatherconditions')['Delivery_person_Ratings']
        .agg(
            media_avaliacao_entrega='mean',
            dp_avaliacao_entrega = 'std'
        )
        .reset_index()
        .rename(columns={'Weatherconditions': 'Clima', 'media_avaliacao_entrega' : 'Media_Avaliação', 'dp_avaliacao_entrega' : 'DP_Avaliação' })
        .sort_values(by = 'Media_Avaliação', ascending=False)
    )

    avaliacao_media_por_clima['CV_Avaliacao'] = (avaliacao_media_por_clima['DP_Avaliação'] / avaliacao_media_por_clima['Media_Avaliação']) *100
    
    st.dataframe(avaliacao_media_por_clima, width=600, height=200)

st.markdown("""___""")

#Added two charts in end of the page

col7, col8 = st.columns(2)

with col7:
    st.markdown("Entregadores Mais Rapidos")
    
    #Cleaner NaN
    valores_remocao = ['NaN','conditions NaN', 'nan']
    df_limpo = df_fd[~df_fd['City'].isin(valores_remocao)]
    
    #Slice Type of Cities
    cidades_unicas = df_limpo['City'].unique()
    
    #Mean Time of Delivery
    media_entregadores_cidade = (
    df_limpo.groupby(['City', 'Delivery_person_ID'])['Time_taken(min)']
    .mean()
    .reset_index()
    .round(1)
    .rename(columns={'City': 'Cidade', 'Delivery_person_ID' : 'Entregador','Time_taken(min)' : 'Tempo_de_Entrega'})
    )
    
    #Diference per Cities
    diferenca_por_cidade = (
        media_entregadores_cidade
        .groupby('Cidade')['Tempo_de_Entrega']
        .agg(['min', 'max'])
        .reset_index()
    )
    
    entregadores_mais_rapidos_cidade = (
    media_entregadores_cidade
        .sort_values(by=['Cidade', 'Tempo_de_Entrega'], ascending=[True, True])
        .groupby('Cidade')
        .head(10)
        .reset_index(drop=True)
    )
    
    st.dataframe(entregadores_mais_rapidos_cidade, use_container_width = True)

with col8:
    st.markdown("Entregadores Mais Lentos")

    entregadores_mais_lentos_cidade = (
       media_entregadores_cidade
       .sort_values(by=['Cidade', 'Tempo_de_Entrega'], ascending=[True, False])
       .groupby('Cidade')
       .head(10)
       .reset_index(drop=True)
    )
    
    st.dataframe(entregadores_mais_lentos_cidade, use_container_width = True)
