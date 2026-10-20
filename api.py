import os
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(
    title="API ODS 13 - Monitoramento Climático",
    description="API para consulta de notícias e indicadores climáticos do projeto ODS 13.",
    version="1.0.0",
)


# Modelo de dados para o POST (Validação via Pydantic)
class NoticiaSchema(BaseModel):
    Titulo: str
    Fonte: str = "Envio via API"


@app.get("/", summary="Rota Raiz", tags=["Geral"])
def home():
    """Retorna uma mensagem de boas-vindas e confirma que a API está online."""
    return {"status": "Online", "mensagem": "API do Dashboard ODS 13 operacional!"}


@app.get("/noticias", summary="Consultar Notícias (GET)", tags=["Notícias"])
def listar_noticias():
    """
    **Rota GET:** Lê e retorna todas as notícias raspadas presentes em `data/noticias.csv`.
    """
    caminho_csv = os.path.join("data", "noticias.csv")

    if not os.path.exists(caminho_csv):
        raise HTTPException(
            status_code=404, detail="Arquivo de notícias não encontrado."
        )

    try:
        df = pd.read_csv(caminho_csv)
        return {"total": len(df), "dados": df.to_dict(orient="records")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao ler os dados: {e}")


@app.post(
    "/noticias", summary="Cadastrar Nova Notícia (POST)", tags=["Notícias"]
)
def adicionar_noticia(noticia: NoticiaSchema):
    """
    **Rota POST:** Recebe uma nova notícia em JSON e adiciona ao arquivo `data/noticias.csv`.
    """
    caminho_csv = os.path.join("data", "noticias.csv")

    nova_linha = {
        "Titulo": noticia.Titulo,
        "Tamanho_Titulo": len(noticia.Titulo),
        "Qtd_Palavras": len(noticia.Titulo.split()),
        "Fonte": noticia.Fonte,
    }

    try:
        if os.path.exists(caminho_csv):
            df = pd.read_csv(caminho_csv)
            df = pd.concat([df, pd.DataFrame([nova_linha])], ignore_index=True)
        else:
            os.makedirs("data", exist_ok=True)
            df = pd.DataFrame([nova_linha])

        df.to_csv(caminho_csv, index=False, encoding="utf-8")
        return {
            "sucesso": True,
            "mensagem": "Notícia inserida com sucesso!",
            "dados": nova_linha,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro ao salvar a notícia: {e}"
        )


@app.get(
    "/llm/contexto-preparado",
    summary="Obter Contexto Formatado para LLM (Preparação)",
    tags=["Inteligência Artificial"],
)
def obter_contexto_llm():
    """
    **Rota de Preparação para IA:**
    Lê os dados brutos do CSV de notícias e os formata em um prompt de contexto
    pronto para ser enviado a um modelo de LLM (como Gemini ou OpenAI).
    """
    caminho_csv = os.path.join("data", "noticias.csv")

    if not os.path.exists(caminho_csv):
        raise HTTPException(
            status_code=404, detail="Arquivo de notícias não encontrado."
        )

    df = pd.read_csv(caminho_csv)

    # Converte os títulos das notícias em um bloco de texto estruturado para Prompt
    titulos = df["Titulo"].tolist()
    bloco_texto = "\n".join([f"- {t}" for t in titulos])

    prompt_preparado = f"""
    [INSTRUÇÃO PARA A LLM]
    Você é um especialista em Clima e Meio Ambiente (ODS 13). 
    Analise as notícias abaixo e forneça um resumo dos principais problemas ambientais identificados.

    [NOTÍCIAS COLETADAS]:
    {bloco_texto}
    """

    return {
        "status": "Sucesso",
        "total_noticias": len(titulos),
        "prompt_pronto_para_llm": prompt_preparado,
    }