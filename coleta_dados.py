import os
import time
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Fontes abertas de notícias ambientais (portais públicos)
FONTES = {
    "Agência Brasil - Meio Ambiente": "https://agenciabrasil.ebc.com.br/meio-ambiente",
    "Ministério do Meio Ambiente - Notícias": "https://www.gov.br/mma/pt-br/noticias",
}

# Quantidade máxima de notícias por fonte, para a coleta continuar rápida
LIMITE_POR_FONTE = 10

# Textos que aparecem na página mas não são notícias (menus, avisos etc.)
TERMOS_IGNORADOS = [
    "pular para",
    "conteúdo principal",
    "menu",
    "busca",
    "cookie",
    "agência brasil",
    "acesso à informação",
    "mapa do site",
    "agenda pública",  # agenda do ministro não é notícia
]


def criar_navegador():
    """Configura o Chrome em modo invisível (headless) e devolve o navegador pronto."""
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Roda sem abrir a janela do Chrome
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("user-agent=ProjetoAcademicoODS13/3.0")

    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)


def baixar_html(driver, url):
    """Usa o Selenium para abrir a página e devolve o HTML completo já carregado."""
    driver.get(url)
    time.sleep(3)  # Aguarda o carregamento completo do DOM
    return driver.page_source


def extrair_noticias(html, nome_fonte):
    """Usa o BeautifulSoup para ler o HTML e separar os títulos das notícias."""
    soup = BeautifulSoup(html, "html.parser")

    noticias = []
    titulos_vistos = set()

    # Os títulos das notícias costumam ficar dentro das tags h2 e h3
    for tag in soup.find_all(["h2", "h3"]):
        texto = tag.get_text(strip=True)

        # Filtro de relevância: tamanho de manchete, sem repetição e sem textos de menu
        if not texto or not (30 <= len(texto) <= 180) or texto in titulos_vistos:
            continue
        if any(termo in texto.lower() for termo in TERMOS_IGNORADOS):
            continue

        titulos_vistos.add(texto)
        noticias.append(
            {
                "Titulo": texto,
                "Tamanho_Titulo": len(texto),
                "Qtd_Palavras": len(texto.split()),
                "Fonte": nome_fonte,
            }
        )

        if len(noticias) >= LIMITE_POR_FONTE:
            break

    return noticias


def salvar_csv(noticias):
    """Salva as notícias coletadas em data/noticias.csv."""
    os.makedirs("data", exist_ok=True)
    caminho_csv = os.path.join("data", "noticias.csv")
    pd.DataFrame(noticias).to_csv(caminho_csv, index=False, encoding="utf-8")
    return caminho_csv


if __name__ == "__main__":
    print("Iniciando a coleta de dados (Selenium + BeautifulSoup)...")

    todas_noticias = []
    driver = None

    try:
        driver = criar_navegador()

        for nome_fonte, url in FONTES.items():
            print(f"\nColetando: {nome_fonte}")
            try:
                html = baixar_html(driver, url)
                noticias = extrair_noticias(html, nome_fonte)
                todas_noticias.extend(noticias)
                print(f"  -> {len(noticias)} notícias encontradas.")
            except Exception as e:
                # Se uma fonte falhar, as outras continuam sendo coletadas
                print(f"  -> Erro ao coletar essa fonte: {e}")

        if todas_noticias:
            caminho = salvar_csv(todas_noticias)
            print(f"\nSucesso! {len(todas_noticias)} notícias salvas em '{caminho}'.")
        else:
            print("\nNenhuma notícia válida foi encontrada nas fontes.")

    except Exception as e:
        print(f"Erro ao iniciar o navegador: {e}")

    finally:
        if driver:
            driver.quit()  # Encerra a instância do navegador