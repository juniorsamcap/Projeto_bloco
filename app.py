import os
import pandas as pd
import streamlit as st

# 1. Configuração da Página
st.set_page_config(
    page_title="Dashboard ODS 13 - Clima", page_icon="🌍", layout="wide"
)


# ==========================================
# 2. IMPLEMENTAÇÃO DE CACHE (@st.cache_data)
# ==========================================
# O decorator @st.cache_data garante que os dados só sejam lidos do disco 1 vez,
# economizando processamento a cada clique do usuário.
@st.cache_data
def carregar_dados_climaticos():
    # Simulação de base de dados climáticos (ODS 13)
    dados = {
        "Data": pd.date_range(start="2024-01-01", periods=10, freq="D"),
        "Cidade": ["São Paulo"] * 5 + ["Rio de Janeiro"] * 5,
        "Temperatura": [25.4, 26.1, 24.8, 27.0, 25.9, 31.2, 30.5, 32.0, 29.8, 31.0],
        "Umidade": [78, 72, 80, 68, 75, 60, 65, 58, 62, 64],
    }
    return pd.DataFrame(dados)


@st.cache_data
def carregar_noticias():
    caminho_csv = os.path.join("data", "noticias.csv")
    if os.path.exists(caminho_csv):
        return pd.read_csv(caminho_csv)
    return pd.DataFrame()


# Carregamento otimizado usando o cache
df_clima = carregar_dados_climaticos()
df_noticias = carregar_noticias()

# ===============================================
# 3. IMPLEMENTAÇÃO DE ESTADO DE SESSÃO (st.session_state)
# ===============================================
# O session_state mantém valores na memória enquanto o usuário navega na aplicação.
if "contador_interacoes" not in st.session_state:
    st.session_state.contador_interacoes = 0


def registrar_interacao():
    st.session_state.contador_interacoes += 1


# ==========================================
# 4. INTERFACE DO USUÁRIO & BARRA LATERAL
# ==========================================
st.title("🌍 Dashboard ODS 13 - Monitoramento Climático")
st.markdown(
    "Acompanhe os indicadores meteorológicos e notícias sobre o meio ambiente."
)

# Filtros na Barra Lateral
st.sidebar.header("🔍 Filtros de Visualização")

cidades_disponiveis = df_clima["Cidade"].unique()
cidade_selecionada = st.sidebar.selectbox(
    "Selecione a Cidade:",
    cidades_disponiveis,
    on_change=registrar_interacao,  # Atualiza o estado da sessão ao mudar de cidade
)

indicador_selecionado = st.sidebar.radio(
    "Selecione o Indicador:",
    ["Temperatura (°C)", "Umidade (%)"],
    on_change=registrar_interacao,  # Atualiza o estado da sessão ao mudar o rádio
)

# Exibe o contador mantido pelo Session State na barra lateral
st.sidebar.markdown("---")
st.sidebar.metric(
    label="⚡ Interações nesta Sessão",
    value=st.session_state.contador_interacoes,
)

# ==========================================
# 5. ESTRUTURA DE ABAS
# ==========================================
aba1, aba2 = st.tabs(
    ["📊 Indicadores Climáticos", "📰 Notícias & Raspagem Web"]
)

# ABA 1: INDICADORES CLIMÁTICOS
with aba1:
    st.subheader(f"Dados Meteorológicos - {cidade_selecionada}")

    # Filtragem dos dados conforme seleção
    df_filtrado = df_clima[df_clima["Cidade"] == cidade_selecionada]

    # Cartões com Métricas
    col1, col2 = st.columns(2)
    temp_media = df_filtrado["Temperatura"].mean()
    umid_media = df_filtrado["Umidade"].mean()

    col1.metric("Temperatura Média", f"{temp_media:.1f} °C")
    col2.metric("Umidade Média", f"{umid_media:.1f} %")

    # Gráfico simples baseado no filtro
    if indicador_selecionado == "Temperatura (°C)":
        st.line_chart(df_filtrado.set_index("Data")["Temperatura"])
    else:
        st.line_chart(df_filtrado.set_index("Data")["Umidade"])

# ABA 2: NOTÍCIAS RASPADAS
with aba2:
    st.subheader("📰 Conteúdo Extraído da Web (BeautifulSoup)")
    st.caption("Dados raspados automaticamente e armazenados em `data/noticias.csv`.")

    if not df_noticias.empty:
        col1, col2, col3 = st.columns(3)
        col1.metric("Total de Notícias Coletadas", len(df_noticias))
        col2.metric(
            "Média de Palavras por Título",
            f"{df_noticias['Qtd_Palavras'].mean():.1f}",
        )
        col3.metric(
            "Maior Título (Caracteres)",
            df_noticias["Tamanho_Titulo"].max(),
        )

        st.markdown("### Tabela de Headlines")
        st.dataframe(
            df_noticias[["Titulo", "Qtd_Palavras"]], use_container_width=True
        )
    else:
        st.warning(
            "Nenhum dado encontrado. Execute o arquivo 'coleta_dados.py' no terminal para gerar o CSV."
        )