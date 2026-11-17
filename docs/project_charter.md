# Project Charter - Dashboard ODS 13 (TP4)

## Objetivo
Integrar um modelo de Inteligência Artificial (LLM) rodando localmente à plataforma de monitoramento climático e ambiental (ODS 13), permitindo classificar automaticamente as notícias coletadas em **Alerta**, **Neutro** ou **Positivo**, com respostas estruturadas e tratamento robusto de erros na API.

## Arquitetura da Solução
- **Interface Gráfica:** Streamlit com navegação multi-páginas (`pages/`), agora consumindo a API (GET e POST) em vez de ler o CSV diretamente.
- **Coleta de Dados:** Selenium WebDriver (Headless) abre as páginas e o BeautifulSoup extrai as manchetes do `page_source`. Duas fontes públicas: Agência Brasil (Meio Ambiente) e Ministério do Meio Ambiente e Mudança do Clima.
- **Camada de API:** Backend FastAPI com Response Models (Pydantic), documentação Swagger em `/docs` e erros padronizados em JSON (422, 503, 404 e 500).
- **Inteligência Artificial:** Modelo `cardiffnlp/twitter-xlm-roberta-base-sentiment` (HuggingFace Transformers) rodando na CPU da máquina local, sem nuvem, isolado no arquivo `llm_service.py`.

## Principais Entregáveis do TP4
1. Escolha do modelo de IA justificada por teste prático com as manchetes reais do projeto (`avaliar_modelos.py` e `docs/escolha_modelo.md`).
2. Serviço de IA local (`llm_service.py`) carregado uma única vez quando a API inicia.
3. Novas rotas na API: `POST /processar_texto` (análise de sentimento) e `GET /llm/status` (situação do modelo).
4. Response Models em todas as rotas e tratamento de erros com mensagens claras em português.
5. Nova página no dashboard: **Análise com IA** (análise individual e panorama de todas as notícias).
6. Correções do feedback do TP3: BeautifulSoup na coleta, segunda fonte de notícias, Streamlit consumindo a API, `requirements.txt` em UTF-8 completo e README finalizado.

## Histórico de Entregas
- **TP1/TP2:** Dashboard Streamlit com indicadores de temperatura e umidade por cidade.
- **TP3:** Arquitetura multi-páginas, raspagem com Selenium, API REST com FastAPI e endpoint de preparação de contexto para LLMs.
- **TP4:** Integração de modelo de IA local, Response Models, tratamento de erros e consumo da API pelo dashboard.

## Próxima Etapa (TP5)
Finalizar a aplicação para apresentação, refinando a integração dos recursos de IA com o restante do painel.