"""
Testa as respostas de erro da API e guarda o resultado como evidência.

Precisa da API rodando (uvicorn api:app). O script manda requisições erradas de propósito
e salva exatamente o que a API respondeu em docs/evidencias/log_testes_erros.md.
Cada execução é adicionada no final do arquivo, com data e hora.
"""

import json
import os
from datetime import datetime

import requests

URL_API = "http://127.0.0.1:8000"
CAMINHO_LOG = os.path.join("docs", "evidencias", "log_testes_erros.md")

# Cada teste: descrição, método, rota, corpo enviado,
# status esperado com o modelo carregado e status esperado sem o modelo
TESTES = [
    ("Texto curto demais (menos de 10 caracteres)", "POST", "/processar_texto", {"texto": "oi"}, 422, 422),
    ("Campo 'texto' não enviado", "POST", "/processar_texto", {}, 422, 422),
    ("Texto só com espaços em branco", "POST", "/processar_texto", {"texto": " " * 15}, 422, 503),
    ("Notícia com título curto demais", "POST", "/noticias", {"Titulo": "abc"}, 422, 422),
    ("Rota que não existe", "GET", "/rota-inexistente", None, 404, 404),
    (
        "Texto válido (para comparar com os erros)",
        "POST",
        "/processar_texto",
        {"texto": "Pará tem 61 cidades em situação de emergência por incêndios florestais"},
        200,
        503,
    ),
]


def consultar_status_modelo():
    """Pergunta para a própria API qual modelo está configurado e se ele carregou."""
    resposta = requests.get(f"{URL_API}/llm/status", timeout=10)
    return resposta.json()


def enviar(metodo, rota, corpo):
    """Faz a requisição GET ou POST para a API."""
    if metodo == "GET":
        return requests.get(f"{URL_API}{rota}", timeout=30)
    return requests.post(f"{URL_API}{rota}", json=corpo, timeout=30)


def main():
    try:
        status = consultar_status_modelo()
    except requests.exceptions.ConnectionError:
        print("Não consegui falar com a API. Ligue ela antes com: uvicorn api:app")
        return

    carregado = status["carregado"]
    agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    linhas = [
        f"## Execução em {agora}\n",
        f"- Modelo configurado: `{status['modelo']}`",
        f"- Modelo carregado: {'sim' if carregado else 'não'}\n",
    ]

    print(f"Modelo carregado: {'sim' if carregado else 'não'}\n")
    acertos = 0

    for numero, (descricao, metodo, rota, corpo, esperado_com, esperado_sem) in enumerate(TESTES, start=1):
        # O status esperado muda dependendo se o modelo está carregado ou não
        esperado = esperado_com if carregado else esperado_sem
        resposta = enviar(metodo, rota, corpo)
        ok = resposta.status_code == esperado
        if ok:
            acertos += 1

        resultado = "OK" if ok else "DIFERENTE DO ESPERADO"
        print(f"{numero}. {descricao}: recebido {resposta.status_code}, esperado {esperado} -> {resultado}")

        linhas.append(f"### {numero}. {descricao}")
        linhas.append(f"- Requisição: `{metodo} {rota}`")
        if corpo is not None:
            linhas.append(f"- Enviado: `{json.dumps(corpo, ensure_ascii=False)}`")
        linhas.append(f"- Status recebido: **{resposta.status_code}** (esperado: {esperado}) -> {resultado}")
        linhas.append("```json")
        linhas.append(json.dumps(resposta.json(), ensure_ascii=False, indent=2))
        linhas.append("```\n")

    linhas.append(f"**Resumo:** {acertos} de {len(TESTES)} testes com o status esperado.\n")
    print(f"\nResumo: {acertos} de {len(TESTES)} testes com o status esperado.")

    # Cria a pasta se não existir e adiciona esta execução no final do log
    os.makedirs(os.path.dirname(CAMINHO_LOG), exist_ok=True)
    arquivo_novo = not os.path.exists(CAMINHO_LOG)
    with open(CAMINHO_LOG, "a", encoding="utf-8") as arquivo:
        if arquivo_novo:
            arquivo.write("# Log dos testes de erro da API\n\n")
            arquivo.write("Gerado pelo script `testar_erros.py` com as respostas reais da API.\n\n")
        arquivo.write("\n".join(linhas) + "\n")

    print(f"Log salvo em {CAMINHO_LOG}")


if __name__ == "__main__":
    main()