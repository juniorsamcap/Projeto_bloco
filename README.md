# 🌍 Dashboard ODS 13 - Monitoramento Climático

Aplicação web interativa que junta dados climáticos reais e notícias ambientais e usa IA local para classificar notícias e gerar resumos com insights, alinhada ao **ODS 13 (Ação Contra a Mudança Global do Clima)** da ONU.

---

## 📌 Sobre o Projeto
Gestores locais, ONGs e voluntários precisam acompanhar o clima e as notícias ambientais, mas essas informações ficam espalhadas em vários sites. Este painel reúne tudo num lugar só:

- **clima real** de São Paulo, Rio de Janeiro e Curitiba (API Open-Meteo), com alertas de calor e chuva;
- **notícias ambientais** coletadas de portais públicos (Selenium + BeautifulSoup);
- um **modelo de IA de sentimento** que marca cada notícia como Alerta, Neutro ou Positivo;
- um **modelo de IA generativo** que lê tudo e escreve um resumo com recomendações.

Os dois modelos rodam **localmente, na CPU**, sem nuvem e sem custo.

---

## ⚙️ Funcionalidades
- 📊 **Indicadores Climáticos:** dados reais de temperatura, umidade e chuva, com filtros de período, cidade e indicador, métricas e alertas do período.
- 📰 **Notícias & Raspagem:** notícias coletadas, listadas e cadastradas pela API.
- 📥 **Upload & Exportação:** envio de CSV e download de relatório.
- 🤖 **Análise com IA:** análise de sentimento de uma notícia ou de todas.
- 🧠 **Resumo com IA:** resumo automático de clima + notícias com três focos (panorama geral, riscos e alertas, só notícias), gráficos, prompt visível e histórico.
- 🔌 **API REST (FastAPI):** rotas documentadas no Swagger, com Response Models e tratamento de erros.

---

## 🛠️ Tecnologias
- **Python 3.14.6** (Windows)
- **Streamlit** e **Plotly** - dashboard e gráficos
- **FastAPI + Uvicorn** - API REST
- **Selenium + BeautifulSoup** - coleta de notícias
- **Requests + Open-Meteo** - dados climáticos reais
- **HuggingFace Transformers + PyTorch** - modelos de IA locais
- **Pandas** - manipulação dos dados

Modelos usados:
- `cardiffnlp/twitter-xlm-roberta-base-sentiment` - sentimento das notícias (~1,1 GB)
- `Qwen/Qwen2.5-0.5B-Instruct` - resumo com IA generativa (~1 GB)

---

## 📁 Estrutura do Projeto
```
Projeto_bloco/
├── app.py                  # Página inicial do dashboard
├── api.py                  # API FastAPI
├── llm_service.py          # Modelo de sentimento das notícias
├── resumo_service.py       # Modelo de resumo e montagem do prompt
├── clima_service.py        # Coleta do clima real (Open-Meteo) e alertas
├── coleta_dados.py         # Coleta de notícias (Selenium + BeautifulSoup)
├── avaliar_modelos.py      # Comparação dos modelos de sentimento (TP4)
├── testar_erros.py         # Testa as respostas de erro da API e salva o log
├── requirements.txt        # Dependências com versões fixas
├── data/
│   ├── noticias.csv             # Notícias coletadas
│   ├── clima.csv                # Último clima coletado (reserva sem internet)
│   ├── avaliacao_modelos.csv    # Comparação dos modelos de sentimento
│   └── historico_resumos.csv    # Registro de todos os resumos gerados
├── docs/
│   ├── project_charter.md
│   ├── data_summary_report.md
│   ├── escolha_modelo.md        # Escolha do modelo de sentimento (TP4)
│   ├── relatorio_final.md       # Relatório final: modelo de resumo, prompt e resultados
│   └── evidencias/              # Log e prints dos testes de erro da API
└── pages/
    ├── 1_📊_Indicadores_Climaticos.py
    ├── 2_📰_Noticias_e_Raspagem.py
    ├── 3_📥_Upload_e_Exportacao.py
    ├── 4_Analise_com_IA.py
    └── 5_Resumo_com_IA.py
```

---

## 🚀 Como Executar o Projeto Localmente (Windows)

### 1. Clone o repositório
```powershell
git clone https://github.com/juniorsamcap/Projeto_bloco.git
cd Projeto_bloco
```

### 2. Crie e ative o ambiente virtual
```powershell
python -m venv .venv
.venv\Scripts\activate
```
> Se aparecer erro de "execução de scripts desabilitada", rode `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` e tente de novo.

### 3. Instale as dependências
```powershell
python -m pip install -r requirements.txt
```

### 4. (Opcional) Atualize as notícias e o clima
Os arquivos `data/noticias.csv` e `data/clima.csv` já vêm preenchidos. Para coletar de novo:
```powershell
python coleta_dados.py
python clima_service.py
```
> A coleta de notícias precisa do Google Chrome instalado. O clima também é atualizado sozinho quando a página de indicadores é aberta.

### 5. Ligue a API (Terminal 1)
```powershell
uvicorn api:app
```
Aguarde **"Modelo carregado com sucesso!"**, **"Modelo de resumo carregado com sucesso!"** e **"Application startup complete"**.
> Na primeira execução os dois modelos (~2 GB no total) são baixados da HuggingFace. Nas próximas vezes eles carregam direto do computador, sem internet. Com 8 GB de RAM, o carregamento pode demorar alguns minutos; fechar abas do navegador ajuda.

### 6. Ligue o dashboard (Terminal 2)
Abra um segundo terminal, ative o ambiente virtual (`.venv\Scripts\activate`) e rode:
```powershell
streamlit run app.py
```
O dashboard abre em **http://localhost:8501**.

> A API e o dashboard precisam ficar ligados ao mesmo tempo, cada um no seu terminal.

---

## 🔌 Rotas da API
Documentação interativa (Swagger): **http://127.0.0.1:8000/docs**

| Método | Rota | Descrição |
|---|---|---|
| GET | `/` | Confirma que a API está online |
| GET | `/noticias` | Lista as notícias coletadas |
| POST | `/noticias` | Cadastra uma nova notícia |
| GET | `/llm/status` | Mostra se os dois modelos de IA estão carregados |
| POST | `/processar_texto` | Analisa o sentimento de um texto |
| GET | `/llm/contexto-preparado` | Monta um prompt simples com as notícias |
| POST | `/llm/resumo` | Gera o resumo inteligente de clima + notícias |

### Exemplo: `POST /llm/resumo`
Requisição:
```json
{"foco": "alertas", "dias_clima": 14}
```
A resposta traz o resumo, o tempo que o modelo levou, as contagens de notícias por sentimento, os dias de alerta por cidade e o prompt usado.

### Tratamento de erros
Todos os erros seguem o mesmo formato:
```json
{"erro": true, "status_code": 422, "mensagem": "Dados de entrada inválidos. Verifique os campos enviados."}
```

| Código | Quando acontece |
|---|---|
| 422 | Texto muito curto, campo faltando, foco ou período inválido |
| 503 | Modelo de IA não carregado ou dados de clima indisponíveis |
| 404 | Arquivo de notícias não encontrado ou rota inexistente |
| 500 | Erro inesperado no processamento |

---

## ✅ Testes
### Testes automáticos dos erros da API
Com a API ligada:
```powershell
python testar_erros.py
```
O script manda requisições com erro de propósito, compara o status recebido com o esperado e salva as respostas em `docs/evidencias/log_testes_erros.md`.

Para testar o erro 503 (modelo indisponível), ligue a API com um modelo que não existe:
```powershell
$env:MODELO_SENTIMENTO="modelo-inexistente/teste-503"
uvicorn api:app
```
Para voltar ao normal: `Remove-Item Env:MODELO_SENTIMENTO` e ligue a API de novo.

Os prints do Swagger e do terminal ficam em `docs/evidencias/`.

### Testes dos resumos
Cada resumo gerado pela página **Resumo com IA** fica registrado em `data/historico_resumos.csv`, com data, hora, foco, tempo e texto.

---

## 📄 Documentação (TDSP)
- [`docs/project_charter.md`](docs/project_charter.md) - problema de negócio, objetivo, arquitetura e alinhamento com ODS/ESG
- [`docs/data_summary_report.md`](docs/data_summary_report.md) - fontes, coleta e integração dos dados
- [`docs/escolha_modelo.md`](docs/escolha_modelo.md) - escolha do modelo de sentimento (TP4)
- [`docs/relatorio_final.md`](docs/relatorio_final.md) - modelo de resumo, engenharia de prompt, testes e resultados

---

Dados meteorológicos: [Open-Meteo.com](https://open-meteo.com/) (licença CC BY 4.0).