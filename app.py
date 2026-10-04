import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import statsmodels.api as sm
import json
import time
import os
import datetime

# Configuração Mobile-First
st.set_page_config(page_title="Oráculo 2026 | A Mãe de Todas as Pesquisas", layout="centered", page_icon="🔥")

# ==========================================
# FUNÇÕES DE NEGÓCIO (LEADS)
# ==========================================
def salvar_lead(nome, contato):
    arquivo_leads = "leads.csv"
    data_atual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    novo_dado = pd.DataFrame([[nome, contato, data_atual]], columns=["Nome", "Contato", "Data"])
    
    if not os.path.exists(arquivo_leads):
        novo_dado.to_csv(arquivo_leads, index=False)
    else:
        novo_dado.to_csv(arquivo_leads, mode='a', header=False, index=False)

# ==========================================
# CABEÇALHO BRANDING (VAGNER TUDISCO)
# ==========================================
st.markdown("""
    <div style='text-align: center; padding: 10px; background-color: #f0f2f6; border-radius: 10px; margin-bottom: 20px;'>
        <h4 style='margin:0; color: #1f2937;'>🚀 Desenvolvido por <strong>Vagner Tudisco</strong></h4>
        <p style='margin:0; font-size: 14px; color: #4b5563;'>Especialista em Dados & Inteligência Preditiva</p>
    </div>
""", unsafe_allow_html=True)

# 1. CARREGAMENTO DOS DADOS
@st.cache_data
def load_data():
    df = pd.read_csv("dados_pesquisas.csv")
    df['Data'] = pd.to_datetime(df['Data'])
    try:
        df_internet = pd.read_csv("dados_sentimento_internet.csv")
        df_internet['Data'] = pd.to_datetime(df_internet['Data'])
        df = pd.merge(df, df_internet, on='Data', how='left')
    except:
        pass
    df = df.sort_values(by='Data')
    return df

df_bruto = load_data()

# 2. MOTOR MATEMÁTICO CORE
def calculate_trend(df, candidate_col):
    df['Days'] = (df['Data'] - df['Data'].min()).dt.days
    lowess = sm.nonparametric.lowess
    smoothed = lowess(df[candidate_col], df['Days'], frac=0.6)
    return smoothed[:, 1]

# 3. SIDEBAR (BRANDING & MODO)
st.sidebar.markdown("### 👨‍💻 Vagner Tudisco")
st.sidebar.markdown("[👉 Siga no LinkedIn](https://www.linkedin.com/in/vagner-tudisco-6191a480/)")
st.sidebar.markdown("[📸 Siga no Instagram](https://instagram.com/vagnertudisco.oficial)")
st.sidebar.markdown("---")

st.sidebar.title("⚙️ Modo de Operação")
st.sidebar.markdown("Use essa chave na Véspera e no Dia da Eleição.")
modo_app = st.sidebar.radio(
    "Escolha o Motor do Painel:",
    ["🔮 Predição (Pesquisas/Internet)", "🔴 Apuração Oficial (TSE)"]
)

if modo_app == "🔴 Apuração Oficial (TSE)":
    # MÓDULO 1: APURAÇÃO AO VIVO TSE
    st.title("🔴 TSE: Apuração ao Vivo")
    st.markdown("Conectado à base oficial de totalização de votos.")
    
    col_btn, col_auto = st.columns([1, 1])
    with col_btn:
        if st.button("🔄 Atualizar Manualmente"):
            st.toast("Buscando pacote de dados no servidor do TSE...")
            time.sleep(0.5)
    with col_auto:
        auto_update = st.toggle("⏱️ Atualização Automática (A cada 30s)", value=False, help="Liga o robô que aperta F5 para você.")
        
    if auto_update:
        import streamlit.components.v1 as components
        components.html(
            "<script>setTimeout(function(){ window.parent.location.reload(); }, 30000);</script>",
            height=0
        )
        
    try:
        with open("tse_apuracao_mock.json", "r", encoding='utf-8') as f:
            dados_tse = json.load(f)
            
        urnas_apuradas = float(dados_tse.get("pst", 0))
        data_hora = f"{dados_tse.get('dt', '')} às {dados_tse.get('ht', '')}"
        
        st.markdown(f"### 🗳️ Urnas Apuradas: **{urnas_apuradas}%**")
        st.caption(f"Última atualização do TSE: {data_hora}")
        
        st.progress(urnas_apuradas / 100.0)
        st.markdown("---")
        
        candidatos = dados_tse.get("cand", [])
        if len(candidatos) >= 2:
            cand1 = candidatos[0]
            cand2 = candidatos[1]
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"<h2 style='text-align: center; color: blue;'>{cand1['nm']}</h2>", unsafe_allow_html=True)
                st.markdown(f"<h1 style='text-align: center;'>{cand1['pvap']}%</h1>", unsafe_allow_html=True)
                st.markdown(f"<p style='text-align: center; color: gray;'>{int(cand1['vap']):,} votos</p>", unsafe_allow_html=True)
                
            with col2:
                st.markdown(f"<h2 style='text-align: center; color: red;'>{cand2['nm']}</h2>", unsafe_allow_html=True)
                st.markdown(f"<h1 style='text-align: center;'>{cand2['pvap']}%</h1>", unsafe_allow_html=True)
                st.markdown(f"<p style='text-align: center; color: gray;'>{int(cand2['vap']):,} votos</p>", unsafe_allow_html=True)
                
            st.markdown("---")
            st.markdown("#### Barra de Tração (Disputa)")
            fig_apuracao = go.Figure()
            fig_apuracao.add_trace(go.Bar(y=['Votos'], x=[float(cand1['pvap'])], name=cand1['nm'], orientation='h', marker=dict(color='blue')))
            fig_apuracao.add_trace(go.Bar(y=['Votos'], x=[float(cand2['pvap'])], name=cand2['nm'], orientation='h', marker=dict(color='red')))
            fig_apuracao.update_layout(barmode='stack', height=150, showlegend=False, margin=dict(l=0, r=0, t=0, b=0))
            fig_apuracao.update_xaxes(range=[0, 100], visible=False)
            fig_apuracao.update_yaxes(visible=False)
            st.plotly_chart(fig_apuracao, use_container_width=True)
            
    except Exception as e:
        st.error(f"Erro ao conectar com o TSE: {e}")

else:
    # MÓDULO 2: PREDIÇÃO GAMIFICADA
    st.title("🔥 Oráculo 2026: A Mãe de Todas as Pesquisas")
    st.markdown("O primeiro supercomputador que mistura as ruas com a internet para prever a urna antes da TV.")

    with st.expander("🧠 Como ler este Painel? (Entenda a Ciência)"):
        st.markdown("**1. Por que os números são diferentes da TV?**")
        st.write("Porque não confiamos apenas no 'Voto Frio' (pesquisas de rua). Nós misturamos a Rua com a velocidade da Internet (Voto Quente/Engajamento). É como prever o tempo: não olhamos só pro céu de hoje, mas para o radar das redes.")
        st.markdown("**2. Para que servem os botões deslizantes?**")
        st.write("Eles são uma 'Máquina do Futuro'. Simulam para onde os eleitores indecisos correriam caso uma bomba estoure (crise ou escândalo) na manhã da eleição.")
        st.markdown("**3. O que são Votos Válidos Projetados?**")
        st.write("É a simulação de como a tela final do TSE vai terminar. Ela já contabiliza o Efeito Voto Útil dos eleitores da terceira via migrando de última hora para os líderes.")

    st.markdown("---")
    st.markdown("### 🎮 Simulador Interativo")
    col_sim1, col_sim2 = st.columns(2)
    with col_sim1:
        sim_economia = st.slider("💰 Crise Econômica (Lula Perde)", min_value=0, max_value=10, value=0, format="-%d%%")
    with col_sim2:
        sim_escandalo = st.slider("📱 Pânico nas Redes (Flávio Perde)", min_value=0, max_value=10, value=0, format="-%d%%")

    df_analise = df_bruto.copy()
    df_analise = df_analise.groupby('Data').mean(numeric_only=True).reset_index()

    # Calculando a tendência para TODOS os candidatos
    candidatos = ['Lula', 'Flavio Bolsonaro', 'Augusto Cury', 'Ronaldo Caiado', 'Romeu Zema', 'Renan Santos']
    for col in candidatos:
        df_analise[f'Tendencia_{col}'] = calculate_trend(df_analise, col)
        
    # Aplicando a fórmula Mista apenas para os gigantes (que tem internet relevante)
    if 'Internet_Lula' in df_analise.columns:
        tendencia_net_lula = calculate_trend(df_analise, 'Internet_Lula')
        tendencia_net_flavio = calculate_trend(df_analise, 'Internet_Flavio Bolsonaro')
        df_analise['Base_Lula'] = (df_analise['Tendencia_Lula'] * 0.6) + (tendencia_net_lula * 0.4)
        df_analise['Base_Flavio'] = (df_analise['Tendencia_Flavio Bolsonaro'] * 0.6) + (tendencia_net_flavio * 0.4)
    else:
        df_analise['Base_Lula'] = df_analise['Tendencia_Lula']
        df_analise['Base_Flavio'] = df_analise['Tendencia_Flavio Bolsonaro']

    # Subtraindo o dano simulado
    latest_lula = df_analise['Base_Lula'].iloc[-1] - sim_economia
    latest_flavio = df_analise['Base_Flavio'].iloc[-1] - sim_escandalo
    
    # Pegando as tendências puras (100% Pesquisa) para a terceira via
    latest_cury = df_analise['Tendencia_Augusto Cury'].iloc[-1]
    latest_caiado = df_analise['Tendencia_Ronaldo Caiado'].iloc[-1]
    latest_zema = df_analise['Tendencia_Romeu Zema'].iloc[-1]
    latest_renan = df_analise['Tendencia_Renan Santos'].iloc[-1]

    st.markdown("---")
    st.markdown("### 🔥 Termômetro: Os Finalistas (Líderes)")

    # Calculando porcentagens válidas GERAIS (somando todos) para que o velocímetro represente 1º Turno
    total_votos_validos_1turno = latest_lula + latest_flavio + latest_cury + latest_caiado + latest_zema + latest_renan
    
    pct_lula_validos = (latest_lula / total_votos_validos_1turno) * 100
    pct_flavio_validos = (latest_flavio / total_votos_validos_1turno) * 100

    fig_gauge = go.Figure()
    fig_gauge.add_trace(go.Indicator(
        mode = "gauge+number", value = pct_lula_validos, title = {'text': "Lula (PT)", 'font': {'size': 24, 'color': 'red'}},
        number = {'suffix': "%", 'font': {'size': 40, 'color': 'red'}},
        gauge = {'axis': {'range': [0, 60], 'tickwidth': 1}, 'bar': {'color': "red"},
                 'steps': [{'range': [0, 50], 'color': "rgba(255, 0, 0, 0.1)"}],
                 'threshold': {'line': {'color': "black", 'width': 6}, 'thickness': 0.75, 'value': 50}}, domain = {'row': 0, 'column': 0}
    ))
    fig_gauge.add_trace(go.Indicator(
        mode = "gauge+number", value = pct_flavio_validos, title = {'text': "Flávio (PL)", 'font': {'size': 24, 'color': 'blue'}},
        number = {'suffix': "%", 'font': {'size': 40, 'color': 'blue'}},
        gauge = {'axis': {'range': [0, 60], 'tickwidth': 1}, 'bar': {'color': "blue"},
                 'steps': [{'range': [0, 50], 'color': "rgba(0, 0, 255, 0.1)"}],
                 'threshold': {'line': {'color': "black", 'width': 6}, 'thickness': 0.75, 'value': 50}}, domain = {'row': 0, 'column': 1}
    ))

    fig_gauge.update_layout(grid={'rows': 1, 'columns': 2, 'pattern': "independent"}, height=350, margin=dict(l=20, r=20, t=50, b=20))
    st.plotly_chart(fig_gauge, use_container_width=True)

    # ==================================
    # BLOCO NOVO: A TERCEIRA VIA
    # ==================================
    st.markdown("### 🏃‍♂️ A Terceira Via (Outros Candidatos)")
    st.markdown("O peso dos nanicos que impedem a vitória no primeiro turno:")
    
    pct_cury = (latest_cury / total_votos_validos_1turno) * 100
    pct_caiado = (latest_caiado / total_votos_validos_1turno) * 100
    pct_zema = (latest_zema / total_votos_validos_1turno) * 100
    pct_renan = (latest_renan / total_votos_validos_1turno) * 100
    
    df_terceira = pd.DataFrame({
        'Candidato': ['Augusto Cury', 'Ronaldo Caiado', 'Romeu Zema', 'Renan Santos'],
        'Porcentagem': [pct_cury, pct_caiado, pct_zema, pct_renan],
        'Cor': ['green', 'purple', 'orange', 'gold']
    }).sort_values(by='Porcentagem', ascending=True) # Ascendente para o barra horizontal ficar bonito
    
    fig_barras = px.bar(df_terceira, x='Porcentagem', y='Candidato', text='Porcentagem', orientation='h', color='Cor', color_discrete_map='identity')
    fig_barras.update_traces(texttemplate='%{text:.1f}%', textposition='outside', marker_line_color='black', marker_line_width=1)
    fig_barras.update_layout(height=250, xaxis=dict(range=[0, 10], visible=False), yaxis_title="", plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=0, t=0, b=0))
    st.plotly_chart(fig_barras, use_container_width=True)

    with st.expander("📊 Ver o Histórico de Crescimento ao Longo do Ano"):
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(x=df_analise['Data'], y=df_analise['Base_Lula'], mode='lines', name='Lula', line=dict(color='red', width=4)))
        fig1.add_trace(go.Scatter(x=df_analise['Data'], y=df_analise['Base_Flavio'], mode='lines', name='Flávio', line=dict(color='blue', width=4)))
        # Opcional: adicionar linhas fracas para os outros
        fig1.add_trace(go.Scatter(x=df_analise['Data'], y=df_analise['Tendencia_Augusto Cury'], mode='lines', name='Cury', line=dict(color='green', width=1, dash='dot')))
        fig1.add_trace(go.Scatter(x=df_analise['Data'], y=df_analise['Tendencia_Ronaldo Caiado'], mode='lines', name='Caiado', line=dict(color='purple', width=1, dash='dot')))
        fig1.add_trace(go.Scatter(x=df_analise['Data'], y=df_analise['Tendencia_Renan Santos'], mode='lines', name='Renan', line=dict(color='gold', width=1, dash='dot')))
        fig1.update_layout(height=350, hovermode='x unified', xaxis_title="", yaxis_title="Intenção Híbrida (%)")
        st.plotly_chart(fig1, use_container_width=True)

# ==========================================
# RODAPÉ: O PEDÁGIO DE LEADS (SOFT CAPTURE)
# ==========================================
st.markdown("---")
st.markdown("### 📊 Receba Nossas Futuras Predições")
st.markdown("Gostou deste painel de Inteligência de Dados? Deixe seu nome e WhatsApp abaixo caso tenha interesse em receber nossas futuras análises e predições de mercado.")

with st.form("lead_form"):
    col_nome, col_contato = st.columns(2)
    with col_nome:
        nome_lead = st.text_input("Seu Nome")
    with col_contato:
        contato_lead = st.text_input("Seu WhatsApp")
    
    submit_lead = st.form_submit_button("Enviar Contato", use_container_width=True)
    
    if submit_lead:
        if nome_lead and contato_lead:
            salvar_lead(nome_lead, contato_lead)
            st.success("✅ Contato salvo com sucesso! Obrigado pelo interesse nas nossas ferramentas de dados.")
        else:
            st.error("⚠️ Por favor, preencha o nome e o contato.")
