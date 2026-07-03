#===========================================
# Import Libraries
#===========================================

import pandas as pd
import plotly.express as px
import streamlit as st

from src.utils import load_data, build_sidebar, guard_empty_dataframe, format_number_ptbr

#===========================================
# Configuration Page
#===========================================

st.set_page_config(page_title='Visão Empresa', page_icon='📈', layout="wide")

#===========================================
# Visual settings
#===========================================
TEMPLATE = 'plotly_dark'
CITY_COLORS = {'Urban': '#EF553B', 'Metropolitian': '#636EFA', 'Semi-Urban': '#00CC96'}
TRAFFIC_COLORS = {'Low': '#00CC96', 'Medium': '#FFA15A', 'High': '#EF553B', 'Jam': '#AB63FA'}

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
    fig = px.line(
        pedidos_por_semana, x='Num_Semana', y='Total_Pedidos', markers=True,
        title='Pedidos por Semana do Ano', labels={'Num_Semana': 'Semana', 'Total_Pedidos': 'Total de Pedidos'},
        template=TEMPLATE
    )
    fig.update_traces(line_color='#636EFA')

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
    fig = px.scatter(
        pedidos_por_cidade_trafego, x='Cidade', y='Trafego', size='Total_Pedidos', color='Cidade',
        color_discrete_map=CITY_COLORS, size_max=45,
        title='Pedidos por Cidade e Tráfego', template=TEMPLATE
    )

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
    fig = px.pie(
        pedidos_por_trafego, values='pct_pedidos', names='Trafego', hole=0.45,
        color='Trafego', color_discrete_map=TRAFFIC_COLORS,
        title='Distribuição de Pedidos por Tráfego', template=TEMPLATE
    )
    fig.update_traces(textinfo='label+percent')

    return fig

def delivery_locations_map(df_fd):
    # Coordenadas fora da faixa geográfica da Índia continental são erro de
    # coleta (ex.: latitude negativa, "null island" perto de 0,0) e distorcem o mapa.
    localizacoes = df_fd.loc[
        df_fd['Delivery_location_latitude'].between(6, 38)
        & df_fd['Delivery_location_longitude'].between(68, 98),
        ['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude']
    ].rename(columns={
        'City': 'Cidade',
        'Road_traffic_density': 'Trafego',
        'Delivery_location_latitude': 'lat',
        'Delivery_location_longitude': 'lon'
    })

    fig = px.scatter_mapbox(
        localizacoes, lat='lat', lon='lon', color='Cidade',
        color_discrete_map=CITY_COLORS, hover_data=['Trafego'], zoom=3, height=550
    )
    fig.update_layout(mapbox_style='open-street-map', margin={'r': 0, 't': 0, 'l': 0, 'b': 0})

    return fig, localizacoes


def order_metric(df_fd):
    pedidos_por_dia = (
    df_fd.groupby('Order_Date')['ID']
    .count()
    .reset_index()
    .rename(columns={'Order_Date': 'Data', 'ID': 'Total_Pedidos'})
    .sort_values(by = 'Total_Pedidos', ascending=False)
    )

    #Plot Bar Chart - Orders per Day
    fig = px.bar(
        pedidos_por_dia, x='Data', y='Total_Pedidos', color='Total_Pedidos',
        color_continuous_scale='Blues', title='Pedidos por Dia',
        labels={'Total_Pedidos': 'Total de Pedidos'}, template=TEMPLATE
    )
    fig.update_layout(coloraxis_showscale=False)

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
guard_empty_dataframe(df_fd)

#===========================================
# STEP 3: Create a Body - Streamlit
#===========================================

#KPI Cards - Visão Geral do Negócio

col1, col2, col3, col4 = st.columns(4)

with col1:
    with st.container(border=True):
        total_pedidos = len(df_fd)
        col1.metric('📦 Total de Pedidos', format_number_ptbr(total_pedidos),
                    help='Quantidade de pedidos após limpeza dos dados, dentro do período e tráfego selecionados.')

with col2:
    with st.container(border=True):
        total_entregadores = df_fd['Delivery_person_ID'].nunique()
        col2.metric('🚴 Total de Entregadores', format_number_ptbr(total_entregadores),
                    help='Número de entregadores únicos (Delivery_person_ID) nos pedidos filtrados.')

with col3:
    with st.container(border=True):
        avaliacao_media_entregadores = df_fd['Delivery_person_Ratings'].mean().round(2)
        col3.metric('⭐ Avaliação Média dos Entregadores', format_number_ptbr(avaliacao_media_entregadores, 2),
                    help='Média simples de Delivery_person_Ratings nos pedidos filtrados.')

with col4:
    with st.container(border=True):
        meta_sla_min = 30
        pct_dentro_sla = (df_fd['Time_taken(min)'] <= meta_sla_min).mean() * 100
        col4.metric(f'✅ Pedidos dentro do SLA (≤{meta_sla_min} min)', f'{format_number_ptbr(pct_dentro_sla, 1)}%',
                    help=f'Percentual de pedidos entregues em até {meta_sla_min} minutos (meta fixa de negócio).')

st.markdown("""___""")

tab1, tab2, tab3 = st.tabs(['📈 Visão Gerencial', '📅 Visão Tática', '🗺️ Visão Geográfica'])

with tab1:
    with st.container(border=True):
        fig = order_metric(df_fd)
        st.plotly_chart (fig, use_container_width=True)

    col1, col2 = st.columns(2)

    with col1:
        with st.container(border=True):
            fig = traffic_order_share(df_fd)
            st.plotly_chart (fig, use_container_width=True)

    with col2:
        with st.container(border=True):
            fig = traffic_city_order_share(df_fd)
            st.plotly_chart (fig, use_container_width=True)

with tab2:
    with st.container(border=True):
        fig = orders_per_week (df_fd)
        st.plotly_chart (fig, use_container_width = True)

with tab3:
    with st.container(border=True):
        fig, localizacoes = delivery_locations_map(df_fd)
        st.caption(f"Localização das Entregas por Cidade e Tráfego ({len(localizacoes)} pontos válidos)")
        st.plotly_chart(fig, use_container_width=True)
