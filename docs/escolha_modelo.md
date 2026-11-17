# Escolha do Modelo de IA (LLM Local) - ODS 13

## Objetivo
Classificar as manchetes ambientais coletadas pelo projeto em **Alerta**, **Neutro** ou **Positivo**, rodando o modelo inteiramente na máquina local (sem nuvem e sem custo), integrado à API FastAPI.

Essa tarefa já estava prevista no Data Summary Report do TP3 ("Análise de Sentimentos: Classificação de notícias em Alerta, Neutro ou Positivo").

## Ambiente de Execução
- **Processador:** Intel Core i5-1235U (12ª geração, 10 núcleos)
- **Memória RAM:** 8 GB
- **Placa de vídeo:** Intel UHD integrada (sem GPU dedicada/CUDA) → o modelo roda **apenas na CPU**
- **Sistema:** Windows + Python 3.14 em ambiente virtual (`.venv`)
- **Bibliotecas:** `transformers` (HuggingFace) + `torch` (versão CPU)

Como a máquina tem pouca memória e não tem GPU, modelos grandes de geração de texto (como Llama ou Mistral, com bilhões de parâmetros) ficaram de fora logo no início. O foco foi em modelos da família **BERT** (encoder), que são menores e feitos justamente para tarefas de classificação.

## Modelos Candidatos
| Modelo | Tipo | Tamanho | Licença / Acesso |
|---|---|---|---|
| `lxyuan/distilbert-base-multilingual-cased-sentiments-student` | DistilBERT - sentimento | ~540 MB | Apache-2.0 |
| `cardiffnlp/twitter-xlm-roberta-base-sentiment` | XLM-RoBERTa - sentimento | ~1,1 GB | Público no HuggingFace Hub |
| `MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7` | mDeBERTa - zero-shot | ~1,1 GB | MIT |
| `recogna-nlp/ptt5-base-summ-xlsum` | PTT5 - resumo em PT-BR | ~900 MB | CC BY-NC-SA 4.0 |

Todos aceitam português e podem ser baixados gratuitamente, sem cadastro, pela biblioteca Transformers.

O **PTT5** (resumo) foi descartado ainda na pesquisa: gerar texto na CPU é bem mais lento que classificar, e a licença é não comercial. Os outros três foram testados na prática.

## Teste Prático com os Dados do Projeto
Em vez de escolher só pela descrição dos modelos, criei o script `avaliar_modelos.py`, que roda os três candidatos sobre as **14 manchetes reais** de `data/noticias.csv`. Os modelos são carregados um de cada vez e liberados da memória em seguida, por causa dos 8 GB de RAM. O resultado completo está em `data/avaliacao_modelos.csv`.

### Exemplos do resultado
| Manchete | DistilBERT | XLM-RoBERTa | mDeBERTa |
|---|---|---|---|
| Pará tem 61 cidades em situação de emergência por incêndios florestais | Positivo (44%) ❌ | **Alerta (67%)** ✅ | Alerta (93%) ✅ |
| Estudo alerta para diminuição da conectividade de rios na Amazônia | Positivo (66%) ❌ | **Alerta (61%)** ✅ | Alerta (88%) ✅ |
| Fundo Amazônia recebe segundo desembolso da Irlanda, de € 5 milhões | Positivo (69%) ✅ | Neutro (83%) | Alerta (57%) ❌ |
| Ibama auxilia na reabilitação de peixes-boi na Ilha do Marajó | Positivo (57%) ✅ | Neutro (66%) | Alerta (43%) ❌ |
| Presidência da COP30 apresenta Relatório de Implementação... | Positivo (58%) ❌ | **Neutro (85%)** ✅ | Neutro (50%) ✅ |

### Resumo
| Modelo | Alertas | Neutras | Positivas | Tempo médio por notícia |
|---|---|---|---|---|
| DistilBERT | 1 | 0 | 13 | 0,10 s |
| **XLM-RoBERTa** | **2** | **10** | **2** | **0,60 s** |
| mDeBERTa (zero-shot) | 11 | 2 | 1 | 6,65 s |

## Análise dos Critérios

### 1. Desempenho
- **DistilBERT:** classificou quase tudo como Positivo, inclusive a notícia de emergência por incêndios. Para um painel de monitoramento climático, deixar passar um alerta é o pior erro possível.
- **mDeBERTa (zero-shot):** foi para o extremo oposto e marcou 11 de 14 manchetes como Alerta, inclusive notícias boas (Fundo Amazônia, reabilitação de peixes-boi). Muitos alarmes falsos fazem o usuário deixar de confiar nos alertas.
- **XLM-RoBERTa:** foi o único que **identificou os dois alertas reais sem gerar nenhum alerta falso**. A maioria das manchetes ficou como Neutro, o que faz sentido, já que são textos jornalísticos e institucionais, com tom mais informativo.

O XLM-RoBERTa é um modelo da família BERT, pré-treinado em cerca de 198 milhões de tweets em vários idiomas e ajustado para análise de sentimento em 8 línguas, entre elas o **português**. Ele devolve três classes (positive, neutral, negative), que no projeto viraram Positivo, Neutro e Alerta.

### 2. Custo Computacional Local
- Roda **somente na CPU**, sem precisar de GPU.
- Ocupa cerca de 1,1 GB em disco e funcionou sem travar a máquina de 8 GB.
- Na API, a **primeira análise levou 0,56 s** e as seguintes ficaram em torno de **0,1 s**, porque o modelo já está "aquecido" na memória.
- O DistilBERT é mais leve (0,10 s), mas a diferença não compensa o erro nos alertas. O mDeBERTa é inviável para o painel: analisar as 14 notícias levaria mais de 1 minuto e meio.

### 3. Acessibilidade Local
- Download gratuito direto do HuggingFace Hub, sem cadastro e sem token.
- Carregado com uma única linha: `pipeline("text-classification", model=NOME_MODELO)`.
- Depois do primeiro download, o modelo fica salvo no computador (`.cache/huggingface`) e funciona **sem internet**.
- Dependências: `transformers`, `torch`, `sentencepiece` e `tiktoken` (as duas últimas são necessárias para o tokenizer do XLM-RoBERTa no Windows).

## Modelo Escolhido
**`cardiffnlp/twitter-xlm-roberta-base-sentiment`**, por ter o melhor equilíbrio entre acerto nos alertas, tempo de resposta aceitável e facilidade de rodar localmente.

## Como a Integração Foi Feita
1. **`llm_service.py`:** arquivo separado que cuida só da IA. Carrega o modelo (`carregar_modelo()`), informa se ele está pronto (`modelo_disponivel()`) e faz a análise (`analisar_sentimento(texto)`), devolvendo sentimento, rótulo original, confiança e tempo.
2. **`api.py`:** quando a API liga, o modelo é carregado uma única vez (função `lifespan`). Foram criadas duas rotas:
   - `POST /processar_texto`: recebe `{"texto": "..."}` e devolve o resultado estruturado pelo Response Model `RespostaProcessamento`;
   - `GET /llm/status`: informa se o modelo foi carregado.
3. **Tratamento de erros:** todas as respostas de erro saem no mesmo formato JSON (`erro`, `status_code`, `mensagem`):
   - **422:** texto vazio ou com menos de 10 caracteres;
   - **503:** modelo de IA não carregado;
   - **404:** arquivo de notícias não encontrado;
   - **500:** erro inesperado durante o processamento.
4. **Dashboard:** a página `pages/4_Analise_com_IA.py` consome a API para analisar uma notícia escolhida ou um texto digitado, e também gera um panorama de todas as notícias (quantidade de alertas, neutras e positivas).

## Limitações Conhecidas
- O modelo foi treinado com **tweets**, não com manchetes. Por isso a confiança nas manchetes ficou entre 50% e 85%, ou seja, o modelo acerta a categoria, mas nem sempre com muita certeza.
- Algumas notícias positivas (ex.: Fundo Amazônia) ficaram como **Neutro**. Para o objetivo do painel, isso é menos grave do que perder um alerta.
- O site do Ministério publica algumas manchetes em **inglês**. Como o modelo é multilíngue, elas foram mantidas e analisadas normalmente.
- A primeira execução precisa de internet para baixar o modelo (~1,1 GB).

## Ligação com o Tema do Projeto
Os indicadores climáticos do painel mostram **o que está acontecendo** com o clima (temperatura e umidade). A análise de sentimento das notícias mostra **como esses eventos estão sendo noticiados**: calor extremo, queimadas, enchentes e ações de combate. Juntas, as duas partes dão uma visão mais completa para quem acompanha o ODS 13.