import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

URL = "https://agenciabrasil.ebc.com.br/meio-ambiente"

print("Iniciando a extração de dados com Selenium...")

# Configuração do navegador invisível (Headless)
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Roda sem abrir a janela do Chrome
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("user-agent=ProjetoAcademicoODS13/2.0")

driver = None
try:
    # Inicializa o robô do Chrome
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    driver.get(URL)
    time.sleep(3)  # Aguarda o carregamento completo do DOM

    # Coleta todos os títulos/links de notícias
    elementos = driver.find_elements(By.XPATH, "//h2 | //h3 | //a")

    noticias = []
    titulos_vistos = set()

    for item in elementos:
        texto = item.text.strip()

        # Filtro de relevância para notícias
        if texto and 30 <= len(texto) <= 180 and texto not in titulos_vistos:
            if not any(
                termo in texto.lower()
                for termo in [
                    "pular para",
                    "conteúdo principal",
                    "menu",
                    "busca",
                    "cookie",
                    "agência brasil",
                ]
            ):
                titulos_vistos.add(texto)
                noticias.append(
                    {
                        "Titulo": texto,
                        "Tamanho_Titulo": len(texto),
                        "Qtd_Palavras": len(texto.split()),
                        "Fonte": "Agência Brasil - Meio Ambiente",
                    }
                )

                # Limita a 10 notícias para manter a coleta rápida e simples
                if len(noticias) >= 10:
                    break

    # Salva os dados no CSV
    if noticias:
        df_noticias = pd.DataFrame(noticias)
        os.makedirs("data", exist_ok=True)
        caminho_csv = os.path.join("data", "noticias.csv")
        df_noticias.to_csv(caminho_csv, index=False, encoding="utf-8")

        print(
            f"Sucesso! {len(df_noticias)} notícias raspadas com Selenium e salvas em '{caminho_csv}'."
        )
    else:
        print("Nenhuma notícia válida foi encontrada na página.")

except Exception as e:
    print(f"Erro na coleta de dados com Selenium: {e}")

finally:
    if driver:
        driver.quit()  # Encerra a instância do navegador