# Data Summary Report - ODS 13 (TP5 - versão final)

## Fontes de Dados
1. **Notícias ambientais (web scraping):** dois portais públicos.
   - Agência Brasil - Meio Ambiente (`agenciabrasil.ebc.com.br/meio-ambiente`)
   - Ministério do Meio Ambiente e Mudança do Clima (`gov.br/mma/pt-br/noticias`)
2. **Clima real (API pública):** Open-Meteo (`api.open-meteo.com/v1/forecast`), gratuita para uso não comercial, sem chave. Os dados são liberados sob a licença CC BY 4.0 e o crédito aparece no rodapé da página de indicadores.
3. **Notícias enviadas pelo usuário:** cadastradas pelo dashboard ou pela API (`POST /noticias`).

## Como os dados foram coletados
### Notícias (`coleta_dados.py`)
- O **Selenium** (Chrome em modo headless) abre cada página e espera o carregamento.
- O **BeautifulSoup** lê o HTML (`page_source`) e extrai os textos das tags `h2` e `h3`.
- Filtros: títulos entre 30 e 180 caracteres, sem repetição e sem textos de menu ou da agenda do ministro.
- Limite de 10 notícias por fonte. Se uma fonte falhar, a coleta continua nas outras.

### Clima (`clima_service.py`)
- Uma requisição por cidade (São Paulo, Rio de Janeiro e Curitiba), usando latitude e longitude.
- Variáveis diárias: temperatura média, temperatura máxima, umidade relativa média e chuva acumulada.
- O período é escolhido no dashboard (7 a 30 dias anteriores + o dia atual).
- Cada busca que dá certo é salva em `data/clima.csv`. Se a API falhar, o sistema usa esse arquivo e avisa na tela.

## Como os dados foram integrados e usados ao longo do projeto
1. **Coleta:** as notícias vão para `data/noticias.csv` e o clima para `data/clima.csv`.
2. **Acesso:** o dashboard não lê as notícias direto do arquivo; ele consulta a API (`GET /noticias`). O clima é carregado pelo `clima_service.py`, que é usado tanto pela página de indicadores quanto pela API.
3. **Preparação:** o clima é resumido por cidade (médias, máxima e chuva total) e os dias acima dos limites viram alertas (`identificar_alertas`).
4. **Classificação:** cada notícia recebe um sentimento (Alerta, Neutro ou Positivo) do modelo XLM-RoBERTa.
5. **Prompt:** clima por cidade + dias de alerta + notícias com sentimento são organizados em um prompt.
6. **Resumo:** o modelo Qwen2.5 gera o texto e a API devolve também as contagens usadas nos gráficos.
7. **Registro:** cada resumo gerado é salvo em `data/historico_resumos.csv`.

## Estrutura dos Conjuntos de Dados
### `data/noticias.csv`
- **Titulo:** manchete coletada (texto)
- **Tamanho_Titulo:** quantidade de caracteres (inteiro)
- **Qtd_Palavras:** quantidade de palavras (inteiro)
- **Fonte:** origem da notícia (texto)

### `data/clima.csv`
- **Data:** dia da medição (data)
- **Cidade:** São Paulo, Rio de Janeiro ou Curitiba (texto)
- **Temperatura:** temperatura média do dia, em °C (decimal)
- **Temp_Maxima:** temperatura máxima do dia, em °C (decimal)
- **Umidade:** umidade relativa média do dia, em % (decimal)
- **Chuva_mm:** chuva acumulada no dia, em mm (decimal)

### `data/avaliacao_modelos.csv` (TP4)
Comparação de três modelos de sentimento nas manchetes reais (DistilBERT, XLM-RoBERTa e mDeBERTa), com a classificação e a confiança de cada um.

### `data/historico_resumos.csv` (TP5)
- **Data_Hora:** quando o resumo foi gerado
- **Foco:** geral, alertas ou noticias
- **Modelo:** modelo usado no resumo
- **Tempo_seg:** tempo que o modelo levou para escrever
- **Resumo:** texto gerado

## Aplicação com IA
- **Análise de sentimento (TP4):** classifica as notícias em Alerta, Neutro ou Positivo. Nas 14 manchetes coletadas o resultado foi de 2 alertas, 10 neutras e 2 positivas.
- **Sumarização com LLM (TP5):** gera um resumo com insights e recomendações a partir do clima real e das notícias classificadas, com três focos possíveis. Os detalhes do modelo e do prompt estão em `docs/relatorio_final.md`.

## Observações sobre a Qualidade dos Dados
- O portal do Ministério publica algumas manchetes em inglês. Elas foram mantidas porque os dois modelos são multilíngues.
- A Agência Brasil retornou menos manchetes (4) que o Ministério (10) com o filtro de tags `h2` e `h3`.
- O valor do dia atual no clima ainda é parcial, porque o dia não terminou.
- O Open-Meteo combina modelos meteorológicos; os valores são estimativas para o ponto da cidade, não a leitura de uma estação específica.