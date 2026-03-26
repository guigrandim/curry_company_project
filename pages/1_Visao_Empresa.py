#===========================================
# Import Libraries
#===========================================

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

st.set_page_config(page_title='Visão Empresa', page_icon='📈', layout="wide")

#===========================================
# Functions
#===========================================
def orders_per_week (df_fd):
    pedidos_por_semana = (
    df_fd.groupby(pd.Grouper(key='Order_Date', freq='W'))['ID']
    .count()
    .reset_index()
    .rename(columns={'Order_Date': 'Inicio_Semana', 'ID': 'Total_Pedidos'})
    .sort_values(by = 'Inicio_Semana', ascending=True)
    )
    
    #Line Chart Order by Week
    pedidos_por_semana['Num_Semana'] = pedidos_por_semana['Inicio_Semana'].dt.isocalendar().week
    fig = px.line(pedidos_por_semana, x='Num_Semana', y='Total_Pedidos')
    
    return fig

def traffic_city_order_share (df_fd):
    pedidos_por_cidade_trafego = (
    df_fd.groupby(['City', 'Road_traffic_density'])['ID']
    .count()
    .reset_index()
    .rename(columns={'City': 'Cidade', 'Road_traffic_density' : 'Trafego', 'ID': 'Total_Pedidos'})
    .sort_values(by = 'Total_Pedidos', ascending=False)
    )

    #Scatter Chart - City and Traffic
    fig = px.scatter(pedidos_por_cidade_trafego, x='Cidade', y='Trafego', size='Total_Pedidos', color='Cidade')
            
    return fig

def traffic_order_share(df_fd):
    pedidos_por_trafego = (
    df_fd.groupby('Road_traffic_density')['ID']
    .count()
    .reset_index()
    .rename(columns={'Road_traffic_density': 'Trafego', 'ID': 'Total_Pedidos'})
    .sort_values(by = 'Total_Pedidos', ascending=False)
    )

    #Chart Traffic Pie
    pedidos_por_trafego['pct_pedidos'] = (pedidos_por_trafego['Total_Pedidos'] / pedidos_por_trafego['Total_Pedidos'].sum()) * 100
    fig = px.pie(pedidos_por_trafego, values='pct_pedidos', names='Trafego')
    
    return fig

def order_metric(df_fd):
    pedidos_por_dia = (
    df_fd.groupby('Order_Date')['ID']
    .count()
    .reset_index()
    .rename(columns={'Order_Date': 'Data', 'ID': 'Total_Pedidos'})
    .sort_values(by = 'Total_Pedidos', ascending=False)
    )
    
    #Plot Bar Chart - Orders per Day
    fig = px.bar(pedidos_por_dia, x='Data', y='Total_Pedidos')
    
    return fig    

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

st.header ('Marketplace - Visão do Cliente')

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

tab1, tab2 = st.tabs(['Visão Gerencial','Visão Tática'])

with tab1:
    with st.container():
        fig = order_metric(df_fd)
        st.markdown("# Order By Day")
        st.plotly_chart (fig, use_container_width=True)
    
    with st.container():
        col1, col2 = st.columns(2)
        
        with col1:
            fig = traffic_order_share(df_fd)
            st.markdown ('# Trafic Order Share')
            st.plotly_chart (fig, use_container_width=True)
 
        with col2:
            fig = traffic_city_order_share(df_fd)
            st.markdown ('# City and Trafic Order Share')
            st.plotly_chart (fig, use_container_width=True)   
    
with tab2:
    fig = orders_per_week (df_fd)
    st.markdown("Pedidos por Semana")
    st.plotly_chart (fig, use_container_width = True)