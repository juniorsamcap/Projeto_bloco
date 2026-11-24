# Log dos testes de erro da API

Gerado pelo script `testar_erros.py` com as respostas reais da API.

## Execução em 23/11/2026 21:35:09

- Modelo configurado: `cardiffnlp/twitter-xlm-roberta-base-sentiment`
- Modelo carregado: sim

### 1. Texto curto demais (menos de 10 caracteres)
- Requisição: `POST /processar_texto`
- Enviado: `{"texto": "oi"}`
- Status recebido: **422** (esperado: 422) -> OK
```json
{
  "erro": true,
  "status_code": 422,
  "mensagem": "Dados de entrada inválidos. Verifique os campos enviados.",
  "detalhes": [
    "body -> texto: String should have at least 10 characters"
  ]
}
```

### 2. Campo 'texto' não enviado
- Requisição: `POST /processar_texto`
- Enviado: `{}`
- Status recebido: **422** (esperado: 422) -> OK
```json
{
  "erro": true,
  "status_code": 422,
  "mensagem": "Dados de entrada inválidos. Verifique os campos enviados.",
  "detalhes": [
    "body -> texto: Field required"
  ]
}
```

### 3. Texto só com espaços em branco
- Requisição: `POST /processar_texto`
- Enviado: `{"texto": "               "}`
- Status recebido: **422** (esperado: 422) -> OK
```json
{
  "erro": true,
  "status_code": 422,
  "mensagem": "O texto precisa ter pelo menos 10 caracteres (sem contar espaços)."
}
```

### 4. Notícia com título curto demais
- Requisição: `POST /noticias`
- Enviado: `{"Titulo": "abc"}`
- Status recebido: **422** (esperado: 422) -> OK
```json
{
  "erro": true,
  "status_code": 422,
  "mensagem": "Dados de entrada inválidos. Verifique os campos enviados.",
  "detalhes": [
    "body -> Titulo: String should have at least 5 characters"
  ]
}
```

### 5. Rota que não existe
- Requisição: `GET /rota-inexistente`
- Status recebido: **404** (esperado: 404) -> OK
```json
{
  "erro": true,
  "status_code": 404,
  "mensagem": "Not Found"
}
```

### 6. Texto válido (para comparar com os erros)
- Requisição: `POST /processar_texto`
- Enviado: `{"texto": "Pará tem 61 cidades em situação de emergência por incêndios florestais"}`
- Status recebido: **200** (esperado: 200) -> OK
```json
{
  "texto_processado": "Pará tem 61 cidades em situação de emergência por incêndios florestais",
  "tipo_analise": "Análise de sentimento",
  "modelo": "cardiffnlp/twitter-xlm-roberta-base-sentiment",
  "resultado": {
    "sentimento": "Alerta",
    "rotulo_original": "negative",
    "confianca": 0.6737,
    "tempo_processamento_seg": 0.655
  }
}
```

**Resumo:** 6 de 6 testes com o status esperado.

## Execução em 23/11/2026 21:46:10

- Modelo configurado: `modelo-inexistente/teste-503`
- Modelo carregado: não

### 1. Texto curto demais (menos de 10 caracteres)
- Requisição: `POST /processar_texto`
- Enviado: `{"texto": "oi"}`
- Status recebido: **422** (esperado: 422) -> OK
```json
{
  "erro": true,
  "status_code": 422,
  "mensagem": "Dados de entrada inválidos. Verifique os campos enviados.",
  "detalhes": [
    "body -> texto: String should have at least 10 characters"
  ]
}
```

### 2. Campo 'texto' não enviado
- Requisição: `POST /processar_texto`
- Enviado: `{}`
- Status recebido: **422** (esperado: 422) -> OK
```json
{
  "erro": true,
  "status_code": 422,
  "mensagem": "Dados de entrada inválidos. Verifique os campos enviados.",
  "detalhes": [
    "body -> texto: Field required"
  ]
}
```

### 3. Texto só com espaços em branco
- Requisição: `POST /processar_texto`
- Enviado: `{"texto": "               "}`
- Status recebido: **503** (esperado: 503) -> OK
```json
{
  "erro": true,
  "status_code": 503,
  "mensagem": "O modelo de IA não está disponível no momento. Consulte /llm/status e reinicie a API."
}
```

### 4. Notícia com título curto demais
- Requisição: `POST /noticias`
- Enviado: `{"Titulo": "abc"}`
- Status recebido: **422** (esperado: 422) -> OK
```json
{
  "erro": true,
  "status_code": 422,
  "mensagem": "Dados de entrada inválidos. Verifique os campos enviados.",
  "detalhes": [
    "body -> Titulo: String should have at least 5 characters"
  ]
}
```

### 5. Rota que não existe
- Requisição: `GET /rota-inexistente`
- Status recebido: **404** (esperado: 404) -> OK
```json
{
  "erro": true,
  "status_code": 404,
  "mensagem": "Not Found"
}
```

### 6. Texto válido (para comparar com os erros)
- Requisição: `POST /processar_texto`
- Enviado: `{"texto": "Pará tem 61 cidades em situação de emergência por incêndios florestais"}`
- Status recebido: **503** (esperado: 503) -> OK
```json
{
  "erro": true,
  "status_code": 503,
  "mensagem": "O modelo de IA não está disponível no momento. Consulte /llm/status e reinicie a API."
}
```

**Resumo:** 6 de 6 testes com o status esperado.

