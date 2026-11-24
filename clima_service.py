"""
Coleta de dados climáticos reais (TP5).

Busca temperatura, umidade e chuva diárias na API pública do Open-Meteo
(gratuita para uso não comercial, sem chave, dados sob licença CC BY 4.0).
Cada busca que dá certo é salva em data/clima.csv. Assim o dashboard
continua funcionando com os últimos dados mesmo se a internet cair.
"""

import os

import pandas as pd
import requests

URL_OPEN_METEO = "https://api.open-meteo.com/v1/forecast"
CAMINHO_CSV = os.path.join("data", "clima.csv")

# As mesmas cidades que eu usava nos dados simulados, agora com latitude e longitude
CIDADES = {
    "São Paulo": (-23.55, -46.63),
    "Rio de Janeiro": (-22.91, -43.17),
    "Curitiba": (-25.43, -49.27),
}

# Nome da variável no Open-Meteo -> nome da coluna no projeto
VARIAVEIS = {
    "temperature_2m_mean": "Temperatura",
    "temperature_2m_max": "Temp_Maxima",
    "relative_humidity_2m_mean": "Umidade",
    "precipitation_sum": "Chuva_mm",
}

# Limites que defini como referência para marcar um dia como alerta
LIMITE_CALOR = 32.0  # temperatura máxima do dia, em °C
LIMITE_CHUVA = 50.0  # chuva acumulada no dia, em mm


def buscar_cidade(nome, latitude, longitude, dias):
    """Pede ao Open-Meteo os dados diários de uma cidade e devolve uma tabela."""
    parametros = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": ",".join(VARIAVEIS.keys()),
        "past_days": dias,  # dias anteriores a hoje
        "forecast_days": 1,  # inclui o dia de hoje
        "timezone": "America/Sao_Paulo",
    }
    resposta = requests.get(URL_OPEN_METEO, params=parametros, timeout=20)
    resposta.raise_for_status()  # se a API devolver erro, para aqui
    diario = resposta.json()["daily"]

    df = pd.DataFrame(diario).rename(columns={"time": "Data", **VARIAVEIS})
    df["Data"] = pd.to_datetime(df["Data"])
    df["Cidade"] = nome
    return df


def coletar_clima(dias=14):
    """Busca todas as cidades, junta numa tabela só e salva em data/clima.csv."""
    tabelas = [buscar_cidade(nome, lat, lon, dias) for nome, (lat, lon) in CIDADES.items()]
    df = pd.concat(tabelas, ignore_index=True)
    df = df[["Data", "Cidade", "Temperatura", "Temp_Maxima", "Umidade", "Chuva_mm"]].round(1)

    os.makedirs("data", exist_ok=True)
    df.to_csv(CAMINHO_CSV, index=False, encoding="utf-8")
    return df


def carregar_clima(dias=14):
    """
    Tenta buscar os dados atualizados. Se não conseguir (sem internet ou API fora do ar),
    usa o último CSV salvo. Devolve a tabela e um texto dizendo de onde os dados vieram.
    """
    try:
        return coletar_clima(dias), "Open-Meteo (atualizado agora)"
    except Exception as erro:
        if os.path.exists(CAMINHO_CSV):
            df = pd.read_csv(CAMINHO_CSV, parse_dates=["Data"])
            return df, f"último arquivo salvo, porque a API falhou ({erro})"
        raise


def identificar_alertas(df):
    """Separa os dias em que alguma cidade passou dos limites de calor ou de chuva."""
    alertas = []
    for _, linha in df.iterrows():
        if linha["Temp_Maxima"] >= LIMITE_CALOR:
            alertas.append([linha["Data"], linha["Cidade"], "Calor forte", f"{linha['Temp_Maxima']:.1f} °C"])
        if linha["Chuva_mm"] >= LIMITE_CHUVA:
            alertas.append([linha["Data"], linha["Cidade"], "Chuva forte", f"{linha['Chuva_mm']:.1f} mm"])
    return pd.DataFrame(alertas, columns=["Data", "Cidade", "Tipo", "Valor"])


# Teste rápido: rodar "python clima_service.py" no terminal
if __name__ == "__main__":
    dados = coletar_clima(14)
    print(dados.head(10))
    print(f"\nTotal de linhas: {len(dados)} (salvo em {CAMINHO_CSV})")
    print(f"\nAlertas encontrados:\n{identificar_alertas(dados)}")