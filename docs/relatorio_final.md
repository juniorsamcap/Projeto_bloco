# Relatório Final - Dashboard ODS 13 (TP5)

Este relatório fecha o ciclo do projeto no modelo TDSP. Ele descreve a solução final, explica a escolha do modelo de resumo e da engenharia de prompt, e mostra como cada etapa contribui para o problema de negócio.

## 1. Resumo da Solução
O Dashboard ODS 13 junta dados climáticos reais de três capitais (São Paulo, Rio de Janeiro e Curitiba) com notícias ambientais coletadas de portais públicos. Dois modelos de IA rodam na minha própria máquina, sem nuvem:
- um **classificador** que marca cada notícia como Alerta, Neutro ou Positivo;
- um **modelo generativo** que lê os dados e escreve um resumo com os principais pontos e recomendações.

O usuário escolhe o foco do resumo no dashboard e recebe a resposta na hora, junto com gráficos e o prompt usado.

## 2. Ciclo de Ciência de Dados aplicado
| Etapa TDSP | O que foi feito | Arquivos |
|---|---|---|
| Entendimento do negócio | Problema e público definidos no Project Charter | `docs/project_charter.md` |
| Aquisição e entendimento dos dados | Web scraping das notícias e API Open-Meteo para o clima | `coleta_dados.py`, `clima_service.py`, `docs/data_summary_report.md` |
| Preparação | Filtros nos títulos, médias por cidade, dias de alerta | `coleta_dados.py`, `clima_service.py` |
| Modelagem | Classificador de sentimento (TP4) e modelo de resumo com prompt (TP5) | `llm_service.py`, `resumo_service.py` |
| Avaliação | Comparação de 3 classificadores nas manchetes reais; testes de erro da API; histórico dos resumos | `avaliar_modelos.py`, `testar_erros.py`, `data/historico_resumos.csv` |
| Implantação | API FastAPI + dashboard Streamlit rodando localmente | `api.py`, `app.py`, `pages/` |

## 3. Modelo de Resumo
### Modelo escolhido
`Qwen/Qwen2.5-0.5B-Instruct`, da HuggingFace.

### Critérios da escolha
- **Desempenho:** é um modelo de instrução (feito para seguir pedidos), multilíngue e com suporte a português. Mesmo pequeno, consegue organizar os dados em tópicos e seguir um formato pedido.
- **Custo computacional local:** tem cerca de 0,5 bilhão de parâmetros (download de aproximadamente 1 GB). Roda só na CPU e cabe na memória junto com o classificador do TP4, numa máquina com 8 GB de RAM e sem GPU (Intel Core i5-1235U).
- **Acessibilidade:** é gratuito, de licença aberta (Apache 2.0) e não precisa de chave nem de internet depois do primeiro download. Isso garante que a apresentação funciona mesmo sem conexão e sem custo.

### Por que não outras opções
- **APIs online (ChatGPT, Gemini etc.):** dariam textos melhores, mas exigem chave, têm limite de uso e dependem de internet. Também mudaria a decisão do TP4 de manter a IA local.
- **Modelos maiores (1,5B ou mais):** ficariam lentos demais na CPU e disputariam a memória com o navegador e o classificador.
- **PTT5 de resumo (avaliado no TP4):** licença não comercial e lento; além disso, ele só resume, não segue instruções de foco.

### Por que sumarização (Opção 2 do enunciado)
Comparei as três opções propostas. A **memória conversacional** deixaria cada resposta mais lenta conforme o histórico cresce, e modelos pequenos inventam informação com facilidade numa conversa livre. O **agente inteligente** precisaria de um modelo grande para decidir quais ferramentas usar. A **sumarização** aproveita tudo o que o projeto já tinha (a rota de contexto do TP3, o classificador do TP4 e o clima real), usa um prompt único e previsível e é a mais fácil de testar com exemplos reais.

## 4. Engenharia de Prompt
O prompt é montado em `resumo_service.py` e tem duas partes.

**Mensagem de sistema (fixa):**
- **Papel:** analista de clima e sustentabilidade que apoia gestores públicos, ONGs e voluntários no ODS 13.
- **Regras:** usar somente os dados fornecidos, não inventar números nem fatos, responder em português do Brasil de forma curta e direta.

**Mensagem do usuário (montada com os dados do momento):**
1. **DADOS CLIMÁTICOS REAIS:** uma linha por cidade com temperatura média e máxima, umidade e chuva acumulada.
2. **DIAS DE ALERTA:** lista dos dias que passaram dos limites.
3. **NOTÍCIAS:** cada título com o sentimento dado pelo classificador entre colchetes, por exemplo `[Alerta]`.
4. **TAREFA:** um modelo de resposta com lacunas `<...>` para preencher, que muda conforme o foco escolhido:
   - *geral*: uma linha de clima por cidade, dois assuntos das notícias e duas recomendações ligadas ao ODS 13;
   - *alertas*: cada dia de alerta, as notícias em Alerta e três ações preventivas;
   - *noticias*: três temas principais e quais notícias pedem mais atenção.

### Ajuste feito a partir do primeiro teste
Na primeira versão, a tarefa era uma instrução aberta ("faça até 3 tópicos sobre o clima...") e vinha antes dos dados. O resumo saiu genérico, sem citar nenhum número ou cidade, e levou cerca de 88 s. Mudei três coisas:
- troquei a instrução aberta por um **modelo de resposta com lacunas**, que modelos pequenos seguem melhor;
- coloquei a **tarefa depois dos dados**, para o formato pedido ser a última coisa que o modelo lê;
- reduzi o limite de resposta de **300 para 220 tokens**, para diminuir o tempo na CPU.

### Outras decisões
- **Dados resumidos em vez de tabelas inteiras:** o modelo é pequeno, então mandar médias por cidade deixa o prompt curto e evita confusão.
- **Sentimento junto de cada notícia:** o resultado de um modelo vira entrada do outro, e o resumo consegue destacar o que é risco.
- **Regra de não inventar dados:** reduz o risco de o modelo criar números que não existem.
- **Geração sem sorteio (`do_sample=False`):** o mesmo prompt gera o mesmo texto, o que facilita testar e comparar.
- **Prompt visível no dashboard:** qualquer pessoa pode conferir exatamente o que foi enviado ao modelo.

## 5. Integração
- **Rota:** `POST /llm/resumo` (corpo: `foco` = geral, alertas ou noticias; `dias_clima` = 7 a 30).
- **Resposta (Response Model `RespostaResumo`):** foco, modelo, resumo, tempo de processamento, total de notícias, notícias por sentimento, dias de alerta no clima, alertas por cidade e o prompt usado.
- **Erros:** 503 se o modelo de resumo não carregou ou se não há dados de clima; 404 se não existe o CSV de notícias; 422 para foco ou período inválidos; 500 para falha inesperada na geração.
- **Carregamento:** os dois modelos são carregados uma vez quando a API liga (`lifespan`), como no TP4.
- **Página:** `pages/5_Resumo_com_IA.py` mostra o resumo, métricas, gráfico de notícias por sentimento, gráfico de dias de alerta por cidade, o prompt e o histórico.

## 6. Testes e Evidências
- **Erros da API:** `testar_erros.py` rodado com o modelo carregado e sem o modelo (6 de 6 com o status esperado nas duas situações). Log e prints em `docs/evidencias/`.
- **Resumos:** gerei o primeiro resumo com o foco geral usando os dados reais do dia. O texto saiu genérico, sem usar os números, e levou cerca de 88 s. A partir desse resultado ajustei o prompt (seção 4) e gerei novamente. Cada execução, com data, hora, foco, tempo e texto gerado, está registrada em `data/historico_resumos.csv`.
- **Compatibilidade:** `pip check` sem conflitos com as versões fixadas no `requirements.txt` (Python 3.14.6, Windows).

## 7. Insights gerados e impacto (ESG e ODS 13)
Com os dados reais coletados para a entrega, o painel mostrou dias de calor forte concentrados no Rio de Janeiro e um pico em São Paulo no mesmo período, enquanto as notícias classificadas como Alerta tratavam de emergências ambientais. O resumo junta esses dois lados numa leitura só e sugere ações, o que antes exigia abrir vários sites e cruzar a informação manualmente.

- **ODS 13.1 (resiliência a riscos climáticos):** os alertas de calor e chuva ajudam a antecipar ações, como avisos à população e atenção a grupos vulneráveis.
- **ODS 13.3 (conscientização):** o resumo em linguagem simples deixa a informação acessível para quem não é especialista.
- **ESG - Ambiental:** monitoramento contínuo de clima e de notícias ambientais.
- **ESG - Governança:** fontes públicas, prompt visível e histórico dos resumos dão transparência e permitem auditar o que a IA respondeu.

## 8. Limitações
- O modelo de resumo é pequeno; o texto pode sair genérico, repetir pontos ou cometer pequenos erros. Por isso o dashboard mostra os números e gráficos ao lado do resumo, para o usuário conferir.
- O tempo de resposta na CPU é alto (perto de 1 minuto ou mais), porque a máquina não tem GPU e a memória fica disputada com o navegador e o outro modelo.
- O resumo usa só os títulos das notícias, não o texto completo das matérias.
- Não houve comparação entre vários modelos generativos, como fiz com os classificadores no TP4; a escolha foi feita pelos critérios de tamanho, licença e suporte a português.
- Os limites de alerta (32 °C e 50 mm) são referências que defini para o projeto.

## 9. Próximos Passos
- Coletar o texto completo das matérias para resumos mais ricos.
- Comparar o Qwen2.5 0.5B com outros modelos generativos pequenos nas mesmas condições.
- Incluir mais cidades e indicadores (por exemplo, qualidade do ar).
- Agendar a coleta automática das notícias e do clima.