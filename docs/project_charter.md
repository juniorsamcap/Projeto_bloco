# Project Charter - Dashboard ODS 13 (TP5 - versão final)

## Problema de Negócio
Gestores públicos locais, ONGs e voluntários que atuam com clima e meio ambiente precisam acompanhar dois tipos de informação ao mesmo tempo: o que está acontecendo com o clima nas cidades (calor, chuva, umidade) e o que está sendo noticiado sobre meio ambiente. Hoje essas informações estão espalhadas em sites diferentes, em formatos diferentes, e ler tudo toma tempo. O resultado é que sinais importantes (uma onda de calor, uma notícia de emergência ambiental) demoram a ser percebidos.

## Objetivo
Entregar um painel simples que junta dados climáticos reais e notícias ambientais, classifica as notícias automaticamente e usa um modelo de linguagem para transformar tudo isso em um resumo curto, com os principais pontos e recomendações práticas ligadas ao **ODS 13 (Ação Contra a Mudança Global do Clima)**.

## Público-alvo
- Gestores municipais e equipes de defesa civil
- ONGs e coletivos ambientais
- Voluntários e estudantes que acompanham o tema

## Como os dados, a IA e a engenharia de prompt resolvem o problema
| Etapa do ciclo | O que faço no projeto | Por que ajuda no problema |
|---|---|---|
| Coleta | Notícias por web scraping (Selenium + BeautifulSoup) e clima real pela API Open-Meteo | Reúne num lugar só informações que estavam espalhadas |
| Preparação | Limpeza dos títulos, médias por cidade e identificação de dias de alerta (calor a partir de 32 °C ou chuva a partir de 50 mm) | Transforma dados brutos em indicadores fáceis de ler |
| Modelagem 1 | Classificação de sentimento das notícias com XLM-RoBERTa (Alerta, Neutro, Positivo) | Separa automaticamente o que é risco do que é informativo |
| Modelagem 2 | Resumo com o modelo generativo Qwen2.5 0.5B, a partir de um prompt montado com os dados | Entrega a leitura pronta, em linguagem natural, em vez de tabelas soltas |
| Apresentação | Dashboard Streamlit com gráficos, filtros e a página de resumo | O usuário escolhe o foco e recebe a resposta na hora |

A **engenharia de prompt** é o que liga os dados ao modelo. O prompt tem três partes: o papel do modelo (analista de clima que apoia gestores do ODS 13), as regras (usar só os dados enviados, não inventar números, responder em português de forma curta) e a tarefa, que muda conforme o foco que o usuário escolhe (panorama geral, riscos e alertas ou só notícias) e traz um modelo de resposta para o modelo preencher. Assim o mesmo modelo atende pedidos diferentes sem precisar de treinamento.

## Relevância para Ciência de Dados, ESG e ODS
- O projeto passa por todo o ciclo de Ciência de Dados: coleta, preparação, modelagem, avaliação e apresentação.
- Na dimensão **Ambiental (E)** do ESG, apoia o monitoramento de riscos climáticos e de notícias sobre desmatamento, queimadas e políticas ambientais.
- Na dimensão **Governança (G)**, dá transparência: as fontes são públicas, o prompt enviado ao modelo aparece na tela e cada resumo gerado fica registrado em histórico.
- Está ligado às metas do ODS 13, principalmente à 13.1 (resiliência a riscos climáticos) e à 13.3 (educação e conscientização sobre mudança do clima).

## Arquitetura da Solução
- **Interface:** Streamlit multipáginas (`app.py` + `pages/`), consumindo a API.
- **Coleta:** `coleta_dados.py` (notícias) e `clima_service.py` (Open-Meteo, com cópia de segurança em `data/clima.csv`).
- **API:** FastAPI v3.0.0 com Response Models, Swagger em `/docs` e erros padronizados em JSON (422, 503, 404 e 500).
- **IA local (sem nuvem e sem custo):**
  - `llm_service.py`: classificador de sentimento `cardiffnlp/twitter-xlm-roberta-base-sentiment`
  - `resumo_service.py`: modelo generativo `Qwen/Qwen2.5-0.5B-Instruct` e montagem do prompt
- **Testes e evidências:** `testar_erros.py` e a pasta `docs/evidencias/`.

## Principais Entregáveis do TP5
1. Dados climáticos reais (Open-Meteo) no lugar dos dados simulados, com alertas de calor e chuva.
2. Sumarização automática com LLM local e engenharia de prompt (rota `POST /llm/resumo`).
3. Nova página **Resumo com IA**, com escolha de foco, gráficos dos resultados, prompt visível e histórico.
4. Correções do feedback do TP4: `requirements.txt` com versões fixas e compatíveis e evidências das respostas de erro guardadas no repositório.
5. Documentação TDSP atualizada: este Charter, o Data Summary Report e o Relatório Final (`docs/relatorio_final.md`).

## Métricas de Sucesso
- O painel mostra dados climáticos reais e atualizados das 3 cidades.
- O resumo é gerado localmente, em CPU, em tempo aceitável para uso no dashboard (os tempos ficam registrados em `data/historico_resumos.csv`).
- O resumo usa apenas os dados enviados no prompt e cita os alertas reais do período.
- Todos os erros da API respondem no formato padrão (evidências em `docs/evidencias/`).

## Riscos e Limitações
- O modelo de resumo é pequeno (0,5 bilhão de parâmetros) para caber em 8 GB de RAM sem GPU. Os textos são úteis, mas podem sair genéricos ou com pequenos erros, então o resumo apoia a decisão e não a substitui.
- O resumo usa só os títulos das notícias, não o texto completo das matérias.
- Os limites de alerta (32 °C e 50 mm) são referências que defini para o projeto, não são limites oficiais.

## Histórico de Entregas
- **TP1/TP2:** Dashboard Streamlit com indicadores de temperatura e umidade por cidade.
- **TP3:** Arquitetura multipáginas, raspagem com Selenium, API REST com FastAPI e endpoint de preparação de contexto para LLMs.
- **TP4:** Modelo de IA local para análise de sentimento, Response Models, tratamento de erros e consumo da API pelo dashboard.
- **TP5:** Clima real, sumarização com LLM local e engenharia de prompt, página de resumo e documentação final.