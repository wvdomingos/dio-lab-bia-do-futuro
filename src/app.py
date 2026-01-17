import streamlit as st
from agente import EloAgent

# Configuração da Página
st.set_page_config(page_title="Elo - Assistente Financeiro", page_icon="🏦")

# Inicialização (Cache do Agente para não recarregar a cada interação)
@st.cache_resource
def get_agent():
    return EloAgent()

agent = get_agent()

# Sidebar com Contexto (Simulação de Logado)
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4712/4712009.png", width=100)
    st.title(f"Olá, {agent.dados_cliente.get('nome', 'Visitante')}!")
    
    # Busca segura pelas novas chaves
    perfil = agent.dados_cliente.get('perfil_investidor', 'Não definido')
    patrimonio = agent.dados_cliente.get('patrimonio_total', 0.0)
    
    st.markdown(f"**Perfil:** {perfil}")
    st.markdown(f"**Patrimônio:** R$ {patrimonio:,.2f}")
    st.divider()
    st.info("💡 Dica: Pergunte 'Quanto rende 1000 reais?'")

# Inicializa histórico de chat
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Mensagem inicial do Elo
    boas_vindas = "Olá! Sou o Elo, seu assistente financeiro. Como posso ajudar com seus investimentos hoje?"
    st.session_state.messages.append({"role": "assistant", "content": boas_vindas})

# Exibe mensagens anteriores
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input do Usuário
if prompt := st.chat_input("Digite sua dúvida financeira..."):
    # 1. Exibe msg do usuário
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 2. Processa resposta (Lógica do Agente)
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("Calculando...") # Feedback visual
        
        # Passa o histórico simplificado (apenas texto)
        historico_texto = [f"{m['role']}: {m['content']}" for m in st.session_state.messages]
        
        resposta_completa = agent.gerar_resposta(prompt, historico_texto)
        
        message_placeholder.markdown(resposta_completa)
    
    st.session_state.messages.append({"role": "assistant", "content": resposta_completa})