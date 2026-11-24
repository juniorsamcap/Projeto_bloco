import plotly.express as px
import streamlit as st

import clima_service

st.set_page_config(page_title="Indicadores Climáticos", page_icon="📊", layout="wide")

# Nome que aparece na tela -> coluna da tabela
INDICADORES = {
    "Temperatura (°C)": "Temperatura",
    "Umidade (%)": "Umidade",
    "Chuva (mm)": "Chuva_mm",
}

# Uma cor fixa para cada cidade, igual em todos os gráficos
CORES = {
    "São Paulo": "#F28E2B",
    "Rio de Janeiro": "#4E79A7",
    "Curitiba": "#59A14F",
}


# Guarda o resultado por 1 hora para não chamar a API a cada clique
@st.cache_data(ttl=3600)
def obter_dados(dias):
    return clima_service.carregar_clima(dias)


st.title("📊 Indicadores Climáticos")
st.caption("Dados reais diários de temperatura, umidade e chuva em três capitais do Sul e Sudeste.")

# Filtros na barra lateral
st.sidebar.header("🔍 Filtros de Visualização")
dias = st.sidebar.slider("Período (últimos dias):", min_value=7, max_value=30, value=14)
if st.sidebar.button("🔄 Atualizar dados"):
    obter_dados.clear()

try:
    df_clima, origem = obter_dados(dias)
except Exception as erro:
    st.error(f"Não foi possível obter os dados climáticos e não há arquivo salvo: {erro}")
    st.stop()

if origem.startswith("Open-Meteo"):
    st.success(f"Fonte dos dados: {origem}")
else:
    st.warning(f"Fonte dos dados: {origem}")

cidades = ["Todas"] + list(df_clima["Cidade"].unique())
cidade_sel = st.sidebar.selectbox("Selecione a Cidade:", cidades)
indicador_nome = st.sidebar.radio("Selecione o Indicador:", list(INDICADORES.keys()))
indicador_sel = INDICADORES[indicador_nome]

# Aplicação do filtro
df_filtrado = df_clima.copy()
if cidade_sel != "Todas":
    df_filtrado = df_filtrado[df_filtrado["Cidade"] == cidade_sel]

# Exibição de métricas
# Na chuva, quando são todas as cidades, mostro a média do acumulado entre elas
chuva_acumulada = df_filtrado.groupby("Cidade")["Chuva_mm"].sum().mean()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Temperatura Média", f"{df_filtrado['Temperatura'].mean():.1f} °C")
col2.metric("Maior Temperatura", f"{df_filtrado['Temp_Maxima'].max():.1f} °C")
col3.metric("Umidade Média", f"{df_filtrado['Umidade'].mean():.1f} %")
col4.metric("Chuva Acumulada", f"{chuva_acumulada:.1f} mm")

st.markdown("---")
st.markdown(f"### Gráfico Temporal: {indicador_nome}")

# Chuva fica mais fácil de ler em barras; temperatura e umidade em linha
if indicador_sel == "Chuva_mm":
    grafico = px.bar(
        df_filtrado, x="Data", y=indicador_sel, color="Cidade",
        barmode="group", color_discrete_map=CORES,
    )
else:
    grafico = px.line(
        df_filtrado, x="Data", y=indicador_sel, color="Cidade",
        markers=True, color_discrete_map=CORES,
    )

# Datas no formato brasileiro (dia/mês), uma marcação por dia
grafico.update_xaxes(tickformat="%d/%m", dtick="D1", title="")
grafico.update_yaxes(title=indicador_nome)
grafico.update_layout(legend_title_text="Cidade", hovermode="x unified")
st.plotly_chart(grafico, width="stretch")

# Alertas do período
st.markdown("---")
st.markdown("### ⚠️ Alertas do Período")
st.caption(
    f"Dias com temperatura máxima a partir de {clima_service.LIMITE_CALOR:.0f} °C "
    f"ou chuva a partir de {clima_service.LIMITE_CHUVA:.0f} mm."
)

df_alertas = clima_service.identificar_alertas(df_filtrado)
if df_alertas.empty:
    st.info("Nenhum dia passou dos limites de alerta no período selecionado.")
else:
    df_alertas["Data"] = df_alertas["Data"].dt.strftime("%d/%m/%Y")
    st.dataframe(df_alertas, hide_index=True, width="stretch")

with st.expander("Ver tabela completa dos dados"):
    df_tabela = df_filtrado.copy()
    df_tabela["Data"] = df_tabela["Data"].dt.strftime("%d/%m/%Y")
    st.dataframe(df_tabela, hide_index=True, width="stretch")

st.caption("Dados meteorológicos: [Open-Meteo.com](https://open-meteo.com/) (licença CC BY 4.0).")