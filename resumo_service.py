"""
Serviço de resumo com IA generativa (TP5).

Carrega um modelo de linguagem pequeno da HuggingFace que roda na CPU
e gera um resumo com insights a partir dos dados do projeto:
clima real (Open-Meteo) + notícias já classificadas pelo modelo de sentimento.
Aqui também fica a montagem do prompt (engenharia de prompt).
"""

import os
import time

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

# Qwen2.5 0.5B Instruct: gratuito (licença Apache 2.0), ~1 GB, entende português e roda só na CPU
NOME_MODELO_RESUMO = os.getenv("MODELO_RESUMO", "Qwen/Qwen2.5-0.5B-Instruct")

# Limite de tamanho da resposta. No primeiro teste, com 300, o resumo levou quase 90 s na CPU
MAX_TOKENS_RESPOSTA = 220

tokenizer = None
modelo = None
erro_carregamento = None

# Papel e regras fixas do modelo (parte "sistema" do prompt)
PROMPT_SISTEMA = (
    "Você é um analista de clima e sustentabilidade que apoia gestores públicos, ONGs e voluntários "
    "no acompanhamento do ODS 13 (Ação Contra a Mudança Global do Clima). "
    "Use somente os dados fornecidos e não invente números nem fatos. "
    "Responda em português do Brasil, de forma curta e direta."
)

# No primeiro teste, com instruções abertas, o modelo escreveu tópicos genéricos sem usar os dados.
# Por isso cada foco agora traz um modelo de resposta com lacunas <...> para o modelo preencher.
INSTRUCOES_FOCO = {
    "geral": (
        "Escreva exatamente neste formato, trocando cada <...> por informações dos dados:\n"
        "CLIMA\n"
        "- São Paulo: <uma frase com a temperatura máxima e a chuva acumulada>\n"
        "- Rio de Janeiro: <uma frase com a temperatura máxima e a chuva acumulada>\n"
        "- Curitiba: <uma frase com a temperatura máxima e a chuva acumulada>\n"
        "NOTÍCIAS\n"
        "- <assunto das notícias marcadas como [Alerta]>\n"
        "- <outro assunto importante das notícias>\n"
        "RECOMENDAÇÕES\n"
        "1. <ação prática ligada ao ODS 13 baseada nos dados>\n"
        "2. <outra ação prática ligada ao ODS 13>"
    ),
    "alertas": (
        "Escreva exatamente neste formato, trocando cada <...> por informações dos dados:\n"
        "RISCOS CLIMÁTICOS\n"
        "- <data, cidade e valor de cada dia de alerta>\n"
        "NOTÍCIAS EM ALERTA\n"
        "- <cada notícia marcada como [Alerta], resumida em poucas palavras>\n"
        "AÇÕES PREVENTIVAS\n"
        "1. <ação para gestores locais>\n"
        "2. <ação para gestores locais>\n"
        "3. <ação para gestores locais>"
    ),
    "noticias": (
        "Escreva exatamente neste formato, trocando cada <...> por informações dos dados:\n"
        "PRINCIPAIS TEMAS\n"
        "- <tema 1 das notícias>\n"
        "- <tema 2 das notícias>\n"
        "- <tema 3 das notícias>\n"
        "PEDEM MAIS ATENÇÃO\n"
        "- <notícia marcada como [Alerta] e o motivo>"
    ),
}


def carregar_modelo():
    """Carrega o modelo de resumo na memória (na primeira vez ele é baixado, ~1 GB)."""
    global tokenizer, modelo, erro_carregamento

    if modelo is not None:
        return True

    try:
        print(f"Carregando o modelo de resumo '{NOME_MODELO_RESUMO}'...")
        tokenizer = AutoTokenizer.from_pretrained(NOME_MODELO_RESUMO)
        modelo = AutoModelForCausalLM.from_pretrained(NOME_MODELO_RESUMO, dtype=torch.float32)
        modelo.eval()
        erro_carregamento = None
        print("Modelo de resumo carregado com sucesso!")
        return True
    except Exception as e:
        tokenizer, modelo = None, None
        erro_carregamento = str(e)
        print(f"Falha ao carregar o modelo de resumo: {e}")
        return False


def modelo_disponivel():
    return modelo is not None


def montar_prompt(foco, df_clima, df_alertas, df_noticias):
    """
    Junta os dados do projeto num texto organizado para o modelo.
    df_noticias precisa ter as colunas Titulo, Fonte e Sentimento.
    """
    # Bloco 1: clima resumido por cidade
    linhas_clima = []
    for cidade, grupo in df_clima.groupby("Cidade"):
        linhas_clima.append(
            f"- {cidade}: temperatura média {grupo['Temperatura'].mean():.1f} °C, "
            f"máxima {grupo['Temp_Maxima'].max():.1f} °C, umidade média {grupo['Umidade'].mean():.0f}%, "
            f"chuva acumulada {grupo['Chuva_mm'].sum():.1f} mm"
        )

    # Bloco 2: dias que passaram dos limites de alerta
    if df_alertas.empty:
        linhas_alertas = ["- Nenhum dia passou dos limites de alerta."]
    else:
        linhas_alertas = [
            f"- {linha['Data']:%d/%m}: {linha['Cidade']}, {linha['Tipo']} ({linha['Valor']})"
            for _, linha in df_alertas.iterrows()
        ]

    # Bloco 3: notícias com o sentimento dado pelo outro modelo
    linhas_noticias = [
        f"- [{linha['Sentimento']}] {linha['Titulo']} ({linha['Fonte']})"
        for _, linha in df_noticias.head(20).iterrows()
    ]

    periodo = f"{df_clima['Data'].min():%d/%m/%Y} a {df_clima['Data'].max():%d/%m/%Y}"

    # Os dados vêm primeiro e a tarefa por último, para o formato pedido ser a última coisa que o modelo lê
    return (
        f"DADOS CLIMÁTICOS REAIS ({periodo}, fonte Open-Meteo):\n" + "\n".join(linhas_clima) + "\n\n"
        "DIAS DE ALERTA (calor a partir de 32 °C ou chuva a partir de 50 mm):\n" + "\n".join(linhas_alertas) + "\n\n"
        "NOTÍCIAS AMBIENTAIS COLETADAS (com o sentimento classificado):\n" + "\n".join(linhas_noticias) + "\n\n"
        f"TAREFA:\n{INSTRUCOES_FOCO[foco]}"
    )


def gerar_resumo(prompt_usuario):
    """Manda o prompt para o modelo e devolve o texto gerado e o tempo gasto."""
    if not modelo_disponivel():
        raise RuntimeError("O modelo de resumo não está carregado.")

    mensagens = [
        {"role": "system", "content": PROMPT_SISTEMA},
        {"role": "user", "content": prompt_usuario},
    ]
    # O próprio tokenizer monta o texto no formato de conversa que o modelo foi treinado para entender
    texto = tokenizer.apply_chat_template(mensagens, tokenize=False, add_generation_prompt=True)
    entradas = tokenizer(texto, return_tensors="pt")

    inicio = time.time()
    with torch.no_grad():
        saida = modelo.generate(
            **entradas,
            max_new_tokens=MAX_TOKENS_RESPOSTA,
            do_sample=False,  # sem sorteio: o mesmo prompt gera sempre o mesmo resumo (bom para testar)
            repetition_penalty=1.1,  # evita o modelo repetir frases
        )
    tempo = time.time() - inicio

    # A saída vem com o prompt junto; pego só a parte nova que o modelo escreveu
    novos_tokens = saida[0][entradas["input_ids"].shape[1]:]
    resumo = tokenizer.decode(novos_tokens, skip_special_tokens=True).strip()
    return resumo, round(tempo, 2)