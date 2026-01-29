import streamlit as st
import os
import base64
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json

# --- CONFIGURAÇÃO INICIAL ---
st.set_page_config(
    page_title="Gestão Educacional",
    page_icon="logo.png",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CONFIGURAÇÕES DE SEGURANÇA (VIA SECRETS) ---
SHEET_NAME = "DB_GESTAO_EDUCACIONAL" 

# --- DADOS PADRÃO (BACKUP PARA PRIMEIRA CARGA) ---
DEFAULT_COORDENACAO = [
    {"label": "Ensalamento de Turmas", "link": "https://ensalamento-senai-gyf6eeutqqgmnvbab8zffj.streamlit.app/", "icon": "⏰"},
    {"label": "Cronograma Avaliação", "link": "https://docs.google.com/spreadsheets/d/10dOuco0yMCS201FnidWxq-BWgbNyTUhxxLNfs82H0t8/edit?gid=2119349890#gid=2119349890", "icon": "📊"},
    {"label": "Fechamento da Produção", "link": "https://docs.google.com/spreadsheets/d/14Lavd7aK2-bgAkCbe3xbdvBhnJvcIWXl/edit?gid=1532317622#gid=1532317622", "icon": "🔒"},
    {"label": "Recuperação Aprendizagem", "link": "https://docs.google.com/spreadsheets/d/1RlttoeaV4p_76AVWIo0-nG4W9ATPX3BF/edit#gid=784543561", "icon": "🎣"},
    {"label": "Tutoriais SGE", "link": "https://drive.google.com/drive/folders/1Ix3EZXUIyjR7F1X8NOWvvuWzrDyPwx99?usp=sharing", "icon": "🎥"},
    {"label": "Empresas Parceiras", "link": "https://docs.google.com/spreadsheets/d/1hzjvp4Hd29m59ow5SMrLlGJgamolZHYYDjstX-0xsBA/edit?pli=1&gid=102579484#gid=102579484", "icon": "⚙️"},
    {"label": "Bibliotech", "link": "https://bibliotechac.my.canva.site/", "icon": "🖥️"},
    {"label": "Contatos Escolas", "link": "https://docs.google.com/spreadsheets/d/1P4mU13bzJyvSASzuWpTFqecgyXlcJJ15/edit?gid=774781193#gid=774781193", "icon": "☎️"},
    {"label": "Cronograma Transversais", "link": "https://docs.google.com/spreadsheets/d/1fpki5rZmV63Hgo7k4dAIOWXhjcaPZ4x0/edit?pli=1&gid=271390469#gid=271390469", "icon": "📅"},
    {"label": "QTD Núcleo de Educação", "link": "https://docs.google.com/spreadsheets/d/1QXfS3_94f1-0PvVfCQdamaUHTFs1syoNSI4_kwhk62k/edit?gid=0#gid=0", "icon": "👩🏻‍🏫"},
    {"label": "Planejamento - ANAC", "link": "https://docs.google.com/spreadsheets/d/1cAapwvzyNMSglMJm6hC2eGphOI9QRUzo/edit?gid=514078859#gid=514078859", "icon": "🗃️"},
    {"label": "Planilha de Pagamento", "link": "https://sistemafieac.sharepoint.com/:x:/r/sites/intranetdosistemafieac001/_layouts/15/Doc.aspx?sourcedoc=%7B92129285-B585-4495-B4AC-BF728C457514%7D&file=Prestadores%20de%20Servi%C3%A7os%20-%20(GERAL).xlsx&action=default&mobileredirect=true", "icon": "💰"},
    {"label": "Frequência Empresa - APz 2025", "link": "https://docs.google.com/spreadsheets/d/1IleRhu3KXXnt5zONpSoMmWof8jHb_2t2/edit?gid=1807407531#gid=1807407531", "icon": "🏭"},
    {"label": "HOSHIM - SAEP 2025", "link": "https://docs.google.com/spreadsheets/d/1rtV7iXsYdvdkxEbjMCgwBfDnmrvWVu-c5-XAbk3Dvz8/edit?gid=99817763#gid=99817763", "icon": "🟣"},
]

DEFAULT_CRONOGRAMAS = {
    "FIC's (NEM)": [
        {"label": "TRILHA GESTÃO (2024-2025)", "link": "https://docs.google.com/spreadsheets/d/1vX35JOwsYnmFEOacJNPijK3q1OLfXiZ6/edit?gid=1416920738#gid=1416920738"},
        {"label": "TRILHA LOGÍSTICA (2025) - 1º ANO", "link": "https://docs.google.com/spreadsheets/d/1vX35JOwsYnmFEOacJNPijK3q1OLfXiZ6/edit?gid=1153727922#gid=1153727922"},
        {"label": "TRILHA LOGÍSTICA (2025) - 2º ANO", "link": "https://docs.google.com/spreadsheets/d/1vX35JOwsYnmFEOacJNPijK3q1OLfXiZ6/edit?gid=1997386750#gid=1997386750"},
        {"label": "TRILHA ENERGIAS (2025) - 2º ANO", "link": "https://docs.google.com/spreadsheets/d/1vX35JOwsYnmFEOacJNPijK3q1OLfXiZ6/edit?gid=502963705#gid=502963705"},
        {"label": "BUSCA ATIVA (NEM 2025)", "link": "https://docs.google.com/spreadsheets/d/1ZRnywoSl-FBlE-iYeu8AZZJNdJKZ3EeVLm_ShHQlR_M/edit?gid=1029141777#gid=1029141777"},
    ],
    "TÉCNICOS NEM": [
        {"label": "ELETROTÉCNICA (2023-2025)", "link": "https://docs.google.com/spreadsheets/d/15xyt51ttXsHLMRctXAWgYlzdCAJEa39s/edit#gid=435143336"},
        {"label": "TÉC. EM SEGURANÇA (2023-2025)", "link": "https://docs.google.com/spreadsheets/d/15xyt51ttXsHLMRctXAWgYlzdCAJEa39s/edit#gid=868615014"},
        {"label": "ENERGIA RENOVÁVEL (2024-2026)", "link": "https://docs.google.com/spreadsheets/d/15xyt51ttXsHLMRctXAWgYlzdCAJEa39s/edit#gid=957305393"},
        {"label": "BUSCA ATIVA (NEM 2023-2026)", "link": "https://docs.google.com/spreadsheets/d/1IjSLQkJ1s2nNDPgrqeqWPdiK_WGIniA7/edit?gid=703051653#gid=703051653"},
    ],
    "FIC's (SENAI)  ": [
        {"label": "APERFEIÇOAMENTO PROFISSIONAL", "link": "https://docs.google.com/spreadsheets/d/1vX35JOwsYnmFEOacJNPijK3q1OLfXiZ6/edit?gid=1354816975#gid=1354816975"},
        {"label": "QUALIFICAÇÃO PROFISSIONAL", "link": "https://docs.google.com/spreadsheets/d/1vX35JOwsYnmFEOacJNPijK3q1OLfXiZ6/edit?gid=601664707#gid=601664707"},
        {"label": "Busca Ativa (2025)", "link": "#"}, 
    ],
    "Técnicos SENAI": [
        {"label": "TÉC. EM SEGURANÇA - EAD (2023-2025)", "link": "https://docs.google.com/spreadsheets/d/1vX35JOwsYnmFEOacJNPijK3q1OLfXiZ6/edit?gid=1925712139#gid=1925712139"},
        {"label": "TÉC. ELETROTÉCNICA (2025-2027)", "link": "https://docs.google.com/spreadsheets/d/1vX35JOwsYnmFEOacJNPijK3q1OLfXiZ6/edit?gid=624513768#gid=624513768"},
    ],
    "Aprendizagem": [
        {"label": "PROCESSOS LOGÍSTICOS - 2025", "link": "#"}, 
        {"label": "GESTÃO INDUSTRIAL - 2025", "link": "#"},
        {"label": "PROGRAMA EDIFICAÇÕES - 2025", "link": "https://docs.google.com/spreadsheets/d/1vX35JOwsYnmFEOacJNPijK3q1OLfXiZ6/edit?gid=1795228939#gid=1795228939"},
        {"label": "BUSCA ATIVA (2025)", "link": "https://docs.google.com/spreadsheets/d/1EegVLYMhoJzrO5jizmaZCH6gbjpS15jf/edit?gid=1368374156#gid=1368374156"},
    ],
    "BACKUP": [
        {"label": "BACKUP 2024", "link": "https://drive.google.com/drive/folders/1DO2T2gg2WV9B-s4ZrqzkgJTnqrPSuIp0"},
        {"label": "BACKUP 2025", "link": "#"},
    ]
}

DEFAULT_TURMAS = {
    "FIC'S (NEM) 2024": [
        {"label": "GESTÃO A  MANHÃ (2024)", "link": "https://docs.google.com/spreadsheets/d/1SiCncHnELxcCs2X5OKKVmhvDnlAgWxyLlF7lBB7dRAM/edit#gid=0"},
        {"label": "GESTÃO A  TARDE (2024)", "link": "https://docs.google.com/spreadsheets/d/1SiCncHnELxcCs2X5OKKVmhvDnlAgWxyLlF7lBB7dRAM/edit#gid=697238086"},
        {"label": "GESTÃO B  TARDE (2024)", "link": "https://docs.google.com/spreadsheets/d/1SiCncHnELxcCs2X5OKKVmhvDnlAgWxyLlF7lBB7dRAM/edit#gid=1124027835"},
    ],
    "FIC'S (NEM) 2025": [
        {"label": "TRILHA LOGÍSTICA - 1 MANHÃ (1º ANO)", "link": "https://docs.google.com/spreadsheets/d/1SiCncHnELxcCs2X5OKKVmhvDnlAgWxyLlF7lBB7dRAM/edit?gid=389234120#gid=389234120"},
        {"label": "TRILHA LOGÍSTICA - 2 TARDE (1º ANO)", "link": "https://docs.google.com/spreadsheets/d/1029141777#gid=1029141777"},
        {"label": "TRILHA LOGÍSTICA - 3 TARDE (1º ANO)", "link": "https://docs.google.com/spreadsheets/d/603235616#gid=603235616"},
        {"label": "TRILHA LOGÍSTICA - 4 TARDE (1º ANO)", "link": "https://docs.google.com/spreadsheets/d/417445561#gid=417445561"},
        {"label": "TRILHA LOGÍSTICA - 5 MANHÃ (2º ANO)", "link": "https://docs.google.com/spreadsheets/d/155259147#gid=155259147"},
        {"label": "TRILHA LOGÍSTICA - 6 TARDE (2º ANO)", "link": "https://docs.google.com/spreadsheets/d/924723208#gid=924723208"},
        {"label": "TRILHA LOGÍSTICA - 7 TARDE (2º ANO)", "link": "https://docs.google.com/spreadsheets/d/1285656207#gid=1285656207"},
        {"label": "TRILHA ENERGIAS - MANHÃ (2º ANO)", "link": "https://docs.google.com/spreadsheets/d/1622990027#gid=1622990027"},
    ],
    "TÉCNICOS NEM": [
        {"label": "TÉCNICO EM ELETROTÉCNICA (2023-2025)", "link": "https://docs.google.com/spreadsheets/d/15xyt51ttXsHLMRctXAWgYlzdCAJEa39s/edit#gid=435143336"},
        {"label": "TÉCNICO EM SEGURANÇA (2023-2025)", "link": "https://docs.google.com/spreadsheets/d/15xyt51ttXsHLMRctXAWgYlzdCAJEa39s/edit#gid=868615014"},
        {"label": "TÉCNICO EM ENERGIA RENOVÁVEL (2024-2026)", "link": "https://docs.google.com/spreadsheets/d/15xyt51ttXsHLMRctXAWgYlzdCAJEa39s/edit#gid=957305393"},
    ],
    "TÉCNICOS SENAI": [
        {"label": "TÉCNICO EM SEGURANÇA - EAD (2023-2025)", "link": "https://docs.google.com/spreadsheets/d/1kyoLq4OjsAfvLVNHeKb7ZmsU2XYg6nrG/edit?gid=307972768#gid=307972768"},
    ],
    "FIC'S (SENAI)": [
        {"label": "FREQUÊNCIAS FIC'S 2025", "link": "https://docs.google.com/spreadsheets/d/1l155mknMTu-6lzLb2OnGFHszqile8MI6GmH8-Cu4AK0/edit?gid=1356514585#gid=1356514585"},
    ],
    "APRENDIZAGEM (2025)": [
        {"label": "GESTÃO INDUSTRIAL 1 - MANHÃ", "link": "https://docs.google.com/spreadsheets/d/1lnLTVwv8dGuo9NGHOHaktLF6HVLW4i9KCsT5ttwhcwk/edit?gid=1484510770#gid=1484510770"},
        {"label": "GESTÃO INDUSTRIAL 2 - MANHÃ", "link": "https://docs.google.com/spreadsheets/d/1lnLTVwv8dGuo9NGHOHaktLF6HVLW4i9KCsT5ttwhcwk/edit?gid=1398337132#gid=1398337132"},
        {"label": "GESTÃO INDUSTRIAL 3 - TARDE", "link": "https://docs.google.com/spreadsheets/d/1lnLTVwv8dGuo9NGHOHaktLF6HVLW4i9KCsT5ttwhcwk/edit?gid=1806022898#gid=1806022898"},
        {"label": "GESTÃO INDUSTRIAL 4 - TARDE", "link": "https://docs.google.com/spreadsheets/d/1lnLTVwv8dGuo9NGHOHaktLF6HVLW4i9KCsT5ttwhcwk/edit?gid=298475697#gid=298475697"},
        {"label": "GESTÃO INDUSTRIAL 5 - TARDE", "link": "https://docs.google.com/spreadsheets/d/1lnLTVwv8dGuo9NGHOHaktLF6HVLW4i9KCsT5ttwhcwk/edit?gid=1375636971#gid=1375636971"},
        {"label": "OPERAÇÕES LOGÍSTICAS 1 - MANHÃ", "link": "https://docs.google.com/spreadsheets/d/1lnLTVwv8dGuo9NGHOHaktLF6HVLW4i9KCsT5ttwhcwk/edit?gid=309880873#gid=309880873"},
        {"label": "OPERAÇÕES LOGÍSTICAS 2 - MANHÃ", "link": "https://docs.google.com/spreadsheets/d/1lnLTVwv8dGuo9NGHOHaktLF6HVLW4i9KCsT5ttwhcwk/edit?gid=1886911715#gid=1886911715"},
        {"label": "OPERAÇÕES LOGÍSTICAS 3 - TARDE", "link": "https://docs.google.com/spreadsheets/d/1lnLTVwv8dGuo9NGHOHaktLF6HVLW4i9KCsT5ttwhcwk/edit?gid=1069851690#gid=1069851690"},
        {"label": "PROGRAMA DE EDIFICAÇÕES", "link": "https://docs.google.com/spreadsheets/d/1lnLTVwv8dGuo9NGHOHaktLF6HVLW4i9KCsT5ttwhcwk/edit?gid=583575371#gid=583575371"},
        {"label": "PROGRAMA DE GESTÃO C - MANHÃ", "link": "#"},
        {"label": "PROGRAMA DE GESTÃO C - TARDE", "link": "#"},
        {"label": "LOGÍSTICA MERCALE - TARDE", "link": "#"},
    ]
}

# --- GOOGLE SHEETS CONNECTION (CORREÇÃO DE BASE64) ---

@st.cache_resource
def get_gspread_client():
    """Conecta ao Google Sheets usando st.secrets com tratamento robusto de chave"""
    # Verifica se os segredos existem
    if "gcp_service_account" not in st.secrets:
        st.error("Segredos do Google (gcp_service_account) não configurados!")
        return None
        
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    
    # 1. Copia o dicionário para não alterar o original
    creds_dict = dict(st.secrets["gcp_service_account"])
    
    # 2. VACINA ROBUSTA PARA O ERRO "INCORRECT PADDING"
    if "private_key" in creds_dict:
        private_key = creds_dict["private_key"]
        
        # Se a chave não começar com o cabeçalho correto, algo está errado na cópia
        if "-----BEGIN PRIVATE KEY-----" not in private_key:
            st.error("ERRO CRÍTICO: A 'private_key' nos Secrets está incompleta. Verifique se copiou desde '-----BEGIN...'.")
            return None
            
        # Tratamento de quebras de linha:
        # Se tiver "\n" literais (duas letras), converte para enter real
        # Se tiver espaços onde deveria ter enter, tenta corrigir (comum em copy-paste)
        private_key = private_key.replace("\\n", "\n")
        
        # Garante que não há espaços em branco no início ou fim que geram padding error
        creds_dict["private_key"] = private_key.strip()
    
    try:
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        return client
    except Exception as e:
        # Mostra o erro na tela para facilitar o debug (remova em produção se quiser)
        st.error(f"Erro na autenticação do Google: {e}")
        return None

def load_data_from_sheet():
    """Lê os dados da planilha e converte para o formato do app"""
    # Se não tiver secrets configurados, usa o backup local para não quebrar
    if "gcp_service_account" not in st.secrets:
        return {"coordenacao": DEFAULT_COORDENACAO, "cronogramas": DEFAULT_CRONOGRAMAS, "turmas": DEFAULT_TURMAS}

    client = get_gspread_client()
    if not client:
        return {"coordenacao": DEFAULT_COORDENACAO, "cronogramas": DEFAULT_CRONOGRAMAS, "turmas": DEFAULT_TURMAS}
    
    try:
        sheet = client.open(SHEET_NAME).sheet1
        records = sheet.get_all_records()
        
        # Se planilha vazia, faz carga inicial
        if not records:
            save_data_to_sheet({
                "coordenacao": DEFAULT_COORDENACAO,
                "cronogramas": DEFAULT_CRONOGRAMAS,
                "turmas": DEFAULT_TURMAS
            })
            return {"coordenacao": DEFAULT_COORDENACAO, "cronogramas": DEFAULT_CRONOGRAMAS, "turmas": DEFAULT_TURMAS}

        # Reconstrói a estrutura
        db = {"coordenacao": [], "cronogramas": {}, "turmas": {}}
        
        for row in records:
            item = {"label": row["LABEL"], "link": row["LINK"]}
            if row["ICONE"]: item["icon"] = row["ICONE"]
            
            if row["ABA"] == "Coordenação":
                db["coordenacao"].append(item)
            elif row["ABA"] == "Cronogramas":
                cat = row["CATEGORIA"]
                if cat not in db["cronogramas"]: db["cronogramas"][cat] = []
                db["cronogramas"][cat].append(item)
            elif row["ABA"] == "Gestão de Turmas":
                cat = row["CATEGORIA"]
                if cat not in db["turmas"]: db["turmas"][cat] = []
                db["turmas"][cat].append(item)
                
        return db
    except Exception as e:
        # st.error(f"Erro ao conectar na planilha: {e}") # Descomente para debug
        return {"coordenacao": DEFAULT_COORDENACAO, "cronogramas": DEFAULT_CRONOGRAMAS, "turmas": DEFAULT_TURMAS}

def save_data_to_sheet(data):
    """Limpa a planilha e reescreve tudo"""
    client = get_gspread_client()
    if not client:
        return
    
    sheet = client.open(SHEET_NAME).sheet1
    
    # Prepara as linhas para salvar
    rows = []
    # Cabeçalho
    rows.append(["ABA", "CATEGORIA", "LABEL", "LINK", "ICONE"])
    
    # Processa Coordenação
    for item in data["coordenacao"]:
        rows.append(["Coordenação", "Geral", item["label"], item["link"], item.get("icon", "")])
        
    # Processa Cronogramas
    for cat, items in data["cronogramas"].items():
        for item in items:
            rows.append(["Cronogramas", cat, item["label"], item["link"], ""])
            
    # Processa Turmas
    for cat, items in data["turmas"].items():
        for item in items:
            rows.append(["Gestão de Turmas", cat, item["label"], item["link"], ""])
            
    # Atualiza a planilha
    sheet.clear()
    sheet.update(rows)

# --- ESTILIZAÇÃO ---
st.markdown("""
    <style>
    .main-header { text-align: center; margin-bottom: 1.5rem; }
    .main-header h1 { color: #0046ad; font-weight: 800; font-size: 2.2rem; margin: 0; text-transform: uppercase; }
    
    button[data-baseweb="tab"] { padding: 0.5rem 1rem !important; flex: 1; }
    .stTabs [data-baseweb="tab"] p { font-size: 20px !important; font-weight: 700 !important; }
    button[data-baseweb="tab"][aria-selected="true"] { color: #0046ad !important; border-bottom-color: #0046ad !important; background-color: #f8f9fa; }

    div[data-testid="stLinkButton"] > a {
        width: 100% !important; border-radius: 8px; min-height: 3.2em !important; height: auto !important; 
        border: 1px solid #e6e6e6; box-shadow: 0 1px 2px rgba(0,0,0,0.05); color: #333333 !important;
        text-decoration: none !important; transition: all 0.2s ease-in-out;
        display: flex !important; align-items: center !important; justify-content: flex-start !important;
        padding: 0.4rem 12px !important; font-size: 13.5px !important; line-height: 1.25 !important; white-space: normal !important;
    }
    div[data-testid="stLinkButton"] > a > div { justify-content: flex-start !important; text-align: left !important; width: 100%; }
    div[data-testid="stLinkButton"] > a:hover { border-color: #0046ad; background-color: #f0f7ff; transform: translateY(-1px); box-shadow: 0 3px 6px rgba(0,70,173,0.15); color: #0046ad !important; }
    
    .category-title { color: #0046ad; font-size: 0.95rem; font-weight: 700; margin-bottom: 8px; border-bottom: 1px solid #f0f2f6; padding-bottom: 4px; margin-top: 15px; text-transform: uppercase; letter-spacing: 0.5px; }
    .block-container { padding-top: 1.5rem; }
    
    .logo-wrapper { display: flex; justify-content: center; margin-bottom: 0.5rem; }
    .logo-wrapper img { max-width: 260px; width: 100%; height: auto; object-fit: contain; }
    @media (max-width: 768px) { .logo-wrapper img { max-width: 180px; } }
    </style>
""", unsafe_allow_html=True)

# --- CARREGA DADOS ---
db_data = load_data_from_sheet()

# --- FUNÇÕES VISUAIS ---
def render_header():
    c_left, c_center, c_right = st.columns([1, 2, 1]) 
    with c_center:
        if os.path.exists("logo.png"):
            with open("logo.png", "rb") as img_file:
                img_base64 = base64.b64encode(img_file.read()).decode()
            st.markdown(f"""<div class="logo-wrapper"><img src="data:image/png;base64,{img_base64}"></div>""", unsafe_allow_html=True)
        else:
            st.markdown("<h2 style='text-align: center; color: gray;'>[LOGO.PNG]</h2>", unsafe_allow_html=True)
        st.markdown("""<div class="main-header"><h1>Gestão Educacional</h1></div>""", unsafe_allow_html=True)

def render_cards_grid(item_list, cols=2):
    for i in range(0, len(item_list), cols):
        row_items = item_list[i:i+cols]
        columns = st.columns(cols)
        for index, item in enumerate(row_items):
            with columns[index]:
                st.link_button(label=f"{item.get('icon', '➡️')}  {item['label']}", url=item['link'], use_container_width=True)

# --- PAINEL ADMIN (SENHA VIA SECRETS) ---
def admin_sidebar():
    st.sidebar.header("🔒 Área da Coordenação")
    
    # Verifica se os segredos existem antes de mostrar login
    if "admin_password" not in st.secrets:
        # Se estiver rodando local sem secrets.toml configurado
        if "gcp_service_account" not in st.secrets:
             st.sidebar.info("Modo Leitura (Secrets não configurados)")
        return

    password = st.sidebar.text_input("Senha de Acesso", type="password")
    
    # Validação da senha segura
    if password == st.secrets["admin_password"]:
        st.sidebar.success("Conectado ao Banco de Dados")
        st.sidebar.markdown("---")
        
        action = st.sidebar.radio("Ação:", ["Adicionar Link", "Remover Link", "Nova Categoria", "Remover Categoria"])
        tab_choice = st.sidebar.selectbox("Selecionar Aba:", ["Coordenação", "Cronogramas", "Gestão de Turmas"])
        
        db_key = ""
        if tab_choice == "Coordenação": db_key = "coordenacao"
        elif tab_choice == "Cronogramas": db_key = "cronogramas"
        elif tab_choice == "Gestão de Turmas": db_key = "turmas"
        
        if action == "Adicionar Link":
            with st.sidebar.form("add"):
                label = st.text_input("Nome")
                link = st.text_input("Link")
                cat = st.selectbox("Categoria", list(db_data[db_key].keys())) if db_key != "coordenacao" else None
                if st.form_submit_button("Salvar"):
                    item = {"label": label, "link": link}
                    if db_key == "coordenacao": 
                        item["icon"] = "📌"
                        db_data[db_key].append(item)
                    else: db_data[db_key][cat].append(item)
                    save_data_to_sheet(db_data)
                    st.rerun()
                    
        elif action == "Remover Link":
            if db_key == "coordenacao":
                opts = [x["label"] for x in db_data[db_key]]
                delt = st.sidebar.selectbox("Remover", opts)
                if st.sidebar.button("Confirmar"):
                    db_data[db_key] = [x for x in db_data[db_key] if x["label"] != delt]
                    save_data_to_sheet(db_data)
                    st.rerun()
            else:
                cat = st.sidebar.selectbox("Categoria", list(db_data[db_key].keys()))
                if cat:
                    opts = [x["label"] for x in db_data[db_key][cat]]
                    delt = st.sidebar.selectbox("Remover", opts)
                    if st.sidebar.button("Confirmar"):
                        db_data[db_key][cat] = [x for x in db_data[db_key][cat] if x["label"] != delt]
                        save_data_to_sheet(db_data)
                        st.rerun()
        
        if action == "Nova Categoria" and db_key != "coordenacao":
             new_c = st.sidebar.text_input("Nova Categoria")
             if st.sidebar.button("Criar"):
                 if new_c not in db_data[db_key]:
                     db_data[db_key][new_c] = []
                     save_data_to_sheet(db_data)
                     st.rerun()
                     
        if action == "Remover Categoria" and db_key != "coordenacao":
            del_c = st.sidebar.selectbox("Apagar Categoria", list(db_data[db_key].keys()))
            if st.sidebar.button("Apagar Tudo"):
                del db_data[db_key][del_c]
                save_data_to_sheet(db_data)
                st.rerun()

# --- MAIN ---
def main():
    admin_sidebar()
    render_header()
    
    tab1, tab2, tab3 = st.tabs(["Coordenação Pedagógica", "Cronogramas", "Gestão de Turmas"])
    
    with tab1:
        s1, c, s2 = st.columns([1, 3, 1])
        with c:
            st.markdown("<br>", unsafe_allow_html=True)
            render_cards_grid(db_data["coordenacao"], cols=2)
            
    with tab2:
        s1, c, s2 = st.columns([0.5, 10, 0.5])
        with c:
            st.markdown("<br>", unsafe_allow_html=True)
            c1, c2, c3 = st.columns(3, gap="medium")
            items = list(db_data["cronogramas"].items())
            with c1:
                for k, v in items[0::3]:
                    st.markdown(f"<div class='category-title'>📂 {k}</div>", unsafe_allow_html=True)
                    render_cards_grid(v, cols=1)
                    st.markdown("<br>", unsafe_allow_html=True)
            with c2:
                for k, v in items[1::3]:
                    st.markdown(f"<div class='category-title'>📂 {k}</div>", unsafe_allow_html=True)
                    render_cards_grid(v, cols=1)
                    st.markdown("<br>", unsafe_allow_html=True)
            with c3:
                for k, v in items[2::3]:
                    st.markdown(f"<div class='category-title'>📂 {k}</div>", unsafe_allow_html=True)
                    render_cards_grid(v, cols=1)
                    st.markdown("<br>", unsafe_allow_html=True)

    with tab3:
        # Mesma lógica do Tab 2 para Turmas
        s1, c, s2 = st.columns([0.5, 10, 0.5])
        with c:
            st.markdown("<br>", unsafe_allow_html=True)
            c1, c2, c3 = st.columns(3, gap="medium")
            items = list(db_data["turmas"].items())
            with c1:
                for k, v in items[0::3]:
                    st.markdown(f"<div class='category-title'>📂 {k}</div>", unsafe_allow_html=True)
                    render_cards_grid(v, cols=1)
                    st.markdown("<br>", unsafe_allow_html=True)
            with c2:
                for k, v in items[1::3]:
                    st.markdown(f"<div class='category-title'>📂 {k}</div>", unsafe_allow_html=True)
                    render_cards_grid(v, cols=1)
                    st.markdown("<br>", unsafe_allow_html=True)
            with c3:
                for k, v in items[2::3]:
                    st.markdown(f"<div class='category-title'>📂 {k}</div>", unsafe_allow_html=True)
                    render_cards_grid(v, cols=1)
                    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("<div style='text-align: center; color: gray; font-size: 0.8em;'>© 2026 SENAI HUB • GeEdu Cloud v1.0</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()