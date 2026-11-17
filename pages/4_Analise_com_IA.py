import pandas as pd
import requests
import streamlit as st

st.set_page_config(page_title="Análise com IA", page_icon="🤖", layout="wide")

# Endereço da API FastAPI rodando localmente (uvicorn api:app)
URL_API = "http://127.0.0.1:8000"

# Cor de cada categoria na tela
CORES = {"Alerta": "🔴", "Neutro": "⚪", "Positivo": "🟢"}


def chamar_api(metodo, rota, dados=None):
    """
    Faz a chamada para a API e devolve (sucesso, conteúdo).
    Se der erro, o conteúdo é a mensagem explicando o problema.
    """
    try:
        resposta = requests.request(metodo, f"{URL_API}{rota}", json=dados, timeout=60)
    except requests.exceptions.ConnectionError:
        return False, "Não foi possível conectar à API. Abra outro terminal e rode: uvicorn api:app"

    if resposta.status_code != 200:
        try:
            mensagem = resposta.json().get("mensagem", resposta.text)
        except ValueError:
            mensagem = resposta.text
        return False, f"Erro {resposta.status_code}: {mensagem}"

    return True, resposta.json()


st.title("🤖 Análise de Sentimento com IA")
st.caption(
    "As notícias são classificadas como **Alerta**, **Neutro** ou **Positivo** por um modelo "
    "da HuggingFace rodando localmente, consultado pela API (POST /processar_texto)."
)

# ---------------- STATUS DO MODELO ----------------
ok, status = chamar_api("GET", "/llm/status")

if not ok:
    st.error(status)
    st.stop()

if status["carregado"]:
    st.success(f"Modelo carregado: `{status['modelo']}`")
else:
    st.error(f"O modelo não está carregado. Detalhe: {status['erro']}")
    st.stop()

st.markdown("---")

# ---------------- ANÁLISE DE UM TEXTO ----------------
st.markdown("### 🔎 Analisar um texto")

origem = st.radio("De onde vem o texto?", ["Escolher uma notícia coletada", "Digitar um texto"], horizontal=True)

texto = ""
if origem == "Escolher uma notícia coletada":
    ok, resposta = chamar_api("GET", "/noticias")
    if ok and resposta["dados"]:
        titulos = [n["Titulo"] for n in resposta["dados"]]
        texto = st.selectbox("Notícia:", titulos)
    elif not ok:
        st.error(resposta)
else:
    texto = st.text_area("Digite o texto (mínimo de 10 caracteres):", height=100)

if st.button("Analisar com IA", type="primary"):
    with st.spinner("O modelo está analisando o texto..."):
        ok, resultado = chamar_api("POST", "/processar_texto", {"texto": texto})

    if ok:
        r = resultado["resultado"]
        col1, col2, col3 = st.columns(3)
        col1.metric("Sentimento", f"{CORES.get(r['sentimento'], '')} {r['sentimento']}")
        col2.metric("Confiança do modelo", f"{r['confianca']:.0%}")
        col3.metric("Tempo de processamento", f"{r['tempo_processamento_seg']:.2f} s")

        with st.expander("Ver resposta completa da API (JSON)"):
            st.json(resultado)
    else:
        st.error(resultado)

st.markdown("---")

# ---------------- ANÁLISE DE TODAS AS NOTÍCIAS ----------------
st.markdown("### 📊 Panorama das notícias coletadas")
st.caption("Envia cada notícia para a IA e mostra quantas são de alerta, neutras ou positivas.")

if st.button("Analisar todas as notícias"):
    ok, resposta = chamar_api("GET", "/noticias")

    if not ok:
        st.error(resposta)
    else:
        linhas = []
        barra = st.progress(0, text="Analisando notícias...")
        noticias = resposta["dados"]

        for i, noticia in enumerate(noticias):
            ok, resultado = chamar_api("POST", "/processar_texto", {"texto": noticia["Titulo"]})
            if ok:
                r = resultado["resultado"]
                linhas.append(
                    {
                        "Sentimento": f"{CORES.get(r['sentimento'], '')} {r['sentimento']}",
                        "Confiança": f"{r['confianca']:.0%}",
                        "Titulo": noticia["Titulo"],
                        "Fonte": noticia["Fonte"],
                        "Categoria": r["sentimento"],
                    }
                )
            barra.progress((i + 1) / len(noticias), text=f"Analisando notícia {i + 1} de {len(noticias)}...")

        barra.empty()
        df = pd.DataFrame(linhas)

        if df.empty:
            st.warning("Nenhuma notícia pôde ser analisada.")
        else:
            contagem = df["Categoria"].value_counts()
            col1, col2, col3 = st.columns(3)
            col1.metric("🔴 Alertas", int(contagem.get("Alerta", 0)))
            col2.metric("⚪ Neutras", int(contagem.get("Neutro", 0)))
            col3.metric("🟢 Positivas", int(contagem.get("Positivo", 0)))

            st.bar_chart(contagem)
            st.dataframe(df[["Sentimento", "Confiança", "Titulo", "Fonte"]], use_container_width=True)