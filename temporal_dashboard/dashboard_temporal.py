import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium

# Configuração da página
st.set_page_config(layout="wide", page_title="Dashboard Temporal com Granizo")

# Título e descrição
st.title("Dashboard: Impactos do Temporal com Granizo")
st.markdown("Análise dos impactos do temporal com granizo em uma comunidade escolar, com visualizações interativas e mapa geolocalizado.")

# Função para carregar e processar os dados
@st.cache_data
def load_data(file_path):
    try:
        # Lê o arquivo CSV
        data = pd.read_csv(file_path)
        # Renomear colunas para padronizar (ajuste conforme seu CSV)
        data.columns = ['ID', 'Turma', 'QtdEntrevistados', 'MoraCasa', 'MoraApto', 'DanosResidencia',
                       'DanoLeve', 'DanoMedio', 'DanoSevero', 'CarroDanificado', 'SeguroCarro',
                       'SeguroResidencia', 'EletroouMoveisDanificados', 'ConseguiuLonaManta',
                       'ConheceValorPrejuizo', 'ValorPrejuizoReais', 'ConsertoDefinitivo',
                       'ConsertocomTelha', 'ConsertocomBrasilite', 'ConsertocomAluzinco',
                       'NaoConsertouNaoSabe', 'AfetouSaudeMental', 'AlguemDesalojado',
                       'AjudouVoluntariamente', 'Regiao1', 'Regiao2', 'Regiao3', 'Regiao4',
                       'Regiao5', 'Regiao6']
        # Tratamento de valores ausentes
        data = data.fillna(0)
        return data
    except Exception as e:
        st.error(f"Erro ao carregar o arquivo: {e}")
        return pd.DataFrame()

# Função para calcular percentuais
def calc_percent(df, col):
    return (df[col].sum() / df['QtdEntrevistados'].sum()) * 100

# Função para criar gráfico de barras empilhadas
def stacked_bar(df, x_col, y_cols, title):
    fig = px.bar(df, x=x_col, y=y_cols, title=title, barmode='stack')
    fig.update_layout(xaxis_title="Turma", yaxis_title="Quantidade")
    return fig

# Função para criar gráfico de pizza
def pie_chart(df, col, title):
    labels = ['Sim', 'Não']
    values = [df[col].sum(), df['QtdEntrevistados'].sum() - df[col].sum()]
    fig = px.pie(names=labels, values=values, title=title)
    return fig

# Função para criar mapa Folium
def create_map(df):
    # Coordenadas das regiões
    coords = {
        'Regiao1': (-27.644250, -52.304118),
        'Regiao2': (-27.647053, -52.284419),
        'Regiao3': (-27.630867, -52.252368),
        'Regiao4': (-27.643165, -52.232465),
        'Regiao5': (-27.659349, -52.256860),
        'Regiao6': (-27.588844, -52.257941)
    }
    # Criar mapa centralizado
    m = folium.Map(location=[-27.64, -52.28], zoom_start=12)
    for reg in coords:
        lat, lon = coords[reg]
        # Tamanho do bubble proporcional ao número de entrevistados na região
        size = df[reg].sum() * 5
        folium.CircleMarker(
            location=[lat, lon],
            radius=size,
            popup=f"{reg}: {df[reg].sum()} alunos",
            color='red',
            fill=True,
            fill_color='red'
        ).add_to(m)
    return m

# Carregar dados
uploaded_file = st.sidebar.file_uploader("Carregar arquivo CSV", type=["csv"])
if uploaded_file is not None:
    df = load_data(uploaded_file)
else:
    st.warning("Por favor, carregue o arquivo CSV para continuar.")
    st.stop()

# Filtro por turma
if 'Turma' not in df.columns:
    st.error("A coluna 'Turma' não foi encontrada. Verifique o nome no CSV.")
    st.stop()

turmas = df['Turma'].unique()
selected_turmas = st.sidebar.multiselect("Selecione as turmas", turmas, default=turmas)
df_filtered = df[df['Turma'].isin(selected_turmas)]

# Métricas-chave (KPIs)
st.header("Métricas-Chave")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total de Alunos", df_filtered['QtdEntrevistados'].sum())
col2.metric("Danos Residência (%)", f"{calc_percent(df_filtered, 'DanosResidencia'):.1f}")
col3.metric("Seguro Carro (%)", f"{calc_percent(df_filtered, 'SeguroCarro'):.1f}")
col4.metric("Seguro Residência (%)", f"{calc_percent(df_filtered, 'SeguroResidencia'):.1f}")

# Seções do dashboard
tab1, tab2, tab3, tab4 = st.tabs(["Danos", "Seguros", "Recuperação", "Mapa"])

# Tab 1: Danos
with tab1:
    st.subheader("Distribuição de Danos")
    fig1 = px.bar(df_filtered, x='Turma', y=['MoraCasa', 'MoraApto'], title="Tipo de Moradia por Turma", barmode='group')
    st.plotly_chart(fig1, use_container_width=True)
    fig2 = stacked_bar(df_filtered, 'Turma', ['DanoLeve', 'DanoMedio', 'DanoSevero'], "Níveis de Dano por Turma")
    st.plotly_chart(fig2, use_container_width=True)
    fig3 = px.bar(df_filtered, x='Turma', y=['DanosResidencia', 'CarroDanificado', 'EletroouMoveisDanificados'],
                  title="Danos em Categorias", barmode='group')
    st.plotly_chart(fig3, use_container_width=True)

# Tab 2: Seguros
with tab2:
    st.subheader("Cobertura de Seguros")
    fig4 = pie_chart(df_filtered, 'SeguroCarro', "Cobertura de Seguro para Carro")
    st.plotly_chart(fig4, use_container_width=True)
    fig5 = pie_chart(df_filtered, 'SeguroResidencia', "Cobertura de Seguro para Residência")
    st.plotly_chart(fig5, use_container_width=True)

# Tab 3: Recuperação
with tab3:
    st.subheader("Recuperação e Recursos")
    fig6 = px.bar(df_filtered, x=['ConsertoDefinitivo', 'NaoConsertouNaoSabe'], y='Turma', orientation='h', title="Tipo de Conserto")
    st.plotly_chart(fig6, use_container_width=True)
    fig7 = px.bar(df_filtered, x='Turma', y=['ConsertocomTelha', 'ConsertocomBrasilite', 'ConsertocomAluzinco', 'NaoConsertouNaoSabe'],
                  title="Materiais Usados para Cobertura de Telhado", barmode='stack')
    st.plotly_chart(fig7, use_container_width=True)

# Tab 4: Mapa
with tab4:
    st.subheader("Mapa de Impacto")
    mapa = create_map(df_filtered)
    st_folium(mapa, width=700, height=500)

# Rodapé
st.markdown("---")
st.markdown("Dashboard desenvolvido com Streamlit, Plotly, Folium e Pandas. Todos os dados são fictícios para demonstração.")
