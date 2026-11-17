"""
Avaliação dos modelos candidatos (TP4).

Roda cada modelo da HuggingFace sobre as manchetes reais coletadas em data/noticias.csv
e salva o resultado lado a lado em data/avaliacao_modelos.csv.
Assim a escolha do modelo é feita com base nos nossos próprios dados, e não só na teoria.

Os modelos são carregados um de cada vez e liberados da memória logo depois,
porque a máquina tem só 8 GB de RAM.
"""

import gc
import os
import time
import pandas as pd
from transformers import pipeline

CAMINHO_NOTICIAS = os.path.join("data", "noticias.csv")
CAMINHO_SAIDA = os.path.join("data", "avaliacao_modelos.csv")

# Tradução dos rótulos para as categorias do projeto
MAPA_SENTIMENTOS = {"positive": "Positivo", "neutral": "Neutro", "negative": "Alerta"}

# Rótulos usados no modelo zero-shot (ele "escolhe" qual frase combina mais com a notícia)
ROTULOS_ZERO_SHOT = {
    "um problema ou risco ambiental": "Alerta",
    "uma conquista ou avanço ambiental": "Positivo",
    "uma informação neutra": "Neutro",
}


def avaliar_sentimento(nome_modelo, titulos):
    """Modelos de sentimento: devolvem positive, neutral ou negative."""
    classificador = pipeline("text-classification", model=nome_modelo)
    resultados = []
    inicio = time.time()
    for titulo in titulos:
        r = classificador(titulo, truncation=True)[0]
        rotulo = r["label"].lower()
        resultados.append(f"{MAPA_SENTIMENTOS.get(rotulo, rotulo)} ({r['score']:.0%})")
    tempo_medio = (time.time() - inicio) / len(titulos)
    del classificador
    gc.collect()
    return resultados, tempo_medio


def avaliar_zero_shot(nome_modelo, titulos):
    """Modelo zero-shot: compara a notícia com as frases que eu defini em ROTULOS_ZERO_SHOT."""
    classificador = pipeline("zero-shot-classification", model=nome_modelo)
    resultados = []
    inicio = time.time()
    for titulo in titulos:
        r = classificador(
            titulo,
            candidate_labels=list(ROTULOS_ZERO_SHOT.keys()),
            hypothesis_template="Esta notícia trata de {}.",
        )
        melhor = r["labels"][0]
        resultados.append(f"{ROTULOS_ZERO_SHOT[melhor]} ({r['scores'][0]:.0%})")
    tempo_medio = (time.time() - inicio) / len(titulos)
    del classificador
    gc.collect()
    return resultados, tempo_medio


if __name__ == "__main__":
    titulos = pd.read_csv(CAMINHO_NOTICIAS)["Titulo"].tolist()
    tabela = pd.DataFrame({"Titulo": titulos})

    candidatos = [
        ("DistilBERT (sentimento)", "lxyuan/distilbert-base-multilingual-cased-sentiments-student", avaliar_sentimento),
        ("XLM-RoBERTa (sentimento)", "cardiffnlp/twitter-xlm-roberta-base-sentiment", avaliar_sentimento),
        ("mDeBERTa (zero-shot)", "MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7", avaliar_zero_shot),
    ]

    for apelido, nome_modelo, funcao in candidatos:
        print(f"\nAvaliando {apelido}... (na primeira vez o modelo é baixado)")
        resultados, tempo_medio = funcao(nome_modelo, titulos)
        tabela[apelido] = resultados
        print(f"  -> tempo médio por notícia: {tempo_medio:.3f} s")

    tabela.to_csv(CAMINHO_SAIDA, index=False, encoding="utf-8")
    print(f"\nAvaliação salva em '{CAMINHO_SAIDA}'.")