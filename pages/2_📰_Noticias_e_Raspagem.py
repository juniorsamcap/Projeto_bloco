import os
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Notícias Climáticas", page_icon="📰", layout="wide")


@st.cache_data
def carregar_noticias():
    caminho_csv = os.path.join("data", "noticias.csv")
    if os.path.exists(caminho_csv):
        return pd.read_csv(caminho_csv)
    return pd.DataFrame()


df_noticias = carregar_noticias()

st.title("📰 Notícias & Raspagem Web")
st.caption("Dados raspados automaticamente e armazenados em `data/noticias.csv`.")

if not df_noticias.empty:
    col1, col2, col3 = st.columns(3)
    col1.metric("Total de Notícias Coletadas", len(df_noticias))
    col2.metric("Média de Palavras por Título", f"{df_noticias['Qtd_Palavras'].mean():.1f}")
    col3.metric("Maior Título (Caracteres)", df_noticias["Tamanho_Titulo"].max())

    st.markdown("---")
    st.markdown("### Tabela de Headlines Coletadas")
    st.dataframe(df_noticias[["Titulo", "Qtd_Palavras"]], use_container_width=True)
else:
    st.warning("Nenhum dado encontrado. Execute o script `coleta_dados.py` para gerar o arquivo de notícias.")