import os

# Ollama roda localmente — sem necessidade de API key
OLLAMA_URL  = "http://localhost:11434/api/chat"
MODEL_NAME  = "llama3.2"  

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
TRANSACOES_PATH = os.path.join(DATA_DIR, "transacoes.csv")
HISTORICO_PATH  = os.path.join(DATA_DIR, "historico_atendimento.csv")
PRODUTOS_PATH   = os.path.join(DATA_DIR, "produtos_financeiros.json")
PERFIL_PATH     = os.path.join(DATA_DIR, "perfil_investidor.json")