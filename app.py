import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import statsmodels.api as sm
import json
import time
import os
import datetime
import requests

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

if 'modo' not in st.session_state:
    st.session_state['modo'] = "Predição"

modo_app = st.session_state['modo']

if modo_app == "🔴 Apuração Oficial (TSE)":
    # MÓDULO 1: APURAÇÃO AO VIVO TSE
    st.title("🔴 TSE: Apuração ao Vivo")
    st.markdown("Conectado à base oficial de totalização de votos.")
    
    # "Tomada" para o link do TSE na véspera
    with st.expander("🔗 Conectar ao Servidor do TSE"):
        url_tse = st.text_input("Link oficial do Governo (deixe em branco para simulação):", value="")
    
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("⬅️ Voltar para Predição", use_container_width=True):
            st.session_state['modo'] = "Predição"
            st.rerun()
    with col_btn2:
        if st.button("🔄 Forçar Atualização", use_container_width=True):
            st.toast("Buscando dados...")
            time.sleep(0.5)
            
    # Robô invisível de atualização automática (sempre ligado a cada 30s)
    import streamlit.components.v1 as components
    components.html(
        "<script>setTimeout(function(){ window.parent.location.reload(); }, 30000);</script>",
        height=0
    )
        
    try:
        if url_tse.strip():
            # Conecta direto no governo
            headers = {'User-Agent': 'Mozilla/5.0'}
            req = requests.get(url_tse.strip(), headers=headers, timeout=10)
            dados_tse = req.json()
        else:
            # Usa o simulador local
            with open("tse_apuracao_mock.json", "r", encoding='utf-8') as f:
                dados_tse = json.load(f)
            
            import random
            # SIMULAÇÃO AO VIVO: Faz os números subirem baseados no relógio
            segundos_passados = (datetime.datetime.now().minute * 60) + datetime.datetime.now().second
            incremento = (segundos_passados / 3600.0) * 15.0 # Sobe até 15% a cada hora
            
            urnas_base = float(dados_tse.get("pst", 0))
            nova_urna = min(urnas_base + incremento, 99.99)
            dados_tse["pst"] = f"{nova_urna:.2f}"
            dados_tse["ht"] = datetime.datetime.now().strftime("%H:%M:%S")
            
            if len(dados_tse.get("cand", [])) >= 2:
                p1_base = float(dados_tse["cand"][0]["pvap"])
                p2_base = float(dados_tse["cand"][1]["pvap"])
                flut = random.uniform(-0.15, 0.15)
                dados_tse["cand"][0]["pvap"] = f"{p1_base + flut:.2f}"
                dados_tse["cand"][1]["pvap"] = f"{p2_base - flut:.2f}"
            
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
            st.plotly_chart(fig_apuracao, use_container_width=True, config={'displayModeBar': False})
            
    except Exception as e:
        st.error(f"Erro ao conectar com o TSE: {e}")

else:
    # MÓDULO 2: PREDIÇÃO GAMIFICADA DE 2º TURNO E AUTÓPSIA
    if st.button("🔴 ACOMPANHAR APURAÇÃO OFICIAL AO VIVO", type="primary", use_container_width=True):
        st.session_state['modo'] = "🔴 Apuração Oficial (TSE)"
        st.rerun()

    st.title("🔥 Oráculo 2026: A Batalha Final")
    st.markdown("O simulador preditivo focado na engenharia matemática do 2º Turno.")

    # NOVO BLOCO: AUTÓPSIA DO 1º TURNO
    st.error("🚨 **AUTÓPSIA DO 1º TURNO:** Por que a Inteligência Artificial errou?")
    st.markdown("**Resultado Oficial:** Flávio (47.03%), Lula (45.16%) e Cury derretendo para (2.89%).")
    st.markdown("**O Erro do Sistema:** A nossa IA foi enganada pela *Ilusão de Engajamento*. Cury, Zema e Caiado tinham um tráfego colossal na internet (Voto Quente), o que mantinha eles com quase 15% nas nossas projeções ao longo do mês. Porém, nas últimas 48 horas, o pânico do **Voto Útil** tomou conta do país. O eleitor abandonou a terceira via na boca de urna para tentar decidir a eleição no 1º turno, esvaziando completamente os nanicos. O Voto Quente da internet não virou voto real.")
    
    st.markdown("---")
    
    st.markdown("### 🎮 Simulador do 2º Turno: O Leilão dos Órfãos")
    st.markdown("A eleição agora depende **exclusivamente** dos **7.81% dos votos válidos** que sobraram da terceira via (Cury, Zema, Caiado, etc). Para quem eles vão transferir seus votos?")
    
    col_sim1, col_sim2 = st.columns(2)
    with col_sim1:
        transf_flavio = st.slider("🔵 % da 3ª Via que vota no Flávio", min_value=0, max_value=100, value=40, format="%d%%")
    with col_sim2:
        transf_lula = st.slider("🔴 % da 3ª Via que vota no Lula", min_value=0, max_value=100, value=40, format="%d%%")
        
    st.caption("Nota: Se a soma não der 100%, o sistema entende que os eleitores restantes votarão Nulo/Branco.")
    
    # Matemática do 2º Turno
    votos_orfaos = 7.81
    base_flavio = 47.03
    base_lula = 45.16
    
    proj_flavio = base_flavio + (votos_orfaos * (transf_flavio / 100.0))
    proj_lula = base_lula + (votos_orfaos * (transf_lula / 100.0))
    
    # Normalizando para válidos no 2º Turno (ignora brancos e nulos)
    total_validos_2t = proj_flavio + proj_lula
    pct_flavio_final = (proj_flavio / total_validos_2t) * 100
    pct_lula_final = (proj_lula / total_validos_2t) * 100

    st.markdown("---")
    st.markdown("### 🔮 Projeção do Vencedor (Votos Válidos 2ºT)")

    fig_gauge = go.Figure()
    fig_gauge.add_trace(go.Indicator(
        mode = "gauge+number", value = pct_lula_final, title = {'text': "Lula (PT)", 'font': {'size': 24, 'color': 'red'}},
        number = {'suffix': "%", 'font': {'size': 40, 'color': 'red'}, 'valueformat': ".1f"},
        gauge = {'axis': {'range': [0, 100], 'tickwidth': 1}, 'bar': {'color': "red"},
                 'steps': [{'range': [0, 50], 'color': "rgba(255, 0, 0, 0.1)"}],
                 'threshold': {'line': {'color': "black", 'width': 6}, 'thickness': 0.75, 'value': 50}}, domain = {'row': 0, 'column': 0}
    ))
    fig_gauge.add_trace(go.Indicator(
        mode = "gauge+number", value = pct_flavio_final, title = {'text': "Flávio (PL)", 'font': {'size': 24, 'color': 'blue'}},
        number = {'suffix': "%", 'font': {'size': 40, 'color': 'blue'}, 'valueformat': ".1f"},
        gauge = {'axis': {'range': [0, 100], 'tickwidth': 1}, 'bar': {'color': "blue"},
                 'steps': [{'range': [0, 50], 'color': "rgba(0, 0, 255, 0.1)"}],
                 'threshold': {'line': {'color': "black", 'width': 6}, 'thickness': 0.75, 'value': 50}}, domain = {'row': 0, 'column': 1}
    ))

    fig_gauge.update_layout(grid={'rows': 1, 'columns': 2, 'pattern': "independent"}, height=350, margin=dict(l=20, r=20, t=50, b=20))
    st.plotly_chart(fig_gauge, use_container_width=True, config={'displayModeBar': False})

    vencedor = "Flávio Bolsonaro" if pct_flavio_final > pct_lula_final else ("Lula" if pct_lula_final > pct_flavio_final else "Empate Técnico")
    cor_vencedor = "blue" if vencedor == "Flávio Bolsonaro" else ("red" if vencedor == "Lula" else "gray")
    
    st.markdown(f"<h3 style='text-align: center;'>Com esta migração, o Eleito seria: <strong style='color: {cor_vencedor};'>{vencedor}</strong></h3>", unsafe_allow_html=True)

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
