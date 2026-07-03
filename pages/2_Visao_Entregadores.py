#===========================================
# Import Libraries
#===========================================

import plotly.express as px
import streamlit as st

from src.utils import load_data, build_sidebar

#===========================================
# Configuration Page
#===========================================

st.set_page_config(page_title='Visão Entregadores', page_icon='🚲', layout="wide")

#===========================================
# Visual settings
#===========================================
TEMPLATE = 'plotly_white'
TRAFFIC_COLORS = {'Low': '#00CC96', 'Medium': '#FFA15A', 'High': '#EF553B', 'Jam': '#AB63FA'}

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

#----------------------------------------- Beginning of the logical structure code --------------------- #

#===========================================
# Load and clean dataset
#===========================================

df_fd = load_data()

#===========================================
# STEP 2: Create a Sidebar and Header - Streamlit
#===========================================

st.header ('Marketplace - Visão do entregador')

df_fd = build_sidebar(df_fd)

#===========================================
# STEP 3: Create a Body - Streamlit
#===========================================

#Added Cards on the top of the page
col1, col2, col3 = st.columns(3)

with col1:
    with st.container(border=True):
        maior_idade = df_fd.loc[:, 'Delivery_person_Age'].max()
        col1.metric('👴 Idade Entregador Mais Velho', maior_idade)

with col2:
    with st.container(border=True):
        menor_idade = df_fd.loc[:, 'Delivery_person_Age'].min()
        col2.metric('👶 Idade Entregador Mais Novo', menor_idade)

with col3:
    with st.container(border=True):
        media_qualidade_frota, qualidade_frota = quality_fleet_delivery(df_fd)
        col3.metric('🛵 Qualidade da Frota', qualidade_frota, media_qualidade_frota, delta_color = "off")
        col3.caption('Faixas (média de Vehicle_condition, escala 0-3): 🟢 >3 Excelente · 🟡 >2 Bom · 🟠 >1 Médio · 🔴 ≤1 Ruim')

st.markdown("""___""")

#Added Cointainer with tree charts (one on left and two on right)

col5, col6 = st.columns([1,1])

with col5:
    with st.container(border=True):
        avaliacao_media_por_entregador = delivery_id_rating (df_fd)
        st.markdown("##### ⭐ Avaliação por Entregador")
        st.dataframe(avaliacao_media_por_entregador, width=500, height=460, use_container_width=True)

with col6:
    with st.container(border=True):
        avaliacao_media_por_trafego = delivery_traffic_rating (df_fd)
        fig = px.bar(
            avaliacao_media_por_trafego, x='Trafego', y='media_avaliacao_entrega',
            error_y='dp_avaliacao_entrega', color='Trafego', color_discrete_map=TRAFFIC_COLORS,
            title='Avaliação Média por Tráfego', labels={'media_avaliacao_entrega': 'Avaliação Média'},
            template=TEMPLATE
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with st.container(border=True):
        avaliacao_media_por_clima = delivery_weather_rating (df_fd)
        fig = px.bar(
            avaliacao_media_por_clima, x='Clima', y='Media_Avaliação', error_y='DP_Avaliação',
            color='Media_Avaliação', color_continuous_scale='Blues',
            title='Avaliação Média por Clima', template=TEMPLATE
        )
        fig.update_layout(coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

st.markdown("""___""")

#Added two charts in end of the page

col7, col8 = st.columns(2)

with col7:
    with st.container(border=True):
        entregadores_mais_rapidos_cidade = speed_delivery (df_fd, 'mais rapido')
        st.markdown("##### 🚀 Entregadores Mais Rápidos por Cidade")
        st.dataframe(entregadores_mais_rapidos_cidade, use_container_width = True)

with col8:
    with st.container(border=True):
        entregadores_mais_lentos_cidade = speed_delivery (df_fd, 'mais lento')
        st.markdown("##### 🐢 Entregadores Mais Lentos por Cidade")
        st.dataframe(entregadores_mais_lentos_cidade, use_container_width = True)
