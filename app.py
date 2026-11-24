import streamlit as st

st.set_page_config(
    page_title="Dashboard ODS 13 - Home", page_icon="🌍", layout="wide"
)

st.title("🌍 Dashboard ODS 13 - Monitoramento Climático")
st.markdown("---")

st.markdown("""
### Bem-vindo ao Sistema de Monitoramento Climático e Notícias!

Este painel junta **dados climáticos reais** e **notícias ambientais** e usa **IA local** para transformar esses dados em informação útil para o acompanhamento do ODS 13.

Use o **menu na barra lateral à esquerda** para navegar entre as seções:

* 📊 **Indicadores Climáticos:** temperatura, umidade e chuva reais de três capitais, com alertas do período.
* 📰 **Notícias & Raspagem:** notícias ambientais coletadas via web scraping.
* 📥 **Upload & Exportação:** envio de novos dados em CSV e exportação de relatórios.
* 🤖 **Análise com IA:** classificação das notícias em Alerta, Neutro ou Positivo.
* 🧠 **Resumo com IA:** resumo automático de clima + notícias, com recomendações.
""")

st.markdown("#### Como os dados viram informação")
st.markdown(
    "**Coleta** (notícias e Open-Meteo) → **Preparação** (limpeza, médias e alertas) → "
    "**Classificação** (sentimento das notícias) → **Prompt** → **Resumo com IA** → **Dashboard**"
)

st.info("👈 Selecione uma opção no menu lateral para começar a explorar.")