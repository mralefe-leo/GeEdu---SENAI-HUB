import streamlit as st
import os
import json
import base64
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- CONFIGURAÇÃO INICIAL ---
st.set_page_config(
    page_title="Gestão Educacional",
    page_icon="logo.png",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CONSTANTES ---
# A senha será carregada dos Secrets. O arquivo local é apenas fallback.
SHEET_NAME = "DB_GESTAO_EDUCACIONAL"

# --- DADOS PADRÃO (BACKUP PARA PRIMEIRA CARGA) ---
# (Mantenha seus dados DEFAULT aqui igual ao código anterior para economizar espaço na resposta,
#  mas no seu arquivo real, mantenha as listas DEFAULT_COORDENACAO, etc...)

# ... COLE AQUI AS LISTAS: DEFAULT_COORDENACAO, DEFAULT_CRONOGRAMAS, DEFAULT_TURMAS ...
# Vou resumir aqui só para o exemplo, mas você mantém as suas completas:
DEFAULT_COORDENACAO = [{"label": "Ensalamento", "link": "#", "icon": "⏰"}] 
DEFAULT_CRONOGRAMAS = {"Exemplo": []}
DEFAULT_TURMAS = {"Exemplo": []}

# --- FUNÇÕES DE CONEXÃO E DADOS ---

@st.cache_resource
def get_gspread_client():
    """
    Conecta ao Google Sheets usando st.secrets (Produção) 
    ou credentials.json (Local)
    """
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    
    try:
        # TENTATIVA 1: Produção (Streamlit Cloud Secrets)
        # O Streamlit transforma o TOML em um dicionário Python automaticamente
        if "gcp_service_account" in st.secrets:
            creds_dict = st.secrets["gcp_service_account"]
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
            return gspread.authorize(creds)

        # TENTATIVA 2: Local (Arquivo credentials.json)
        elif os.path.exists("credentials.json"):
            creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
            return gspread.authorize(creds)
            
        else:
            return None

    except Exception as e:
        st.error(f"Erro na conexão: {e}")
        return None

def load_data_from_sheet():
    client = get_gspread_client()
    
    # Se não conectar, usa os Defaults (Modo Offline/Segurança)
    if not client:
        return {"coordenacao": DEFAULT_COORDENACAO, "cronogramas": DEFAULT_CRONOGRAMAS, "turmas": DEFAULT_TURMAS}
    
    try:
        # Tenta abrir a planilha
        try:
            sheet = client.open(SHEET_NAME).sheet1
        except gspread.SpreadsheetNotFound:
            st.error(f"Planilha '{SHEET_NAME}' não encontrada. Verifique se compartilhou com o email da API.")
            return {"coordenacao": DEFAULT_COORDENACAO, "cronogramas": DEFAULT_CRONOGRAMAS, "turmas": DEFAULT_TURMAS}

        records = sheet.get_all_records()
        
        # Se vazia, popula
        if not records:
            save_data_to_sheet({
                "coordenacao": DEFAULT_COORDENACAO,
                "cronogramas": DEFAULT_CRONOGRAMAS,
                "turmas": DEFAULT_TURMAS
            })
            return {"coordenacao": DEFAULT_COORDENACAO, "cronogramas": DEFAULT_CRONOGRAMAS, "turmas": DEFAULT_TURMAS}

        # Reconstrói estrutura
        db = {"coordenacao": [], "cronogramas": {}, "turmas": {}}
        for row in records:
            item = {"label": str(row["LABEL"]), "link": str(row["LINK"])}
            if row.get("ICONE"): item["icon"] = str(row["ICONE"])
            
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
        st.warning(f"Usando backup local. Erro ao ler planilha: {e}")
        return {"coordenacao": DEFAULT_COORDENACAO, "cronogramas": DEFAULT_CRONOGRAMAS, "turmas": DEFAULT_TURMAS}

def save_data_to_sheet(data):
    client = get_gspread_client()
    if not client:
        st.error("Não conectado. Alterações não salvas na nuvem.")
        return
    
    try:
        sheet = client.open(SHEET_NAME).sheet1
        rows = [["ABA", "CATEGORIA", "LABEL", "LINK", "ICONE"]]
        
        for item in data["coordenacao"]:
            rows.append(["Coordenação", "Geral", item["label"], item["link"], item.get("icon", "")])
        for cat, items in data["cronogramas"].items():
            for item in items:
                rows.append(["Cronogramas", cat, item["label"], item["link"], ""])
        for cat, items in data["turmas"].items():
            for item in items:
                rows.append(["Gestão de Turmas", cat, item["label"], item["link"], ""])
        
        sheet.clear()
        sheet.update(rows)
    except Exception as e:
        st.error(f"Erro ao salvar: {e}")

# Carrega Dados
db_data = load_data_from_sheet()

# --- FUNÇÕES VISUAIS ---

def render_header():
    c_left, c_center, c_right = st.columns([1, 2, 1]) 
    with c_center:
        # Tenta carregar logo local
        if os.path.exists("logo.png"):
            with open("logo.png", "rb") as img_file:
                img_base64 = base64.b64encode(img_file.read()).decode()
            st.markdown(f"""<div class="logo-wrapper"><img src="data:image/png;base64,{img_base64}"></div>""", unsafe_allow_html=True)
        else:
            st.markdown("<h2 style='text-align: center; color: gray;'>[LOGO]</h2>", unsafe_allow_html=True)
        st.markdown("""<div class="main-header"><h1>Gestão Educacional</h1></div>""", unsafe_allow_html=True)

def render_cards_grid(item_list, cols=2):
    for i in range(0, len(item_list), cols):
        row_items = item_list[i:i+cols]
        columns = st.columns(cols)
        for index, item in enumerate(row_items):
            with columns[index]:
                st.link_button(label=f"{item.get('icon', '➡️')}  {item['label']}", url=item['link'], use_container_width=True)

# --- ADMIN PANEL ---

def get_admin_password():
    # Tenta pegar dos secrets, senão usa um padrão seguro ou vazio
    try:
        return st.secrets["admin_password"]
    except:
        return "admin_local" # Apenas para teste local sem secrets

def admin_sidebar():
    st.sidebar.header("🔒 Área da Coordenação")
    
    # Verifica conexão
    client = get_gspread_client()
    status_icon = "🟢" if client else "🔴"
    status_msg = "Online (Google Sheets)" if client else "Offline (Backup Local)"
    st.sidebar.caption(f"Status do Banco de Dados: {status_icon} {status_msg}")

    password = st.sidebar.text_input("Senha de Acesso", type="password")
    
    # Pega a senha real dos Secrets
    REAL_PASSWORD = get_admin_password()
    
    if password == REAL_PASSWORD:
        st.sidebar.success("Acesso Concedido")
        st.sidebar.markdown("---")
        
        action = st.sidebar.radio("Ação:", ["Adicionar Link", "Remover Link", "Nova Categoria", "Remover Categoria"])
        tab_choice = st.sidebar.selectbox("Selecionar Aba:", ["Coordenação", "Cronogramas", "Gestão de Turmas"])
        
        db_key = ""
        if tab_choice == "Coordenação": db_key = "coordenacao"
        elif tab_choice == "Cronogramas": db_key = "cronogramas"
        elif tab_choice == "Gestão de Turmas": db_key = "turmas"
        
        # --- ADD LINK ---
        if action == "Adicionar Link":
            with st.sidebar.form("add"):
                label = st.text_input("Nome")
                link = st.text_input("Link")
                cat = st.selectbox("Categoria", list(db_data[db_key].keys())) if db_key != "coordenacao" else None
                
                if st.form_submit_button("Salvar"):
                    if not client:
                        st.error("Erro: Não é possível salvar sem conexão com Google Sheets.")
                    else:
                        item = {"label": label, "link": link}
                        if db_key == "coordenacao": 
                            item["icon"] = "📌"
                            db_data[db_key].append(item)
                        else: 
                            db_data[db_key][cat].append(item)
                        save_data_to_sheet(db_data)
                        st.rerun()
        
        # --- REMOVE LINK ---
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

        # --- NOVA CATEGORIA ---
        elif action == "Nova Categoria" and db_key != "coordenacao":
             new_c = st.sidebar.text_input("Nova Categoria")
             if st.sidebar.button("Criar"):
                 if new_c not in db_data[db_key]:
                     db_data[db_key][new_c] = []
                     save_data_to_sheet(db_data)
                     st.rerun()

        # --- REMOVER CATEGORIA ---
        elif action == "Remover Categoria" and db_key != "coordenacao":
            del_c = st.sidebar.selectbox("Apagar Categoria", list(db_data[db_key].keys()))
            if st.sidebar.button("Apagar Tudo"):
                del db_data[db_key][del_c]
                save_data_to_sheet(db_data)
                st.rerun()

# --- ESTILOS VISUAIS (MANTENDO O SEU) ---
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

# --- MAIN RENDER ---
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
    st.markdown("<div style='text-align: center; color: gray; font-size: 0.8em;'>© 2026 SENAI HUB • GeEdu v2.0 Cloud</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()