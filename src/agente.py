import json
import requests
import pandas as pd
from config import (
    OLLAMA_URL, MODEL_NAME,
    TRANSACOES_PATH, HISTORICO_PATH, PRODUTOS_PATH, PERFIL_PATH,
)


# ─────────────────────────────────────────
# Carregamento da base de conhecimento
# ─────────────────────────────────────────

def carregar_dados():
    transacoes = pd.read_csv(TRANSACOES_PATH)
    historico  = pd.read_csv(HISTORICO_PATH)
    produtos   = json.load(open(PRODUTOS_PATH, encoding="utf-8"))
    perfil     = json.load(open(PERFIL_PATH,   encoding="utf-8"))
    return transacoes, historico, produtos, perfil


def formatar_transacoes(df):
    linhas = []
    for _, r in df.iterrows():
        sinal = "+" if r["tipo"] == "entrada" else "-"
        linhas.append(
            f"  {r['data']}: {r['descricao']:<22} {sinal}R$ {r['valor']:>8.2f}  ({r['categoria']})"
        )
    return "\n".join(linhas)


def formatar_historico(df):
    linhas = []
    for _, r in df.iterrows():
        linhas.append(f"  {r['data']} [{r['canal']}] {r['tema']}: {r['resumo']}")
    return "\n".join(linhas)


def formatar_produtos(produtos, aceita_risco):
    mapa = {"baixo": "✓", "medio": "~", "alto": "✗"}
    linhas = []
    for p in produtos:
        obs = " ← NÃO recomendado" if p["risco"] == "alto" and not aceita_risco else ""
        linhas.append(
            f"  {mapa.get(p['risco'],'?')} {p['nome']:<22} | risco: {p['risco']:<6} | "
            f"{p['rentabilidade']:<14} | mín R$ {p['aporte_minimo']:.0f}{obs}"
        )
    return "\n".join(linhas)


def formatar_metas(metas):
    return "\n".join(
        f"  {i}. {m['meta']}: R$ {m['valor_necessario']:,.0f} até {m['prazo']}"
        for i, m in enumerate(metas, 1)
    )


def montar_system_prompt(transacoes, historico, produtos, perfil):
    return f"""Você é Julia, assistente financeira virtual de uma fintech brasileira.
Seu objetivo é educar jovens sobre finanças pessoais de forma clara,
acolhedora e sem julgamentos, usando os dados reais do cliente.

PERSONA:
- Tom informal, acolhedor, direto. Como uma amiga que entende de finanças.
- Nunca use jargões sem explicar. Frases curtas. Parágrafos pequenos.
- Responda SEMPRE em português brasileiro.

CONTEXTO DO CLIENTE:
  Nome: {perfil['nome']} | Idade: {perfil['idade']} anos | Profissão: {perfil['profissao']}
  Renda: R$ {perfil['renda_mensal']:,.0f} | Perfil: {perfil['perfil_investidor'].capitalize()}
  Aceita risco: {'Sim' if perfil['aceita_risco'] else 'Não'} | Patrimônio: R$ {perfil['patrimonio_total']:,.0f}

METAS:
{formatar_metas(perfil['metas'])}

TRANSAÇÕES RECENTES:
{formatar_transacoes(transacoes)}

HISTÓRICO DE ATENDIMENTOS:
{formatar_historico(historico)}

PRODUTOS DISPONÍVEIS:
{formatar_produtos(produtos, perfil['aceita_risco'])}

REGRAS:
1. Baseie respostas apenas nos dados acima. Nunca invente informações.
2. Se não souber, admita e ofereça uma alternativa.
3. Nunca sugira produtos de risco alto para este cliente.
4. Nunca peça senha, CPF ou dados sensíveis.
5. Não execute operações — direcione ao app ou atendimento humano.
6. Conecte respostas às metas do cliente quando relevante.
"""


# ─────────────────────────────────────────
# Chamada ao Ollama (local, sem API key)
# ─────────────────────────────────────────

def enviar_mensagem(system_prompt: str, historico_chat: list[dict]) -> str:
    """
    Chama o Ollama localmente via HTTP.
    historico_chat: lista de {"role": "user"|"assistant", "content": str}
    """
    mensagens = [{"role": "system", "content": system_prompt}] + historico_chat

    try:
        resposta = requests.post(
            OLLAMA_URL,
            json={"model": MODEL_NAME, "messages": mensagens, "stream": False},
            timeout=120,
        )
        resposta.raise_for_status()
        return resposta.json()["message"]["content"]

    except requests.exceptions.ConnectionError:
        return (
            "⚠️ Não consegui conectar ao Ollama. Verifique se ele está rodando "
            "com o comando `ollama serve` no terminal."
        )
    except Exception as e:
        return f"⚠️ Erro inesperado: {e}"