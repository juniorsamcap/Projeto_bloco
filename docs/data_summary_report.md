# Data Summary Report - ODS 13

## Fontes de Dados
1. **Notícias Climáticas:** Extraídas dinamicamente do portal Agência Brasil (Meio Ambiente) via Selenium.
2. **Indicadores Climáticos:** Dados estruturados de temperatura e umidade regional.

## Estrutura do Conjunto de Dados (`data/noticias.csv`)
- **Titulo:** Manchete da notícia coletada (string).
- **Tamanho_Titulo:** Quantidade total de caracteres (integer).
- **Qtd_Palavras:** Total de palavras presentes no título (integer).
- **Fonte:** Origem do dado (string).

## Potencial de Aplicação com LLM (Próxima Etapa)
- **Análise de Sentimentos:** Classificação de notícias em Alerta, Neutro ou Positivo.
- **Resumos Automáticos:** Síntese em linguagem natural dos principais fatos ambientais do dia.
- **Sistemas de Q&A (RAG):** Assistente virtual para responder dúvidas com base no histórico armazenado.