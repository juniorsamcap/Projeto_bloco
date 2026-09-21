import os
import pandas as pd
import requests
from bs4 import BeautifulSoup

# URL pública de Notícias do Meio Ambiente
URL = "https://agenciabrasil.ebc.com.br/meio-ambiente"

print("Iniciando a extração de dados da web...")

try:
    headers = {
        "User-Agent": "ProjetoAcademicoODS13/1.0 (Estudo Academico)"
    }
    
    resposta = requests.get(URL, headers=headers, timeout=10)
    
    if resposta.status_code == 200:
        soup = BeautifulSoup(resposta.content, "html.parser")
        
        # Procura por links/títulos da página
        elementos = soup.find_all(["h2", "h3", "a"])
        
        noticias = []
        
        for item in elementos:
            texto = item.get_text(strip=True)
            
            # Filtro simples: texto com tamanho de notícia e que não seja botão de acessibilidade/menu
            if texto and 30 <= len(texto) <= 150:
                if not any(termo in texto.lower() for termo in ["pular para", "conteúdo principal", "menu", "busca", "cookie"]):
                    noticias.append({
                        "Titulo": texto,
                        "Tamanho_Titulo": len(texto),
                        "Qtd_Palavras": len(texto.split())
                    })
                    break  # Pega exatamente 1 notícia válida e encerra (foco didático)
        
        df_noticias = pd.DataFrame(noticias)
        
        os.makedirs("data", exist_ok=True)
        caminho_csv = os.path.join("data", "noticias.csv")
        df_noticias.to_csv(caminho_csv, index=False, encoding="utf-8")
        
        print(f"Sucesso! {len(df_noticias)} notícia real salva em '{caminho_csv}'.")
    else:
        print(f"Acesso indisponível. Código HTTP: {resposta.status_code}")

except Exception as e:
    print(f"Erro na coleta de dados: {e}")