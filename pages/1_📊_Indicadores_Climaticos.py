import pandas as pd
import streamlit as st

st.set_page_config(page_title="Indicadores Climáticos", page_icon="📊", layout="wide")


@st.cache_data
def carregar_dados_climaticos():
    datas = pd.date_range(start="2024-01-01", periods=10, freq="D")
    dados = {
        "Data": list(datas) * 3,
        "Cidade": ["São Paulo"] * 10 + ["Rio de Janeiro"] * 10 + ["Curitiba"] * 10,
        "Temperatura": [
            25.4, 26.1, 24.8, 27.0, 25.9, 28.0, 27.5, 26.8, 25.0, 26.5,
            31.2, 30.5, 32.0, 29.8, 31.0, 33.1, 32.5, 30.8, 31.4, 32.0,
            18.5, 19.0, 17.8, 20.2, 19.5, 21.0, 18.9, 17.5, 19.8, 20.0
        ],
        "Umidade": [
            78, 72, 80, 68, 75, 70, 74, 79, 81, 76,
            60, 65, 58, 62, 64, 59, 61, 66, 63, 60,
            85, 88, 82, 79, 84, 80, 86, 89, 83, 81
        ],
    }
    return pd.DataFrame(dados)


df_clima = carregar_dados_climaticos()

st.title("📊 Indicadores Climáticos")

# Filtros na barra lateral
st.sidebar.header("🔍 Filtros de Visualização")
cidades = ["Todas"] + list(df_clima["Cidade"].unique())
cidade_sel = st.sidebar.selectbox("Selecione a Cidade:", cidades)
indicador_sel = st.sidebar.radio("Selecione o Indicador:", ["Temperatura", "Umidade"])

# Aplicação do filtro
df_filtrado = df_clima.copy()
if cidade_sel != "Todas":
    df_filtrado = df_filtrado[df_filtrado["Cidade"] == cidade_sel]

# Exibição de Métricas
col1, col2 = st.columns(2)
col1.metric("Temperatura Média", f"{df_filtrado['Temperatura'].mean():.1f} °C")
col2.metric("Umidade Média", f"{df_filtrado['Umidade'].mean():.1f} %")

st.markdown("---")
st.markdown("### Gráfico Temporal")

if cidade_sel == "Todas":
    df_pivot = df_filtrado.pivot_table(index="Data", columns="Cidade", values=indicador_sel)
    st.line_chart(df_pivot)
else:
    st.line_chart(df_filtrado.set_index("Data")[indicador_sel])