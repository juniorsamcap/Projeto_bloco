import os
import streamlit as st
import pandas as pd
import numpy as np

# Configuração da página
st.set_page_config(
    page_title="Dashboard ODS 13 - Clima",
    page_icon="🌍",
    layout="wide"
)

# Título Principal
st.title("🌍 Dashboard ODS 13 - Monitoramento Climático")
st.markdown("Acompanhe os indicadores meteorológicos e notícias sobre o meio ambiente.")

# --- CARREGAR DADOS METEOROLÓGICOS (Simulados) ---
@st.cache_data
def carregar_dados_clima():
    datas = pd.date_range(start="2024-01-01", end="2024-06-30", freq="D")
    np.random.seed(42)
    dados = []
    cidades = ["São Paulo", "Rio de Janeiro", "Curitiba"]
    for cidade in cidades:
        temp_base = 22 if cidade == "São Paulo" else (26 if cidade == "Rio de Janeiro" else 18)
        temperaturas = temp_base + np.random.normal(0, 3, len(datas))
        umidades = 70 + np.random.normal(0, 10, len(datas))
        for d, t, u in zip(datas, temperaturas, umidades):
            dados.append({
                "Data": d.date(),
                "Cidade": cidade,
                "Temperatura (°C)": round(t, 1),
                "Umidade (%)": round(min(max(u, 30), 100), 1)
            })
    return pd.DataFrame(dados)

df_clima = carregar_dados_clima()

# --- CARREGAR DADOS EXTRAÍDOS DA WEB (BeautifulSoup) ---
@st.cache_data
def carregar_noticias():
    caminho = os.path.join("data", "noticias.csv")
    if os.path.exists(caminho):
        return pd.read_csv(caminho)
    return pd.DataFrame()

df_noticias = carregar_noticias()

# --- CRIAÇÃO DE ABAS NA INTERFACE ---
aba1, aba2 = st.tabs(["📊 Indicadores Climáticos", "📰 Notícias & Raspagem Web"])

# ================= ABA 1: CLIMA =================
with aba1:
    st.sidebar.header("🔍 Filtros de Visualização")
    cidade_selecionada = st.sidebar.selectbox("Selecione a Cidade:", options=df_clima["Cidade"].unique())
    indicador_selecionado = st.sidebar.radio("Selecione o Indicador:", options=["Temperatura (°C)", "Umidade (%)"])

    df_filtrado = df_clima[df_clima["Cidade"] == cidade_selecionada]

    st.subheader(f"Análise de {indicador_selecionado} - {cidade_selecionada}")
    
    col1, col2, col3 = st.columns(3)
    col1.metric(f"Média", f"{df_filtrado[indicador_selecionado].mean():.1f}")
    col2.metric(f"Máxima", f"{df_filtrado[indicador_selecionado].max():.1f}")
    col3.metric(f"Mínima", f"{df_filtrado[indicador_selecionado].min():.1f}")

    st.divider()
    st.line_chart(data=df_filtrado, x="Data", y=indicador_selecionado, use_container_width=True)

# ================= ABA 2: NOTÍCIAS RASPADAS =================
with aba2:
    st.subheader("📰 Conteúdo Extraído da Web (BeautifulSoup)")
    st.write("Dados raspados automaticamente e armazenados em `data/noticias.csv`.")

    if not df_noticias.empty:
        # Estatísticas Básicas das Notícias
        m1, m2, m3 = st.columns(3)
        m1.metric("Total de Notícias Coletadas", len(df_noticias))
        m2.metric("Média de Palavras por Título", f"{df_noticias['Qtd_Palavras'].mean():.1f}")
        m3.metric("Maior Título (Caracteres)", df_noticias["Tamanho_Titulo"].max())

        st.divider()

        # Tabela com as Notícias
        st.write("### Tabela de Headlines")
        st.dataframe(df_noticias[["Titulo", "Qtd_Palavras"]], use_container_width=True)
    else:
        st.warning("Nenhum dado encontrado. Execute o arquivo 'coleta_dados.py' no terminal para gerar o CSV.")