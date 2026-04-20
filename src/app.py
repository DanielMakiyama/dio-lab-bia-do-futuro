import streamlit as st
from agente import carregar_dados, montar_system_prompt, enviar_mensagem

st.set_page_config(
    page_title="Julia — Assistente Financeira",
    page_icon="💜",
    layout="centered",
)

st.markdown("""
<style>
.julia-header {
    display: flex; align-items: center; gap: 14px;
    padding: 18px 20px;
    background: linear-gradient(135deg, #6C48C5 0%, #9B72E8 100%);
    border-radius: 14px; margin-bottom: 8px;
}
.julia-avatar {
    width: 52px; height: 52px;
    background: rgba(255,255,255,0.2); border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 26px;
}
.julia-title { color: white; margin: 0; font-size: 1.3rem; font-weight: 700; }
.julia-sub   { color: rgba(255,255,255,0.82); font-size: 0.85rem; margin: 2px 0 0; }
.card {
    background: #f8f6ff; border: 1px solid #e2d9f3;
    border-radius: 10px; padding: 12px 16px;
    margin-bottom: 8px; font-size: 0.88rem;
}
.card-title { font-weight: 700; color: #6C48C5; margin-bottom: 4px; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────
# Inicialização
# ─────────────────────────────────────────
@st.cache_resource
def inicializar():
    transacoes, historico, produtos, perfil = carregar_dados()
    system_prompt = montar_system_prompt(transacoes, historico, produtos, perfil)
    return system_prompt, perfil, transacoes, produtos

if "historico_chat" not in st.session_state:
    st.session_state.historico_chat = []

system_prompt, perfil, transacoes, produtos = inicializar()


# ─────────────────────────────────────────
# Cabeçalho
# ─────────────────────────────────────────
st.markdown("""
<div class="julia-header">
  <div class="julia-avatar">💜</div>
  <div>
    <p class="julia-title">Julia</p>
    <p class="julia-sub">Assistente Financeira · Rodando localmente com Ollama</p>
  </div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────
with st.sidebar:
    st.markdown("### 👤 Perfil do cliente")

    total_saidas   = transacoes[transacoes["tipo"] == "saida"]["valor"].sum()
    total_entradas = transacoes[transacoes["tipo"] == "entrada"]["valor"].sum()
    saldo_mes      = total_entradas - total_saidas

    meta_reserva = next(
        m for m in perfil["metas"] if "reserva" in m["meta"].lower()
    )
    progresso = perfil["reserva_emergencia_atual"] / meta_reserva["valor_necessario"]

    st.markdown(f"""
    <div class="card">
      <div class="card-title">📋 Dados gerais</div>
      <b>{perfil['nome']}</b> · {perfil['idade']} anos<br>
      Renda: <b>R$ {perfil['renda_mensal']:,.0f}</b><br>
      Perfil: <b>{perfil['perfil_investidor'].capitalize()}</b>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("**🎯 Reserva de emergência**")
    st.progress(progresso, text=f"R$ {perfil['reserva_emergencia_atual']:,.0f} / R$ {meta_reserva['valor_necessario']:,.0f}")

    st.markdown(f"""
    <div class="card" style="margin-top:8px">
      <div class="card-title">💰 Resumo outubro/2025</div>
      Entradas: <b>R$ {total_entradas:,.2f}</b><br>
      Saídas: <b>R$ {total_saidas:,.2f}</b><br>
      Saldo: <b style="color:#6C48C5">R$ {saldo_mes:,.2f}</b>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("**📦 Produtos disponíveis**")
    risco_cor = {"baixo": "🟢", "medio": "🟡", "alto": "🔴"}
    for p in produtos:
        st.markdown(f"{risco_cor.get(p['risco'], '⚪')} **{p['nome']}** — {p['rentabilidade']}")

    st.divider()
    st.caption("🖥️ Modelo local: `llama3.2` via Ollama")
    if st.button("🗑️ Limpar conversa", use_container_width=True):
        st.session_state.historico_chat = []
        st.rerun()


# ─────────────────────────────────────────
# Boas-vindas
# ─────────────────────────────────────────
if not st.session_state.historico_chat:
    with st.chat_message("assistant", avatar="💜"):
        st.markdown(
            f"Oi, **{perfil['nome'].split()[0]}**! 👋 Sou a Julia, sua assistente financeira.\n\n"
            "Pode me perguntar qualquer coisa sobre seus gastos, produtos financeiros "
            "ou suas metas — sem julgamento! 😊"
        )

    st.markdown("**💡 Perguntas frequentes:**")
    sugestoes = [
        "Como tá minha reserva de emergência?",
        "O que é CDI?",
        "Tô gastando muito esse mês?",
        "Qual a diferença entre CDB e Tesouro Selic?",
        "Posso pagar só o mínimo do cartão?",
    ]
    cols = st.columns(2)
    for i, s in enumerate(sugestoes):
        if cols[i % 2].button(s, key=f"sugestao_{i}", use_container_width=True):
            st.session_state.historico_chat.append({"role": "user", "content": s})
            st.rerun()


# ─────────────────────────────────────────
# Histórico
# ─────────────────────────────────────────
for msg in st.session_state.historico_chat:
    avatar = "💜" if msg["role"] == "assistant" else "🧑"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])


# ─────────────────────────────────────────
# Input
# ─────────────────────────────────────────
if prompt := st.chat_input("Digite sua pergunta para a Julia..."):
    st.session_state.historico_chat.append({"role": "user", "content": prompt})

    with st.chat_message("user", avatar="🧑"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="💜"):
        with st.spinner("Julia está pensando... (pode levar alguns segundos)"):
            resposta = enviar_mensagem(system_prompt, st.session_state.historico_chat)
            st.markdown(resposta)
            st.session_state.historico_chat.append(
                {"role": "assistant", "content": resposta}
            )