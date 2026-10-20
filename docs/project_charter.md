# Project Charter - Dashboard ODS 13 (TP3)

## Objetivo
Evoluir a plataforma de monitoramento climático e ambiental (ODS 13) para uma arquitetura modular, escalável e com serviços RESTful integrados.

## Arquitetura da Solução
- **Interface Gráfica:** Streamlit com navegação multi-páginas (`pages/`).
- **Coleta de Dados:** Raspagem dinâmica via Selenium WebDriver (Headless) armazenando em `data/noticias.csv`.
- **Camada de API:** Backend FastAPI com endpoints REST (`GET`, `POST`) e documentação Swagger OpenAPI.
- **Preparação para IA:** Endpoint de formatação de contexto/prompts para consumo por LLMs em entregas futuras.

## Principais Entregáveis do TP3
1. Aplicação Streamlit modularizada em diretório de páginas.
2. Script de Web Scraping automatizado com Selenium.
3. API REST funcional em FastAPI com documentação em `/docs`.
4. Endpoint preparado para integração de LLMs (`/llm/contexto-preparado`).