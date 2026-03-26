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
import plotly.graph_objects as go
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

st.header ('Marketplace - Visão Restaurantes')

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
    default = ['Low','Medium','High','Jam']
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

#Header Cards Main Page

col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    
    #Clean NaN
    valores_remocao = ['NaN','conditions NaN', 'nan']
    df_limpo = df_fd[~df_fd['Delivery_person_Age'].isin(valores_remocao)]

    #Filter By Unique Delivery
    entregadores_unicos = len(df_limpo.loc[:,'Delivery_person_ID'].unique())
    
    col1.metric('Entregadores BD', entregadores_unicos)

with col2:
    #Clean NaN
    valores_remocao = ['NaN','conditions NaN', 'nan']
    df_limpo = df_fd[~df_fd['City'].isin(valores_remocao)].copy()
    
    distancia_media_geral = df_limpo['distancia_km'].mean().round(0)
    
    col2.metric('Distancia Med [Km]', distancia_media_geral)

with col3:
    #Clean NaN
    valores_remocao = ['NaN','conditions NaN', 'nan']
    df_limpo = df_fd[~df_fd['Festival'].isin(valores_remocao)]
    
    entrega_festival = (
        df_limpo.groupby('Festival')
        .agg(
            tempo_medio = ('Time_taken(min)', 'mean'),
            dp_tempo = ('Time_taken(min)', 'std'),
            distancia_media = ('distancia_km', 'mean'),
            dp_distancia = ('distancia_km','std')
        )
        .reset_index()
        .round(2)
    )
    
    entrega_festival['coef_variacao'] = ((entrega_festival['dp_tempo'] / entrega_festival['tempo_medio']) *100).round(2)
    
    clas_cv = [0, 15, 30, 50, 100]
    labels = ["💎 Muito Consistente", "✅ Aceitável", "⚠️ Instável", "🚨 Crítico"]
    
    entrega_festival['class_cv'] = pd.cut(entrega_festival['coef_variacao'],bins=clas_cv, labels=labels)
    
    tempo_entrega_festival = entrega_festival['tempo_medio'].iloc[-1]
    estabilidade_operacao_festival = entrega_festival['class_cv'].iloc[-1]
    
    col3.metric('Media Entrega[min]\n\nCom Festival', tempo_entrega_festival, estabilidade_operacao_festival, delta_color = "off", delta_arrow="off")
    
with col4:
    dp_entrega_festival = entrega_festival['dp_tempo'].iloc[-1]
    col4.metric('DP Entrega[min]\n\nCom Festival', dp_entrega_festival)
    
with col5:
    tempo_entrega_sem_festival = entrega_festival['tempo_medio'].iloc[0]
    estabilidade_operacao_sem_festival = entrega_festival['class_cv'].iloc[0]
    
    col5.metric('Media Entrega[min]\n\nSem Festival', tempo_entrega_sem_festival, estabilidade_operacao_sem_festival, delta_color = "off", delta_arrow="off")

with col6:
    dp_entrega_sem_festival = entrega_festival['dp_tempo'].iloc[0]
    col6.metric('DP Entrega[min]\n\nSem Festival', dp_entrega_sem_festival)

st.markdown("""___""")

#Pie Chart - Order by Time Delivry by City

container1 = st.container(border = True)

with container1:
    st.markdown("Distancia Média por cidade")
    
    #PreProcessamento
    valores_remocao = ['NaN','conditions NaN', 'nan']
    df_limpo = df_fd[~df_fd['City'].isin(valores_remocao)]
    
    distancia_restaurante_cidade = (
        df_limpo.groupby('City')
        .agg(
            distancia_media = ('distancia_km', 'mean'),
            dp_distancia = ('distancia_km', 'std'),
            tempo_medio = ('Time_taken(min)', 'mean'),
            dp_tempo = ('Time_taken(min)', 'std')
            )
        .reset_index()
        .round(2)
    )
    
    fig = go.Figure(data=[go.Pie(labels=distancia_restaurante_cidade['City'], 
                                     values=distancia_restaurante_cidade['distancia_media'], 
                                     textinfo='label+percent', 
                                     insidetextorientation='radial')])
    st.plotly_chart(fig)
    
    st.dataframe(distancia_restaurante_cidade)

st.markdown("""___""")

#Two Charts - First Chart (Bar Chart - Mean and Std) and Second Chart (Sunburst Chart)

col1, col2 = st.columns([1,2])

with col1:
    st.markdown("Distribuição de Tempo por Cidade")
    
    #Clear all NaN
    valores_remocao = ['NaN','conditions NaN', 'nan']
    df_limpo = df_fd[~df_fd['City'].isin(valores_remocao)]
    
    tempo_medio_entrega_cidade = (
    df_limpo.groupby('City')['Time_taken(min)']
    .agg(
        tempo_medio_entregas = 'mean',
        dp_entregas = 'std')
    .reset_index()
    .round(2)
    .rename(columns={'City': 'cidade'})
    )
    
    tempo_medio_entrega_cidade['coef_variacao'] = ((tempo_medio_entrega_cidade['dp_entregas'] / tempo_medio_entrega_cidade['tempo_medio_entregas']) * 100).round(2)
    
    fig = go.Figure()
    fig.add_trace(go.Bar(name='Control', x=tempo_medio_entrega_cidade['cidade'], y=tempo_medio_entrega_cidade['tempo_medio_entregas'],
                         error_y=dict(type='data', array=tempo_medio_entrega_cidade['dp_entregas'])))
    st.plotly_chart(fig)
    
with col2:
    st.markdown("Tempo Médio por tipo de Entrega")
    
    valores_remocao = ['NaN','conditions NaN', 'nan']
    df_limpo = df_fd[~df_fd['City'].isin(valores_remocao) & ~df_fd['Type_of_order'].isin(valores_remocao)]

    tempo_medio_cidade_tipo = (
        df_limpo.groupby(['City','Type_of_order'])['Time_taken(min)']
        .agg(
            tempo_medio = 'mean',
            dp_tempo = 'std'
        )
        .reset_index()
        .round(2)
        .rename(columns={'City': 'cidade', 'Type_of_order': 'pedido', })
        .sort_values(by='tempo_medio', ascending=True)
    )
    
    tempo_medio_cidade_tipo['coef_variacao'] = ((tempo_medio_cidade_tipo['dp_tempo'] / tempo_medio_cidade_tipo['tempo_medio']) *100).round(2)

    clas_cv = [0, 15, 30, 50, 100]
    labels = ["💎 Muito Consistente", "✅ Aceitável", "⚠️ Instável", "🚨 Crítico"]

    tempo_medio_cidade_tipo['class_cv'] = pd.cut(tempo_medio_cidade_tipo['coef_variacao'],bins=clas_cv, labels=labels)
    
    st.dataframe(tempo_medio_cidade_tipo)

container1 = st.container(border = True)

with container1:
    st.markdown("Media de Tempo de Entrega por Cidade e Trafego")
    
    #Remove NaN
    valores_remocao = ['NaN','conditions NaN', 'nan']
    df_limpo = df_fd[~df_fd['City'].isin(valores_remocao) & ~df_fd['Road_traffic_density'].isin(valores_remocao)]
    
    #GroupBy City and Traffic
    tempo_medio_cidade_trafego = (
        df_limpo.groupby(['City','Road_traffic_density'])['Time_taken(min)']
        .agg(
            tempo_medio = 'mean',
            dp_tempo = 'std'
        )
        .round(2)
        .sort_values(by=['City', 'tempo_medio'], ascending=[True, True])
        .reset_index()
        .rename(columns={'City': 'cidade', 'Road_traffic_density': 'Trafego'})
    )
    
    fig = px.sunburst(tempo_medio_cidade_trafego, path =['cidade', 'Trafego'], values='tempo_medio',
                      color = 'dp_tempo', color_continuous_scale='RdBu',
                      color_continuous_midpoint=np.average(tempo_medio_cidade_trafego['dp_tempo']))
    
    st.plotly_chart(fig)
    
    st.dataframe(tempo_medio_cidade_trafego)