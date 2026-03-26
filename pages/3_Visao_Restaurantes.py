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
import plotly.graph_objects as go
import streamlit as st
from PIL import Image

#===========================================
# Configuration Page
#===========================================

st.set_page_config(page_title='Visão Entregadores', page_icon='🍽️', layout="wide")

#===========================================
# Functions
#===========================================
def traffic_city_mean (df_fd):
    tempo_medio_cidade_trafego = (
        df_fd.groupby(['City','Road_traffic_density'])['Time_taken(min)']
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
    
    return fig, tempo_medio_cidade_trafego

def time_city_order (df_fd):
    tempo_medio_cidade_tipo = (
        df_fd.groupby(['City','Type_of_order'])['Time_taken(min)']
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
    
    return tempo_medio_cidade_tipo

def delivery_mean_city (df_fd):
    tempo_medio_entrega_cidade = (
    df_fd.groupby('City')['Time_taken(min)']
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
    return fig


def restaurante_distance (df_fd):
    distancia_restaurante_cidade = (
        df_fd.groupby('City')
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
    
    return fig, distancia_restaurante_cidade

def festival_delivery(df_fd):
    entrega_festival = (
        df_fd.groupby('Festival')
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
    dp_entrega_festival = entrega_festival['dp_tempo'].iloc[-1]
    tempo_entrega_sem_festival = entrega_festival['tempo_medio'].iloc[0]
    estabilidade_operacao_sem_festival = entrega_festival['class_cv'].iloc[0]
    dp_entrega_sem_festival = entrega_festival['dp_tempo'].iloc[0]
        
    return {
        'tempo_entrega_festival': tempo_entrega_festival,
        'estabilidade_operacao_festival': estabilidade_operacao_festival,
        'dp_entrega_festival': dp_entrega_festival,
        'tempo_entrega_sem_festival': tempo_entrega_sem_festival,
        'estabilidade_operacao_sem_festival': estabilidade_operacao_sem_festival,
        'dp_entrega_sem_festival': dp_entrega_sem_festival
    }

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

# Create page widescreen

st.set_page_config(layout="wide")

#1. Create a Header and Sidebar (Filters)

st.header ('Marketplace - Visão do Restaurante')

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

#Header Cards Main Page

col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    #Filter By Unique Delivery
    entregadores_unicos = len(df_fd.loc[:,'Delivery_person_ID'].unique())
    col1.metric('Entregadores BD', entregadores_unicos)

with col2:
    distancia_media_geral = df_fd['distancia_km'].mean().round(0)
    col2.metric('Distancia Med [Km]', distancia_media_geral)

with col3:
    var = festival_delivery(df_fd)
    col3.metric(label = 'Media Entrega[min]\n\nCom Festival', 
                value = var['tempo_entrega_festival'],
                delta = var['estabilidade_operacao_festival'],
                delta_color = "off", 
                delta_arrow="off")
    
with col4:
    var = festival_delivery(df_fd)
    col4.metric(label = 'DP Entrega[min]\n\nCom Festival',
                value = var['dp_entrega_festival'])
    
with col5:
    var = festival_delivery(df_fd)
    col5.metric(label= 'Media Entrega[min]\n\nSem Festival', 
                value = var ['tempo_entrega_sem_festival'],
                delta = var ['estabilidade_operacao_sem_festival'],
                delta_color = "off", 
                delta_arrow="off")

with col6:
    var = festival_delivery(df_fd)
    col6.metric(label = 'DP Entrega[min]\n\nSem Festival',
                value = var['dp_entrega_sem_festival'])

st.markdown("""___""")

#Pie Chart - Order by Time Delivry by City

container1 = st.container(border = True)

with container1:
    fig, distancia_restaurante_cidade = restaurante_distance (df_fd)
    st.markdown("Distancia Média por cidade")
    st.plotly_chart(fig)
    st.dataframe(distancia_restaurante_cidade)

st.markdown("""___""")

#Two Charts - First Chart (Bar Chart - Mean and Std) and Second Chart (Sunburst Chart)

col1, col2 = st.columns([1,2])

with col1:
    fig = delivery_mean_city (df_fd)
    st.markdown("Distribuição de Tempo por Cidade")
    st.plotly_chart(fig)
     
with col2:
    tempo_medio_cidade_tipo = time_city_order (df_fd)
    st.markdown("Tempo Médio por tipo de Entrega")
    st.dataframe(tempo_medio_cidade_tipo)

container1 = st.container(border = True)

with container1:
    fig, tempo_medio_cidade_trafego = traffic_city_mean (df_fd)
    st.markdown("Media de Tempo de Entrega por Cidade e Trafego")
    st.plotly_chart(fig)
    st.dataframe(tempo_medio_cidade_trafego)