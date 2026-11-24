import os

import pandas as pd
import plotly.express as px
import requests
import streamlit as st

URL_API = "http://127.0.0.1:8000"
CAMINHO_HISTORICO = os.path.join("data", "historico_resumos.csv")

# Nome que aparece na tela -> valor que a API espera
FOCOS = {
    "Panorama geral": "geral",
    "Riscos e alertas": "alertas",
    "Só as notícias": "noticias",
}

CORES_SENTIMENTO = {"Alerta": "#E15759", "Neutro": "#BAB0AC", "Positivo": "#59A14F"}

st.set_page_config(page_title="Resumo com IA", page_icon="🧠", layout="wide")

st.title("🧠 Resumo Inteligente: Clima + Notícias")
st.caption(
    "Um modelo de linguagem rodando localmente lê os dados reais do projeto e escreve um resumo "
    "com os principais pontos e recomendações ligadas ao ODS 13."
)

with st.expander("Como o resumo é gerado (ciclo dos dados)"):
    st.markdown(
        """
1. **Coleta:** notícias ambientais (Selenium + BeautifulSoup) e clima real das 3 cidades (API Open-Meteo).
2. **Preparação:** limpeza dos títulos, médias por cidade e identificação dos dias de alerta (calor ou chuva).
3. **Classificação:** o modelo XLM-RoBERTa marca cada notícia como Alerta, Neutro ou Positivo.
4. **Prompt:** junto tudo num texto organizado, com o papel do modelo, as regras e a tarefa do foco escolhido.
5. **Resumo:** o modelo Qwen2.5 (local, na CPU) escreve o resumo, que aparece aqui com os gráficos.
"""
    )

# Confere se a API e os modelos estão prontos
try:
    status = requests.get(f"{URL_API}/llm/status", timeout=5).json()
except requests.exceptions.RequestException:
    st.error("A API não está respondendo. Ligue ela com: uvicorn api:app")
    st.stop()

if not status.get("resumo_carregado"):
    st.warning(f"O modelo de resumo não está carregado. Erro: {status.get('erro_resumo')}")

# Opções na barra lateral
st.sidebar.header("⚙️ Opções do Resumo")
foco_nome = st.sidebar.radio("Foco do resumo:", list(FOCOS.keys()))
dias = st.sidebar.slider("Dias de clima considerados:", min_value=7, max_value=30, value=14)

if st.button("✨ Gerar resumo", type="primary"):
    with st.spinner("O modelo está lendo os dados e escrevendo o resumo. Pode levar até 1 minuto..."):
        try:
            resposta = requests.post(
                f"{URL_API}/llm/resumo",
                json={"foco": FOCOS[foco_nome], "dias_clima": dias},
                timeout=600,
            )
        except requests.exceptions.RequestException as erro:
            st.error(f"Não consegui falar com a API: {erro}")
            st.stop()

    if resposta.status_code == 200:
        st.session_state["ultimo_resumo"] = resposta.json()
    else:
        st.error(f"Erro {resposta.status_code}: {resposta.json().get('mensagem')}")

# Mostra o último resumo gerado (fica na tela mesmo se mexer nos filtros)
resultado = st.session_state.get("ultimo_resumo")
if resultado:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Notícias analisadas", resultado["total_noticias"])
    col2.metric("Notícias em Alerta", resultado["noticias_por_sentimento"].get("Alerta", 0))
    col3.metric("Dias de alerta no clima", resultado["alertas_clima"])
    col4.metric("Tempo do modelo", f"{resultado['tempo_processamento_seg']:.1f} s")

    st.markdown("### 📝 Resumo gerado")
    with st.container(border=True):
        st.markdown(resultado["resumo"])
    st.caption(f"Foco: {resultado['foco']} | Modelo: {resultado['modelo']}")

    graf1, graf2 = st.columns(2)

    df_sent = pd.DataFrame(
        list(resultado["noticias_por_sentimento"].items()), columns=["Sentimento", "Quantidade"]
    )
    fig_sent = px.bar(
        df_sent, x="Sentimento", y="Quantidade", color="Sentimento",
        color_discrete_map=CORES_SENTIMENTO, title="Notícias por sentimento",
    )
    graf1.plotly_chart(fig_sent, width="stretch")

    if resultado["alertas_por_cidade"]:
        df_alertas = pd.DataFrame(
            list(resultado["alertas_por_cidade"].items()), columns=["Cidade", "Dias de alerta"]
        )
        fig_alertas = px.bar(df_alertas, x="Cidade", y="Dias de alerta", title="Dias de alerta climático por cidade")
        graf2.plotly_chart(fig_alertas, width="stretch")
    else:
        graf2.info("Nenhum dia de alerta climático no período.")

    with st.expander("Ver o prompt enviado ao modelo"):
        st.code(resultado["prompt_usado"], language="text")

# Histórico de todos os resumos já gerados (registro dos testes)
if os.path.exists(CAMINHO_HISTORICO):
    with st.expander("Histórico de resumos gerados"):
        st.dataframe(pd.read_csv(CAMINHO_HISTORICO), hide_index=True, width="stretch")