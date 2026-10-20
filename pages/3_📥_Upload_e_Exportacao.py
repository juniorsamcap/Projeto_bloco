import pandas as pd
import streamlit as st

st.set_page_config(page_title="Upload e Exportação", page_icon="📥", layout="wide")

st.title("📥 Upload & Exportação de Dados")

st.subheader("1. Upload de Novos Dados Climáticos")
arquivo_enviado = st.file_uploader("Envie um arquivo CSV com dados climáticos adicionais:", type=["csv"])

if arquivo_enviado is not None:
    try:
        df_upload = pd.read_csv(arquivo_enviado)
        st.success("Arquivo CSV carregado com sucesso!")
        st.dataframe(df_upload.head(), use_container_width=True)
    except Exception as e:
        st.error(f"Erro ao ler o arquivo CSV informado: {e}")

st.markdown("---")
st.subheader("2. Exportar Dados do Sistema")
st.caption("Baixe os dados processados pelo sistema para uso externo.")

# Exemplo simples de exportação
dados_exemplo = pd.DataFrame({
    "Cidade": ["São Paulo", "Rio de Janeiro", "Curitiba"],
    "Status_Coleta": ["OK", "OK", "OK"]
})
csv_buffer = dados_exemplo.to_csv(index=False).encode("utf-8")

st.download_button(
    label="💾 Baixar Relatório de Coleta (CSV)",
    data=csv_buffer,
    file_name="relatorio_coleta.csv",
    mime="text/csv",
)