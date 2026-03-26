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

st.header ('Marketplace - Visão do cliente')

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

#Slider Date Filter

linhas_selecionadas = df_fd['Order_Date'] < date_slider
df_fd = df_fd.loc[linhas_selecionadas,:]

#Traffic Filter

linhas_selecionadas = df_fd['Road_traffic_density'].isin(traffic_options)
df_fd = df_fd.loc[linhas_selecionadas, :]

#===========================================
# STEP 4: Create a Body - Streamlit
#===========================================

tab1, tab2 = st.tabs(['Visão Gerencial','Visão Tática'])

with tab1:
    with st.container():
        st.markdown("# Quantidade de Pedidos Por Dia")
        #Clean NaN
        valores_remocao = ['NaN','conditions NaN', 'nan']
        df_limpo = df_fd[~df_fd['ID'].isin(valores_remocao) & ~df_fd['Order_Date'].isin(valores_remocao)]
    
        #GroupBy Orders per Day
        pedidos_por_dia = (
        df_limpo.groupby('Order_Date')['ID']
        .count()
        .reset_index()
        .rename(columns={'Order_Date': 'Data', 'ID': 'Total_Pedidos'})
        .sort_values(by = 'Total_Pedidos', ascending=False)
        )
    
        #Plot Bar Chart - Orders per Day
        fig_bar = px.bar(pedidos_por_dia, x='Data', y='Total_Pedidos')
        st.plotly_chart (fig_bar, use_container_width=True)
    
    with st.container():
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown ('# Trafic Order Share')
            #Clean NaN
            valores_remocao = ['NaN','conditions NaN', 'nan']
            df_limpo = df_fd[~df_fd['ID'].isin(valores_remocao) & ~df_fd['Road_traffic_density'].isin(valores_remocao)]

            # Order by Traffic
            pedidos_por_trafego = (
            df_limpo.groupby('Road_traffic_density')['ID']
            .count()
            .reset_index()
            .rename(columns={'Road_traffic_density': 'Trafego', 'ID': 'Total_Pedidos'})
            .sort_values(by = 'Total_Pedidos', ascending=False)
            )

            #Chart Traffic Pie
            pedidos_por_trafego['pct_pedidos'] = (pedidos_por_trafego['Total_Pedidos'] / pedidos_por_trafego['Total_Pedidos'].sum()) * 100
            fig_pie = px.pie(pedidos_por_trafego, values='pct_pedidos', names='Trafego')
            st.plotly_chart (fig_pie, use_container_width=True)
            
        
        with col2:
            st.markdown ('# City and Trafic Order Share')
            
            #Clean NaN
            valores_remocao = ['NaN','conditions NaN', 'nan']
            df_limpo = df_fd[~df_fd['ID'].isin(valores_remocao) & ~df_fd['Road_traffic_density'].isin(valores_remocao) & ~df_fd['City'].isin(valores_remocao)]

            #Order by City and Traffic
            pedidos_por_cidade_trafego = (
            df_limpo.groupby(['City', 'Road_traffic_density'])['ID']
            .count()
            .reset_index()
            .rename(columns={'City': 'Cidade', 'Road_traffic_density' : 'Trafego', 'ID': 'Total_Pedidos'})
            .sort_values(by = 'Total_Pedidos', ascending=False)
        )

            #Scatter Chart - City and Traffic
            fig_scatter = px.scatter(pedidos_por_cidade_trafego, x='Cidade', y='Trafego', size='Total_Pedidos', color='Cidade')
            st.plotly_chart (fig_scatter, use_container_width=True)
    
    
with tab2:
    st.markdown(" Teste 02")
    
    #Clean NaN
    valores_remocao = ['NaN','conditions NaN', 'nan']
    df_limpo = df_fd[~df_fd['ID'].isin(valores_remocao) & ~df_fd['Order_Date'].isin(valores_remocao)]
    
    #Order by Week
    pedidos_por_semana = (
    df_limpo.groupby(pd.Grouper(key='Order_Date', freq='W'))['ID']
    .count()
    .reset_index()
    .rename(columns={'Order_Date': 'Inicio_Semana', 'ID': 'Total_Pedidos'})
    .sort_values(by = 'Inicio_Semana', ascending=True)
    )
    
    #Line Chart Order by Week
    pedidos_por_semana['Num_Semana'] = pedidos_por_semana['Inicio_Semana'].dt.isocalendar().week
    fig_line = px.line(pedidos_por_semana, x='Num_Semana', y='Total_Pedidos')
    st.plotly_chart (fig_line, use_container_width = True)