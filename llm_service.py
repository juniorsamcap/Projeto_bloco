"""
Serviço de IA do projeto (TP4).

Este arquivo cuida só da parte de inteligência artificial:
carrega o modelo da HuggingFace na máquina local e faz a análise de sentimento.
A API (api.py) apenas chama as funções daqui.
"""

import os
import time
from transformers import pipeline

# Modelo escolhido: XLM-RoBERTa multilíngue (treinado também em português), roda só na CPU.
# Ele foi o que mais acertou nas manchetes reais do projeto (ver avaliar_modelos.py e docs/escolha_modelo.md)
# A variável de ambiente MODELO_SENTIMENTO permite trocar o modelo sem mexer no código.
# Usei isso para testar o erro 503 (modelo indisponível), passando um nome de modelo que não existe.
NOME_MODELO = os.getenv("MODELO_SENTIMENTO", "cardiffnlp/twitter-xlm-roberta-base-sentiment")

# O modelo responde em inglês; aqui traduzo para as categorias usadas no projeto
MAPA_SENTIMENTOS = {
    "positive": "Positivo",
    "neutral": "Neutro",
    "negative": "Alerta",
}

# Variáveis que guardam o estado do modelo enquanto a API está rodando
classificador = None
erro_carregamento = None


def carregar_modelo():
    """
    Carrega o modelo na memória (só na primeira vez).
    Na primeira execução o Transformers baixa o modelo (~1,1 GB) e guarda no computador.
    Nas próximas vezes ele já carrega direto do disco, sem internet.
    """
    global classificador, erro_carregamento

    if classificador is not None:
        return True

    try:
        print(f"Carregando o modelo '{NOME_MODELO}'...")
        classificador = pipeline("text-classification", model=NOME_MODELO)
        erro_carregamento = None
        print("Modelo carregado com sucesso!")
        return True
    except Exception as e:
        classificador = None
        erro_carregamento = str(e)
        print(f"Falha ao carregar o modelo: {e}")
        return False


def modelo_disponivel():
    """Diz se o modelo está pronto para uso."""
    return classificador is not None


def analisar_sentimento(texto):
    """
    Recebe um texto e devolve o sentimento (Positivo, Neutro ou Alerta),
    a confiança do modelo e o tempo que levou para processar.
    """
    if not modelo_disponivel():
        raise RuntimeError("O modelo de IA não está carregado.")

    inicio = time.time()
    resultado = classificador(texto, truncation=True)[0]  # truncation evita erro com textos muito longos
    tempo = time.time() - inicio

    rotulo = resultado["label"].lower()

    return {
        "sentimento": MAPA_SENTIMENTOS.get(rotulo, rotulo),
        "rotulo_original": rotulo,
        "confianca": round(float(resultado["score"]), 4),
        "tempo_processamento_seg": round(tempo, 3),
    }


# Teste rápido: rodar "python llm_service.py" no terminal
if __name__ == "__main__":
    if carregar_modelo():
        exemplos = [
            "Pará tem 61 cidades em situação de emergência por incêndios florestais",
            "Fundo Amazônia recebe novo desembolso para projetos de preservação",
            "Ministério divulga agenda de reuniões da semana",
        ]
        for frase in exemplos:
            print(f"\nTexto: {frase}")
            print(f"Resultado: {analisar_sentimento(frase)}")