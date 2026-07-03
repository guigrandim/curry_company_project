#===========================================
# Import Libraries
#===========================================

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.utils import load_data, build_sidebar

#===========================================
# Configuration Page
#===========================================

st.set_page_config(page_title='Visão Restaurantes', page_icon='🍽️', layout="wide")

#===========================================
# Visual settings
#===========================================
TEMPLATE = 'plotly_white'
CITY_COLORS = {'Urban': '#EF553B', 'Metropolitian': '#636EFA', 'Semi-Urban': '#00CC96'}

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
                      color_continuous_midpoint=np.average(tempo_medio_cidade_trafego['dp_tempo']),
                      title='Tempo Médio de Entrega por Cidade e Tráfego', template=TEMPLATE)

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

    cores = [CITY_COLORS.get(cidade, '#636EFA') for cidade in tempo_medio_entrega_cidade['cidade']]

    fig = go.Figure()
    fig.add_trace(go.Bar(name='Tempo Médio', x=tempo_medio_entrega_cidade['cidade'], y=tempo_medio_entrega_cidade['tempo_medio_entregas'],
                         marker_color=cores,
                         error_y=dict(type='data', array=tempo_medio_entrega_cidade['dp_entregas'])))
    fig.update_layout(
        title='Tempo Médio de Entrega por Cidade', template=TEMPLATE,
        yaxis_title='Tempo Médio (min)', xaxis_title='Cidade', showlegend=False
    )
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

    cores = [CITY_COLORS.get(cidade, '#636EFA') for cidade in distancia_restaurante_cidade['City']]

    fig = go.Figure(data=[go.Pie(labels=distancia_restaurante_cidade['City'],
                                     values=distancia_restaurante_cidade['distancia_media'],
                                     textinfo='label+percent',
                                     insidetextorientation='radial',
                                     hole=0.45,
                                     marker=dict(colors=cores))])
    fig.update_layout(title='Distância Média por Cidade', template=TEMPLATE)

    return fig, distancia_restaurante_cidade

def festival_stats(df_fd, festival_selecionado):
    festival_map = {'Sim': 'Yes', 'Não': 'No'}

    dados = df_fd if festival_selecionado == 'Todos' else df_fd.loc[df_fd['Festival'] == festival_map[festival_selecionado], :]

    tempo_medio = dados['Time_taken(min)'].mean().round(2)
    dp_tempo = dados['Time_taken(min)'].std().round(2)
    coef_variacao = round((dp_tempo / tempo_medio) * 100, 2)

    clas_cv = [0, 15, 30, 50, 100]
    labels = ["💎 Muito Consistente", "✅ Aceitável", "⚠️ Instável", "🚨 Crítico"]
    estabilidade = pd.cut([coef_variacao], bins=clas_cv, labels=labels)[0]

    return tempo_medio, dp_tempo, estabilidade

#----------------------------------------- Beginning of the logical structure code --------------------- #

#===========================================
# Load and clean dataset
#===========================================

df_fd = load_data()

#===========================================
# STEP 2: Create a Sidebar and Header - Streamlit
#===========================================

st.header ('Marketplace - Visão do Restaurante')

df_fd = build_sidebar(df_fd)

#===========================================
# STEP 3: Create a Body - Streamlit
#===========================================

#Header Cards Main Page

festival_selecionado = st.radio('Festival', ['Todos', 'Sim', 'Não'], horizontal=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    with st.container(border=True):
        #Filter By Unique Delivery
        entregadores_unicos = len(df_fd.loc[:,'Delivery_person_ID'].unique())
        col1.metric('🚴 Entregadores na Base', entregadores_unicos)

with col2:
    with st.container(border=True):
        distancia_media_geral = df_fd['distancia_km'].mean().round(0)
        col2.metric('📏 Distância Média [Km]', distancia_media_geral)

with col3:
    with st.container(border=True):
        tempo_medio, dp_tempo, estabilidade = festival_stats(df_fd, festival_selecionado)
        col3.metric(label = f'⏱️ Tempo Médio de Entrega [min]\n\nFestival: {festival_selecionado}',
                    value = tempo_medio,
                    delta = estabilidade,
                    delta_color = "off",
                    delta_arrow="off")

with col4:
    with st.container(border=True):
        col4.metric(label = f'📊 DP Tempo de Entrega [min]\n\nFestival: {festival_selecionado}',
                    value = dp_tempo)

st.markdown("""___""")

#Pie Chart - Order by Time Delivry by City

with st.container(border=True):
    fig, distancia_restaurante_cidade = restaurante_distance (df_fd)
    st.plotly_chart(fig, use_container_width=True)
    with st.expander("Ver dados detalhados"):
        st.dataframe(distancia_restaurante_cidade, use_container_width=True)

st.markdown("""___""")

#Two Charts - First Chart (Bar Chart - Mean and Std) and Second Chart (Sunburst Chart)

col1, col2 = st.columns([1,2])

with col1:
    with st.container(border=True):
        fig = delivery_mean_city (df_fd)
        st.plotly_chart(fig, use_container_width=True)

with col2:
    with st.container(border=True):
        tempo_medio_cidade_tipo = time_city_order (df_fd)
        st.markdown("##### Tempo Médio por Tipo de Entrega")
        st.dataframe(tempo_medio_cidade_tipo, use_container_width=True)

with st.container(border=True):
    fig, tempo_medio_cidade_trafego = traffic_city_mean (df_fd)
    st.plotly_chart(fig, use_container_width=True)
    with st.expander("Ver dados detalhados"):
        st.dataframe(tempo_medio_cidade_trafego, use_container_width=True)
