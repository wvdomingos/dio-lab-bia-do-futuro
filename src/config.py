import os
from pathlib import Path
from dotenv import load_dotenv

# Carrega variáveis do arquivo .env
load_dotenv()

# Configurações de API
API_KEY = os.getenv("GOOGLE_API_KEY") # ou OPENAI_API_KEY

# Caminhos Absolutos (para evitar erro de FileNotFoundError)
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

# Arquivos de Dados
ARQUIVO_CLIENTE = DATA_DIR / "perfil_investidor.json"
ARQUIVO_PRODUTOS = DATA_DIR / "produtos_financeiros.json"

# Configurações do Modelo
MODEL_NAME = "gemini-3-flash-preview" # Modelo rápido e eficiente
TEMPERATURE = 0.7