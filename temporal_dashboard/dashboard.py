"""
Dashboard Interativo sobre Impactos do Temporal com Granizo
Desenvolvido em Streamlit
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium
import os
# =============================
# LEITURA DO ARQUIVO EXCEL REAL
# =============================

import pandas as pd
import streamlit as st
import os

@st.cache_data
def carregar_dados():
    arquivo = "Dados_21A.xlsx"

    # Verifica se o arquivo existe na pasta
    if not os.path.isfile(arquivo):
        st.error(f"❌ O arquivo '{arquivo}' não foi encontrado na pasta do dashboard.")
        st.stop()

    try:
        df = pd.read_excel(arquivo)
        st.success("✅ Dados carregados com sucesso!")
        return df
    except Exception as e:
        st.error("❌ Erro ao carregar os dados do Excel.")
        st.write(e)
        st.stop()

# Carrega os dados reais
df = carregar_dados()

# Caminho padrão do arquivo Excel
DEFAULT_FILE_PATH = r"C:\Users\gabri\Desktop\temporal_dashboard\Dados_21A.xlsx"

# Coordenadas das regiões (fixas)
REGIOES = {
    "Região 1": (-27.644250, -52.304118),
    "Região 2": (-27.647053, -52.284419),
    "Região 3": (-27.630867, -52.252368),
    "Região 4": (-27.643165, -52.232465),
    "Região 5": (-27.659349, -52.256860),
    "Zona Rural": (-27.588844, -52.257941),
}


# -------------------------------------
# FUNÇÃO PARA CARREGAR OU GERAR DADOS
# -------------------------------------
def load_data(path):
    """Carrega o Excel. Se não encontrar, gera dados de exemplo"""
    if os.path.exists(path):
        st.success("Arquivo Excel encontrado e carregado.")
        return pd.read_excel(path)
    else:
        st.warning("Arquivo não encontrado. Usando dados de exemplo.")
        return generate_example_data()


def generate_example_data():
    """Gera dados sintéticos se o Excel não existir"""
    df = pd.DataFrame({
        "Turma": [f"Turma {i}" for i in range(1, 11)],
        "Qtd_Entrevistados": np.random.randint(8, 14, 10),
        "Mora_Casa_Sim": np.random.randint(5, 14, 10),
        "Mora_Casa_Nao": np.random.randint(0, 5, 10),
        "Dano_Residencia_Sim": np.random.randint(2, 10, 10),
        "Dano_Residencia_Nao": np.random.randint(0, 8, 10),
        "Dano_Leve": np.random.randint(0, 8, 10),
        "Dano_Medio": np.random.randint(0, 4, 10),
        "Dano_Severo": np.random.randint(0, 3, 10),
        "Carro_Danificado_Sim": np.random.randint(0, 6, 10),
        "Carro_Danificado_Nao": np.random.randint(2, 14, 10),
        "Seguro_Carro_Sim": np.random.randint(0, 4, 10),
        "Seguro_Carro_Nao": np.random.randint(0, 6, 10),
        "Seguro_Casa_Sim": np.random.randint(0, 5, 10),
        "Seguro_Casa_Nao": np.random.randint(2, 10, 10),
        "Eletro_Danos_Sim": np.random.randint(0, 4, 10),
        "Eletro_Danos_Nao": np.random.randint(5, 14, 10),
        "Conserto_Temporario": np.random.randint(0, 8, 10),
        "Conserto_Definitivo": np.random.randint(0, 8, 10),
        "Material_Telha": np.random.randint(0, 5, 10),
        "Material_Brasilite": np.random.randint(0, 5, 10),
        "Material_Aluzinco": np.random.randint(0, 5, 10),
        "Material_Nao_Sabe": np.random.randint(0, 5, 10),
        "Afetou_Saude_Mental_Sim": np.random.randint(0, 6, 10),
        "Afetou_Saude_Mental_Nao": np.random.randint(3, 14, 10),
        "Desalojado_Sim": np.random.randint(0, 3, 10),
        "Desalojado_Nao": np.random.randint(6, 14, 10),
        "Ajudou_Sim": np.random.randint(3, 14, 10),
        "Ajudou_Nao": np.random.randint(0, 6, 10),
        "Regiao": np.random.choice(list(REGIOES.keys()), 10)
    })
    return df


# -------------------------
# GRÁFICOS
# -------------------------
def plot_moradia(df):
    dados = {
        "Tipo": ["Casa", "Apartamento/Outros"],
        "Quantidade": [df["Mora_Casa_Sim"].sum(), df["Mora_Casa_Nao"].sum()]
    }
    fig = px.bar(dados, x="Tipo", y="Quantidade", title="Distribuição de Moradia")
    return fig


def plot_niveis_dano(df):
    dados = {
        "Nível": ["Leve", "Médio", "Severo"],
        "Quantidade": [
            df["Dano_Leve"].sum(),
            df["Dano_Medio"].sum(),
            df["Dano_Severo"].sum(),
        ]
    }
    fig = px.bar(dados, x="Nível", y="Quantidade", title="Níveis de Dano")
    return fig


def plot_conserto(df):
    fig = px.bar(
        x=["Temporário", "Definitivo"],
        y=[df["Conserto_Temporario"].sum(), df["Conserto_Definitivo"].sum()],
        title="Tipo de Conserto"
    )
    return fig


def plot_materiais(df):
    dados = {
        "Material": ["Telha", "Brasilite", "Aluzinco", "Não sabe"],
        "Quantidade": [
            df["Material_Telha"].sum(),
            df["Material_Brasilite"].sum(),
            df["Material_Aluzinco"].sum(),
            df["Material_Nao_Sabe"].sum(),
        ]
    }
    fig = px.bar(dados, x="Material", y="Quantidade", title="Materiais Utilizados")
    return fig


def plot_mapa(df):
    mapa = folium.Map(location=(-27.63, -52.27), zoom_start=12)

    grupo = df.groupby("Regiao")["Dano_Residencia_Sim"].sum()

    for regiao, quantidade in grupo.items():
        lat, lon = REGIOES[regiao]
        folium.CircleMarker(
            location=(lat, lon),
            radius=6 + quantidade * 2,
            popup=f"{regiao}: {quantidade} danos",
            color="red",
            fill=True,
            fill_color="red"
        ).add_to(mapa)

    return mapa


# -------------------------
# LAYOUT DO DASHBOARD
# -------------------------
def main():
    st.title("Dashboard — Impactos do Temporal com Granizo")

    # Carregar dados
    df = load_data(DEFAULT_FILE_PATH)

    st.subheader("Tabela de Dados")
    st.dataframe(df)

    # Gráficos
    st.subheader("Distribuição de Moradia")
    st.plotly_chart(plot_moradia(df))

    st.subheader("Níveis de dano")
    st.plotly_chart(plot_niveis_dano(df))

    st.subheader("Tipos de conserto")
    st.plotly_chart(plot_conserto(df))

    st.subheader("Materiais usados no conserto")
    st.plotly_chart(plot_materiais(df))

    st.subheader("Mapa dos danos por região")
    mapa = plot_mapa(df)
    st_folium(mapa, width=800, height=500)


if __name__ == "__main__":
    main()
