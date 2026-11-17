import pandas as pd
import requests
import streamlit as st

st.set_page_config(page_title="Notícias Climáticas", page_icon="📰", layout="wide")

# Endereço da API FastAPI rodando localmente (uvicorn api:app)
URL_API = "http://127.0.0.1:8000"


def mostrar_erro_api(resposta):
    """Mostra a mensagem de erro padronizada que a API devolve."""
    try:
        mensagem = resposta.json().get("mensagem", resposta.text)
    except ValueError:
        mensagem = resposta.text
    st.error(f"Erro {resposta.status_code}: {mensagem}")


def buscar_noticias():
    """Consulta a rota GET /noticias da API e devolve a lista de notícias."""
    try:
        resposta = requests.get(f"{URL_API}/noticias", timeout=10)
    except requests.exceptions.ConnectionError:
        st.error("Não foi possível conectar à API. Abra outro terminal e rode: uvicorn api:app")
        return None

    if resposta.status_code != 200:
        mostrar_erro_api(resposta)
        return None

    return resposta.json()["dados"]


def enviar_noticia(titulo, fonte):
    """Envia uma nova notícia para a rota POST /noticias da API."""
    try:
        resposta = requests.post(
            f"{URL_API}/noticias",
            json={"Titulo": titulo, "Fonte": fonte},
            timeout=10,
        )
    except requests.exceptions.ConnectionError:
        st.error("Não foi possível conectar à API. Abra outro terminal e rode: uvicorn api:app")
        return False

    if resposta.status_code != 200:
        mostrar_erro_api(resposta)
        return False

    st.sidebar.success(resposta.json()["mensagem"])
    return True


st.title("📰 Notícias & Raspagem Web")
st.caption("Dados coletados com Selenium + BeautifulSoup e consultados pela API FastAPI (GET /noticias).")

# ---------------- CADASTRO (POST) - barra lateral ----------------
# Fica antes da listagem para que a notícia nova já apareça na tabela logo após o envio
st.sidebar.header("➕ Cadastrar Nova Notícia")
st.sidebar.caption("A notícia é enviada para a API (POST /noticias), que valida os dados e salva no CSV.")

with st.sidebar.form("form_noticia", clear_on_submit=True):
    titulo = st.text_input("Título da notícia")
    fonte = st.text_input("Fonte", value="Envio via Dashboard")
    enviar = st.form_submit_button("Enviar para a API")

if enviar:
    enviar_noticia(titulo, fonte)

# ---------------- LISTAGEM (GET) ----------------
noticias = buscar_noticias()

if noticias:
    df_noticias = pd.DataFrame(noticias)

    col1, col2, col3 = st.columns(3)
    col1.metric("Total de Notícias Coletadas", len(df_noticias))
    col2.metric("Média de Palavras por Título", f"{df_noticias['Qtd_Palavras'].mean():.1f}")
    col3.metric("Maior Título (Caracteres)", df_noticias["Tamanho_Titulo"].max())

    st.markdown("---")
    st.markdown("### Tabela de Headlines Coletadas")
    st.dataframe(df_noticias[["Titulo", "Qtd_Palavras", "Fonte"]], use_container_width=True)

elif noticias == []:
    st.warning("Nenhuma notícia cadastrada ainda. Execute o script `coleta_dados.py` para gerar os dados.")
    