#===========================================
# Import Libraries
#===========================================

import pandas as pd
import plotly.express as px
import streamlit as st

from src.utils import load_data, build_sidebar

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

#----------------------------------------- Beginning of the logical structure code --------------------- #

#===========================================
# Load and clean dataset
#===========================================

df_fd = load_data()

#===========================================
# STEP 2: Create a Sidebar and Header - Streamlit
#===========================================

st.header ('Marketplace - Visão da Empresa')

df_fd = build_sidebar(df_fd)

#===========================================
# STEP 3: Create a Body - Streamlit
#===========================================

#KPI Cards - Visão Geral do Negócio

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_pedidos = len(df_fd)
    col1.metric('Total de Pedidos', total_pedidos)

with col2:
    total_entregadores = df_fd['Delivery_person_ID'].nunique()
    col2.metric('Total de Entregadores', total_entregadores)

with col3:
    avaliacao_media_entregadores = df_fd['Delivery_person_Ratings'].mean().round(2)
    col3.metric('Avaliação Média dos Entregadores', avaliacao_media_entregadores)

with col4:
    meta_sla_min = 30
    pct_dentro_sla = (df_fd['Time_taken(min)'] <= meta_sla_min).mean() * 100
    col4.metric(f'Pedidos dentro do SLA (≤{meta_sla_min} min)', f'{pct_dentro_sla:.1f}%')

st.markdown("""___""")

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
