import os
from contextlib import asynccontextmanager
from typing import List, Optional

import pandas as pd
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from starlette.exceptions import HTTPException as StarletteHTTPException

import llm_service

CAMINHO_CSV = os.path.join("data", "noticias.csv")


# Quando a API liga, o modelo de IA já é carregado uma única vez na memória
@asynccontextmanager
async def lifespan(app: FastAPI):
    llm_service.carregar_modelo()
    yield


app = FastAPI(
    title="API ODS 13 - Monitoramento Climático",
    description="API para consulta de notícias, indicadores climáticos e análise de sentimento com IA local (ODS 13).",
    version="2.0.0",
    lifespan=lifespan,
)


# ---------------------------------------------------------------
# MODELOS DE DADOS (Pydantic)
# Entrada: validam o que o usuário envia
# Resposta (Response Models): garantem que a API sempre devolve o mesmo formato
# ---------------------------------------------------------------

class NoticiaSchema(BaseModel):
    Titulo: str = Field(..., min_length=5, description="Título da notícia")
    Fonte: str = "Envio via API"


class Noticia(BaseModel):
    Titulo: str
    Tamanho_Titulo: int
    Qtd_Palavras: int
    Fonte: str


class RespostaNoticias(BaseModel):
    total: int
    dados: List[Noticia]


class RespostaCadastro(BaseModel):
    sucesso: bool
    mensagem: str
    dados: Noticia


class TextoEntrada(BaseModel):
    texto: str = Field(
        ...,
        min_length=10,
        max_length=2000,
        description="Texto que será analisado pelo modelo (entre 10 e 2000 caracteres)",
        examples=["Pará tem 61 cidades em situação de emergência por incêndios florestais"],
    )


class ResultadoAnalise(BaseModel):
    sentimento: str = Field(..., description="Positivo, Neutro ou Alerta")
    rotulo_original: str = Field(..., description="Rótulo devolvido pelo modelo (positive, neutral, negative)")
    confianca: float = Field(..., ge=0, le=1, description="Confiança do modelo, de 0 a 1")
    tempo_processamento_seg: float


class RespostaProcessamento(BaseModel):
    texto_processado: str
    tipo_analise: str
    modelo: str
    resultado: ResultadoAnalise


class RespostaStatusLLM(BaseModel):
    modelo: str
    carregado: bool
    erro: Optional[str] = None


class RespostaContexto(BaseModel):
    status: str
    total_noticias: int
    prompt_pronto_para_llm: str


class RespostaErro(BaseModel):
    erro: bool = True
    status_code: int
    mensagem: str
    detalhes: Optional[list] = None


# ---------------------------------------------------------------
# TRATAMENTO DE ERROS
# Todos os erros saem no mesmo formato JSON, com mensagem clara em português
# ---------------------------------------------------------------

@app.exception_handler(StarletteHTTPException)
async def tratar_erro_http(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"erro": True, "status_code": exc.status_code, "mensagem": str(exc.detail)},
    )


@app.exception_handler(RequestValidationError)
async def tratar_erro_validacao(request: Request, exc: RequestValidationError):
    # Monta uma lista simples dizendo qual campo veio errado
    detalhes = [
        f"{' -> '.join(str(parte) for parte in erro['loc'])}: {erro['msg']}"
        for erro in exc.errors()
    ]
    return JSONResponse(
        status_code=422,
        content={
            "erro": True,
            "status_code": 422,
            "mensagem": "Dados de entrada inválidos. Verifique os campos enviados.",
            "detalhes": detalhes,
        },
    )


# Respostas de erro que aparecem documentadas no Swagger (/docs)
ERROS_PADRAO = {
    422: {"model": RespostaErro, "description": "Dados de entrada inválidos"},
    500: {"model": RespostaErro, "description": "Erro interno"},
}


def ler_csv_noticias():
    """Lê o CSV de notícias ou devolve erro 404 se ele não existir."""
    if not os.path.exists(CAMINHO_CSV):
        raise HTTPException(
            status_code=404,
            detail="Arquivo de notícias não encontrado. Execute 'python coleta_dados.py' para gerar os dados.",
        )
    try:
        return pd.read_csv(CAMINHO_CSV)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao ler o arquivo de notícias: {e}")


# ---------------------------------------------------------------
# ROTAS
# ---------------------------------------------------------------

@app.get("/", summary="Rota Raiz", tags=["Geral"])
def home():
    """Retorna uma mensagem de boas-vindas e confirma que a API está online."""
    return {"status": "Online", "mensagem": "API do Dashboard ODS 13 operacional!"}


@app.get(
    "/noticias",
    summary="Consultar Notícias (GET)",
    tags=["Notícias"],
    response_model=RespostaNoticias,
    responses={404: {"model": RespostaErro, "description": "CSV não encontrado"}, **ERROS_PADRAO},
)
def listar_noticias():
    """
    **Rota GET:** Lê e retorna todas as notícias raspadas presentes em `data/noticias.csv`.
    """
    df = ler_csv_noticias()

    try:
        return {"total": len(df), "dados": df.to_dict(orient="records")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao ler os dados: {e}")


@app.post(
    "/noticias",
    summary="Cadastrar Nova Notícia (POST)",
    tags=["Notícias"],
    response_model=RespostaCadastro,
    responses=ERROS_PADRAO,
)
def adicionar_noticia(noticia: NoticiaSchema):
    """
    **Rota POST:** Recebe uma nova notícia em JSON e adiciona ao arquivo `data/noticias.csv`.
    """
    titulo = noticia.Titulo.strip()

    nova_linha = {
        "Titulo": titulo,
        "Tamanho_Titulo": len(titulo),
        "Qtd_Palavras": len(titulo.split()),
        "Fonte": noticia.Fonte,
    }

    try:
        if os.path.exists(CAMINHO_CSV):
            df = pd.read_csv(CAMINHO_CSV)
            df = pd.concat([df, pd.DataFrame([nova_linha])], ignore_index=True)
        else:
            os.makedirs("data", exist_ok=True)
            df = pd.DataFrame([nova_linha])

        df.to_csv(CAMINHO_CSV, index=False, encoding="utf-8")
        return {
            "sucesso": True,
            "mensagem": "Notícia inserida com sucesso!",
            "dados": nova_linha,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao salvar a notícia: {e}")


@app.get(
    "/llm/status",
    summary="Status do Modelo de IA",
    tags=["Inteligência Artificial"],
    response_model=RespostaStatusLLM,
)
def status_modelo():
    """Informa qual modelo está configurado e se ele foi carregado corretamente."""
    return {
        "modelo": llm_service.NOME_MODELO,
        "carregado": llm_service.modelo_disponivel(),
        "erro": llm_service.erro_carregamento,
    }


@app.post(
    "/processar_texto",
    summary="Analisar Sentimento com IA Local",
    tags=["Inteligência Artificial"],
    response_model=RespostaProcessamento,
    responses={503: {"model": RespostaErro, "description": "Modelo de IA indisponível"}, **ERROS_PADRAO},
)
def processar_texto(entrada: TextoEntrada):
    """
    **Rota de IA:** Recebe um texto e devolve a análise de sentimento feita pelo modelo
    da HuggingFace rodando localmente (sem nuvem).

    Categorias: **Positivo**, **Neutro** ou **Alerta**.
    """
    # 503: o modelo não carregou (ex.: falha no download ou falta de memória)
    if not llm_service.modelo_disponivel():
        raise HTTPException(
            status_code=503,
            detail="O modelo de IA não está disponível no momento. Consulte /llm/status e reinicie a API.",
        )

    texto = entrada.texto.strip()

    # 422: o texto só tinha espaços em branco
    if len(texto) < 10:
        raise HTTPException(
            status_code=422,
            detail="O texto precisa ter pelo menos 10 caracteres (sem contar espaços).",
        )

    # 500: qualquer erro inesperado durante a análise
    try:
        resultado = llm_service.analisar_sentimento(texto)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar o texto com o modelo: {e}")

    return {
        "texto_processado": texto,
        "tipo_analise": "Análise de sentimento",
        "modelo": llm_service.NOME_MODELO,
        "resultado": resultado,
    }


@app.get(
    "/llm/contexto-preparado",
    summary="Obter Contexto Formatado para LLM (Preparação)",
    tags=["Inteligência Artificial"],
    response_model=RespostaContexto,
    responses={404: {"model": RespostaErro, "description": "CSV não encontrado"}},
)
def obter_contexto_llm():
    """
    **Rota de Preparação para IA:**
    Lê os dados brutos do CSV de notícias e os formata em um prompt de contexto
    pronto para ser enviado a um modelo de LLM.
    """
    df = ler_csv_noticias()

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