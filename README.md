# 🌍 Dashboard ODS 13 - Monitoramento Climático

Aplicação web interativa para visualização e análise de dados meteorológicos regionais e notícias ambientais, alinhada ao **ODS 13 (Ação Contra a Mudança Global do Clima)** da ONU.

---

## 📌 Sobre o Projeto
A falta de visualização simples de dados meteorológicos dificulta o acompanhamento de variações de temperatura e umidade. Este painel foi desenvolvido para democratizar o acesso a essas informações, apoiando a tomada de decisão de ONGs, gestores locais e voluntários.

Além dos indicadores climáticos, o projeto coleta notícias ambientais de portais públicos e usa um **modelo de Inteligência Artificial rodando localmente** para classificar cada notícia como **Alerta**, **Neutro** ou **Positivo**.

---

## ⚙️ Funcionalidades
- 📊 **Indicadores Climáticos:** gráficos e métricas de temperatura e umidade por cidade.
- 📰 **Notícias & Raspagem:** notícias coletadas com Selenium + BeautifulSoup, listadas e cadastradas pela API.
- 📥 **Upload & Exportação:** envio de CSV e download de relatório.
- 🤖 **Análise com IA:** análise de sentimento de uma notícia ou de todas as notícias coletadas.
- 🔌 **API REST (FastAPI):** rotas documentadas no Swagger, com Response Models e tratamento de erros.

---

## 🛠️ Tecnologias
- **Python** (testado com a versão 3.14)
- **Streamlit** - interface do dashboard
- **FastAPI + Uvicorn** - API REST
- **Selenium + BeautifulSoup** - coleta de notícias
- **HuggingFace Transformers + PyTorch** - modelo de IA local
- **Pandas** - manipulação dos dados

---

## 📁 Estrutura do Projeto
```
Projeto_bloco/
├── app.py                  # Página inicial do dashboard
├── api.py                  # API FastAPI
├── llm_service.py          # Carrega o modelo de IA e faz a análise de sentimento
├── coleta_dados.py         # Coleta de notícias (Selenium + BeautifulSoup)
├── avaliar_modelos.py      # Comparação dos modelos de IA candidatos
├── requirements.txt        # Dependências do projeto
├── data/
│   ├── noticias.csv            # Notícias coletadas
│   └── avaliacao_modelos.csv   # Resultado da comparação dos modelos
├── docs/
│   ├── project_charter.md
│   ├── data_summary_report.md
│   └── escolha_modelo.md       # Justificativa da escolha do modelo de IA
└── pages/
    ├── 1_📊_Indicadores_Climaticos.py
    ├── 2_📰_Noticias_e_Raspagem.py
    ├── 3_📥_Upload_e_Exportacao.py
    └── 4_Analise_com_IA.py
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

### 4. (Opcional) Atualize as notícias
O arquivo `data/noticias.csv` já vem preenchido. Para coletar notícias novas (precisa do Google Chrome instalado):
```powershell
python coleta_dados.py
```

### 5. Ligue a API (Terminal 1)
```powershell
uvicorn api:app
```
Aguarde as mensagens **"Modelo carregado com sucesso!"** e **"Application startup complete"**.
> Na primeira execução o modelo de IA (~1,1 GB) é baixado da HuggingFace. Nas próximas, ele carrega direto do computador, sem internet.

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
| GET | `/llm/status` | Mostra se o modelo de IA está carregado |
| POST | `/processar_texto` | Analisa o sentimento de um texto com a IA local |
| GET | `/llm/contexto-preparado` | Monta um prompt com as notícias para uso em LLMs |

### Exemplo: `POST /processar_texto`
Requisição:
```json
{"texto": "Pará tem 61 cidades em situação de emergência por incêndios florestais"}
```
Resposta (200):
```json
{
  "texto_processado": "Pará tem 61 cidades em situação de emergência por incêndios florestais",
  "tipo_analise": "Análise de sentimento",
  "modelo": "cardiffnlp/twitter-xlm-roberta-base-sentiment",
  "resultado": {
    "sentimento": "Alerta",
    "rotulo_original": "negative",
    "confianca": 0.6737,
    "tempo_processamento_seg": 0.099
  }
}
```

### Tratamento de erros
Todos os erros seguem o mesmo formato:
```json
{"erro": true, "status_code": 422, "mensagem": "Dados de entrada inválidos. Verifique os campos enviados."}
```

| Código | Quando acontece |
|---|---|
| 422 | Texto vazio, muito curto ou campo inválido |
| 503 | Modelo de IA não carregado |
| 404 | Arquivo de notícias não encontrado |
| 500 | Erro inesperado no processamento |

---

## ✅ Testes Realizados
Testes feitos manualmente pelo Swagger (`/docs`) e pelo dashboard:

| Teste | Resultado esperado | Status |
|---|---|---|
| `GET /llm/status` | `"carregado": true` | ✅ |
| `POST /processar_texto` com manchete de incêndios | 200 e sentimento "Alerta" | ✅ |
| `POST /processar_texto` com `{"texto": "oi"}` | 422 com mensagem de erro | ✅ |
| Página de notícias listando via `GET /noticias` | Tabela com as notícias | ✅ |
| Cadastro de notícia pelo dashboard (`POST /noticias`) | Notícia aparece na tabela | ✅ |
| Cadastro com título curto pelo dashboard | Erro 422 exibido na tela | ✅ |
| Página Análise com IA - panorama geral | 2 alertas, 10 neutras, 2 positivas | ✅ |

---

## 📄 Documentação
- [`docs/project_charter.md`](docs/project_charter.md) - objetivo, arquitetura e entregáveis
- [`docs/data_summary_report.md`](docs/data_summary_report.md) - fontes e estrutura dos dados
- [`docs/escolha_modelo.md`](docs/escolha_modelo.md) - justificativa da escolha do modelo de IA