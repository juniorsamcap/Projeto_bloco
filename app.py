import io
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


@st.cache_data
def carregar_noticias():
    caminho_csv = os.path.join("data", "noticias.csv")
    if os.path.exists(caminho_csv):
        return pd.read_csv(caminho_csv)
    return pd.DataFrame()


# Carregamento base dos dados
df_clima_base = carregar_dados_climaticos()
df_noticias = carregar_noticias()

# Limits de data padrão para filtros
DATA_MIN_PADRAO = df_clima_base["Data"].min().date()
DATA_MAX_PADRAO = df_clima_base["Data"].max().date()

# ===============================================
# 3. IMPLEMENTAÇÃO DE ESTADO DE SESSÃO (st.session_state)
# ===============================================
if "contador_interacoes" not in st.session_state:
    st.session_state.contador_interacoes = 0

# Inicialização dos estados padrão dos filtros
if "filtro_cidade" not in st.session_state:
    st.session_state.filtro_cidade = "Todas"

if "filtro_datas" not in st.session_state:
    st.session_state.filtro_datas = (DATA_MIN_PADRAO, DATA_MAX_PADRAO)

if "filtro_indicador" not in st.session_state:
    st.session_state.filtro_indicador = "Temperatura (°C)"


def registrar_interacao():
    st.session_state.contador_interacoes += 1


def resetar_filtros():
    st.session_state.filtro_cidade = "Todas"
    st.session_state.filtro_datas = (DATA_MIN_PADRAO, DATA_MAX_PADRAO)
    st.session_state.filtro_indicador = "Temperatura (°C)"
    st.session_state.contador_interacoes += 1


# ==========================================
# 4. INTERFACE DO USUÁRIO & BARRA LATERAL
# ==========================================
st.title("🌍 Dashboard ODS 13 - Monitoramento Climático")
st.markdown(
    "Acompanhe os indicadores meteorológicos e notícias sobre o meio ambiente."
)

# --- UPLOAD DE ARQUIVOS NA BARRA LATERAL ---
st.sidebar.header("📥 Upload de Dados Adicionais")
arquivo_enviado = st.sidebar.file_uploader(
    "Envie um arquivo CSV com novos dados climáticos:",
    type=["csv"],
    on_change=registrar_interacao,
)

if arquivo_enviado is not None:
    try:
        df_upload = pd.read_csv(arquivo_enviado)
        df_upload["Data"] = pd.to_datetime(df_upload["Data"])
        df_clima = pd.concat([df_clima_base, df_upload], ignore_index=True)
        st.sidebar.success("Arquivo CSV carregado com sucesso!")
    except Exception as e:
        st.sidebar.error(f"Erro ao ler o CSV enviado: {e}")
        df_clima = df_clima_base.copy()
else:
    df_clima = df_clima_base.copy()

# --- FILTROS DE VISUALIZAÇÃO ---
st.sidebar.markdown("---")
st.sidebar.header("🔍 Filtros de Visualização")

# 1. Filtro de Cidade
cidades_lista = ["Todas"] + list(df_clima["Cidade"].unique())
st.sidebar.selectbox(
    "Selecione a Cidade:",
    cidades_lista,
    key="filtro_cidade",
    on_change=registrar_interacao,
)

# 2. Filtro por Intervalo de Datas
st.sidebar.date_input(
    "Selecione o Período:",
    min_value=DATA_MIN_PADRAO,
    max_value=DATA_MAX_PADRAO,
    key="filtro_datas",
    on_change=registrar_interacao,
)

# 3. Filtro de Indicador Meteorológico
st.sidebar.radio(
    "Selecione o Indicador:",
    ["Temperatura (°C)", "Umidade (%)"],
    key="filtro_indicador",
    on_change=registrar_interacao,
)

# 4. Botão Resetar Filtros
st.sidebar.button("🔄 Resetar Filtros", on_click=resetar_filtros)

st.sidebar.markdown("---")
st.sidebar.metric(
    label="⚡ Interações nesta Sessão",
    value=st.session_state.contador_interacoes,
)

# ==========================================
# 5. APLICAÇÃO DOS FILTROS NOS DADOS
# ==========================================
df_filtrado = df_clima.copy()

# Aplica filtro de cidade
if st.session_state.filtro_cidade != "Todas":
    df_filtrado = df_filtrado[df_filtrado["Cidade"] == st.session_state.filtro_cidade]

# Aplica filtro de datas
if isinstance(st.session_state.filtro_datas, tuple) and len(st.session_state.filtro_datas) == 2:
    data_inicio, data_fim = st.session_state.filtro_datas
    df_filtrado = df_filtrado[
        (df_filtrado["Data"].dt.date >= data_inicio)
        & (df_filtrado["Data"].dt.date <= data_fim)
    ]

# ==========================================
# 6. ESTRUTURA DE ABAS
# ==========================================
aba1, aba2 = st.tabs(
    ["📊 Indicadores Climáticos", "📰 Notícias & Raspagem Web"]
)

# ABA 1: INDICADORES CLIMÁTICOS & DOWNLOAD
with aba1:
    st.subheader(f"Dados Meteorológicos - Cidade: {st.session_state.filtro_cidade}")

    if not df_filtrado.empty:
        col1, col2 = st.columns(2)
        temp_media = df_filtrado["Temperatura"].mean()
        umid_media = df_filtrado["Umidade"].mean()

        col1.metric("Temperatura Média", f"{temp_media:.1f} °C")
        col2.metric("Umidade Média", f"{umid_media:.1f} %")

        coluna_indicador = (
            "Temperatura" if st.session_state.filtro_indicador == "Temperatura (°C)" else "Umidade"
        )

        if st.session_state.filtro_cidade == "Todas":
            df_pivot = df_filtrado.pivot_table(
                index="Data", columns="Cidade", values=coluna_indicador
            )
            st.line_chart(df_pivot)
        else:
            st.line_chart(df_filtrado.set_index("Data")[coluna_indicador])

        # --- SERVIÇO DE DOWNLOAD DE ARQUIVOS ---
        st.markdown("---")
        st.subheader("📤 Exportar Dados Processados")
        st.caption(
            "Baixe os dados filtrados em formato CSV para apresentações ou relatórios externos."
        )

        csv_buffer = df_filtrado.to_csv(index=False, encoding="utf-8").encode("utf-8")

        st.download_button(
            label=f"💾 Baixar CSV ({st.session_state.filtro_cidade})",
            data=csv_buffer,
            file_name=f"dados_climaticos_{st.session_state.filtro_cidade.lower().replace(' ', '_')}.csv",
            mime="text/csv",
            on_click=registrar_interacao,
        )
    else:
        st.warning("Nenhum dado encontrado para os filtros selecionados.")

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