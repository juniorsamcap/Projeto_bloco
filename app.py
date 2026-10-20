import streamlit as st

st.set_page_config(
    page_title="Dashboard ODS 13 - Home", page_icon="🌍", layout="wide"
)

st.title("🌍 Dashboard ODS 13 - Monitoramento Climático")
st.markdown("---")

st.markdown("""
### Bem-vindo ao Sistema de Monitoramento Climático e Notícias!

Esta aplicação foi evoluída para uma estrutura de **Múltiplas Páginas** para facilitar a navegação e a análise dos dados.

Use o **menu na barra lateral à esquerda** para navegar entre as diferentes seções:

* 📊 **Indicadores Climáticos:** Gráficos interativos e estatísticas de temperatura e umidade.
* 📰 **Notícias & Raspagem:** Visualização de notícias climáticas coletadas via Web Scraping.
* 📥 **Upload & Exportação:** Envio de novos dados em CSV e exportação de relatórios.
""")

st.info("👈 Selecione uma opção no menu lateral para começar a explorar.")