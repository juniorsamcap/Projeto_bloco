# Data Summary Report - ODS 13

## Fontes de Dados
1. **Notícias Climáticas:** Coletadas de dois portais públicos:
   - Agência Brasil - Meio Ambiente (`agenciabrasil.ebc.com.br/meio-ambiente`)
   - Ministério do Meio Ambiente e Mudança do Clima (`gov.br/mma/pt-br/noticias`)
2. **Indicadores Climáticos:** Dados estruturados de temperatura e umidade regional (São Paulo, Rio de Janeiro e Curitiba).
3. **Notícias enviadas pelo usuário:** Cadastradas pelo dashboard ou pela API (`POST /noticias`), com a fonte "Envio via Dashboard" ou "Envio via API".

## Processo de Coleta
- O **Selenium** (Chrome em modo headless) abre cada página e aguarda o carregamento.
- O **BeautifulSoup** lê o HTML (`page_source`) e extrai os textos das tags `h2` e `h3`.
- **Filtros aplicados:** títulos entre 30 e 180 caracteres, sem repetição e sem textos de menu ou da agenda do ministro.
- Limite de 10 notícias por fonte, para manter a coleta rápida.
- Se uma fonte falhar, a coleta continua nas demais.

## Estrutura do Conjunto de Dados (`data/noticias.csv`)
- **Titulo:** Manchete da notícia coletada (string).
- **Tamanho_Titulo:** Quantidade total de caracteres (integer).
- **Qtd_Palavras:** Total de palavras presentes no título (integer).
- **Fonte:** Origem do dado (string).

## Avaliação dos Modelos (`data/avaliacao_modelos.csv`)
Resultado do script `avaliar_modelos.py`, que comparou três modelos da HuggingFace sobre as manchetes coletadas.
- **Titulo:** Manchete analisada (string).
- **DistilBERT (sentimento):** Classificação e confiança do modelo DistilBERT (string, ex.: "Positivo (44%)").
- **XLM-RoBERTa (sentimento):** Classificação e confiança do modelo XLM-RoBERTa (string).
- **mDeBERTa (zero-shot):** Classificação e confiança do modelo mDeBERTa (string).

## Aplicação com LLM
- **Análise de Sentimentos (implementada no TP4):** Cada notícia é classificada em **Alerta**, **Neutro** ou **Positivo** pelo modelo `cardiffnlp/twitter-xlm-roberta-base-sentiment`, rodando localmente. Nas 14 manchetes coletadas o resultado foi de 2 alertas, 10 neutras e 2 positivas.
- **Resumos Automáticos (possível evolução):** Síntese em linguagem natural dos principais fatos ambientais do dia, aproveitando o endpoint `/llm/contexto-preparado`.
- **Sistemas de Q&A (possível evolução):** Assistente virtual para responder dúvidas com base no histórico armazenado.

## Observações sobre a Qualidade dos Dados
- O portal do Ministério publica algumas manchetes também em inglês. Elas foram mantidas, porque o modelo de IA é multilíngue.
- A Agência Brasil retornou menos manchetes (4) que o Ministério (10) com o filtro de tags `h2` e `h3`.
- Os indicadores de temperatura e umidade ainda são dados de exemplo.