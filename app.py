import streamlit as st
import os
import base64
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json


# ============================================================
# CONFIGURAÇÃO INICIAL
# ============================================================

st.set_page_config(
    page_title="Gestão Educacional",
    page_icon="logo.png",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ============================================================
# NAVEGAÇÃO
# ============================================================

if "active_page" not in st.session_state:
    st.session_state.active_page = "Coordenação Pedagógica"


def change_page(page):
    st.session_state.active_page = page
    st.rerun()


# ============================================================
# CONFIGURAÇÕES DE SEGURANÇA
# ============================================================

SHEET_NAME = "DB_GESTAO_EDUCACIONAL"


# ============================================================
# DADOS PADRÃO — COORDENAÇÃO
# ============================================================

DEFAULT_COORDENACAO = [
    {
        "label": "Ensalamento de Turmas",
        "link": "https://ensalamento-senai-gyf6eeutqqgmnvbab8zffj.streamlit.app/",
        "icon": "⏰"
    },
    {
        "label": "Cronograma Avaliação",
        "link": "https://docs.google.com/spreadsheets/d/10dOuco0yMCS201FnidWxq-BWgbNyTUhxxLNfs82H0t8/edit?gid=2119349890#gid=2119349890",
        "icon": "📊"
    },
    {
        "label": "Fechamento da Produção",
        "link": "https://docs.google.com/spreadsheets/d/14Lavd7aK2-bgAkCbe3xbdvBhnJvcIWXl/edit?gid=1532317622#gid=1532317622",
        "icon": "🔒"
    },
    {
        "label": "Recuperação Aprendizagem",
        "link": "https://docs.google.com/spreadsheets/d/1RlttoeaV4p_76AVWIo0-nG4W9ATPX3BF/edit#gid=784543561",
        "icon": "🎣"
    },
    {
        "label": "Tutoriais SGE",
        "link": "https://drive.google.com/drive/folders/1Ix3EZXUIyjR7F1X8NOWvvuWzrDyPwx99?usp=sharing",
        "icon": "🎥"
    },
    {
        "label": "Empresas Parceiras",
        "link": "https://docs.google.com/spreadsheets/d/1hzjvp4Hd29m59ow5SMrLlGJgamolZHYYDjstX-0xsBA/edit?pli=1&gid=102579484#gid=102579484",
        "icon": "⚙️"
    },
    {
        "label": "Bibliotech",
        "link": "https://bibliotechac.my.canva.site/",
        "icon": "🖥️"
    },
    {
        "label": "Contatos Escolas",
        "link": "https://docs.google.com/spreadsheets/d/1P4mU13bzJyvSASzuWpTFqecgyXlcJJ15/edit?gid=774781193#gid=774781193",
        "icon": "☎️"
    },
    {
        "label": "Cronograma Transversais",
        "link": "https://docs.google.com/spreadsheets/d/1fpki5rZmV63Hgo7k4dAIOWXhjcaPZ4x0/edit?pli=1&gid=271390469#gid=271390469",
        "icon": "📅"
    },
    {
        "label": "QTD Núcleo de Educação",
        "link": "https://docs.google.com/spreadsheets/d/1QXfS3_94f1-0PvVfCQdamaUHTFs1syoNSI4_kwhk62k/edit?gid=0#gid=0",
        "icon": "👩🏻‍🏫"
    },
    {
        "label": "Planejamento - ANAC",
        "link": "https://docs.google.com/spreadsheets/d/1cAapwvzyNMSglMJm6hC2eGphOI9QRUzo/edit?gid=514078859#gid=514078859",
        "icon": "🗃️"
    },
    {
        "label": "Planilha de Pagamento",
        "link": "https://sistemafieac.sharepoint.com/:x:/r/sites/intranetdosistemafieac001/_layouts/15/Doc.aspx?sourcedoc=%7B92129285-B585-4495-B4AC-BF728C457514%7D&file=Prestadores%20de%20Servi%C3%A7os%20-%20(GERAL).xlsx&action=default&mobileredirect=true",
        "icon": "💰"
    },
    {
        "label": "Frequência Empresa - APz 2025",
        "link": "https://docs.google.com/spreadsheets/d/1IleRhu3KXXnt5zONpSoMmWof8jHb_2t2/edit?gid=1807407531#gid=1807407531",
        "icon": "🏭"
    },
    {
        "label": "HOSHIM - SAEP 2025",
        "link": "https://docs.google.com/spreadsheets/d/1rtV7iXsYdvdkxEbjMCgwBfDnmrvWVu-c5-XAbk3Dvz8/edit?gid=99817763#gid=99817763",
        "icon": "🟣"
    },
]


# ============================================================
# DADOS PADRÃO — CRONOGRAMAS
# ============================================================

DEFAULT_CRONOGRAMAS = {

    "FIC's (NEM)": [
        {
            "label": "TRILHA GESTÃO (2024-2025)",
            "link": "https://docs.google.com/spreadsheets/d/1vX35JOwsYnmFEOacJNPijK3q1OLfXiZ6/edit?gid=1416920738#gid=1416920738"
        },
        {
            "label": "TRILHA LOGÍSTICA (2025) - 1º ANO",
            "link": "https://docs.google.com/spreadsheets/d/1vX35JOwsYnmFEOacJNPijK3q1OLfXiZ6/edit?gid=1153727922#gid=1153727922"
        },
        {
            "label": "TRILHA LOGÍSTICA (2025) - 2º ANO",
            "link": "https://docs.google.com/spreadsheets/d/1vX35JOwsYnmFEOacJNPijK3q1OLfXiZ6/edit?gid=1997386750#gid=1997386750"
        },
        {
            "label": "TRILHA ENERGIAS (2025) - 2º ANO",
            "link": "https://docs.google.com/spreadsheets/d/1vX35JOwsYnmFEOacJNPijK3q1OLfXiZ6/edit?gid=502963705#gid=502963705"
        },
        {
            "label": "BUSCA ATIVA (NEM 2025)",
            "link": "https://docs.google.com/spreadsheets/d/1ZRnywoSl-FBlE-iYeu8AZZJNdJKZ3EeVLm_ShHQlR_M/edit?gid=1029141777#gid=1029141777"
        },
    ],

    "TÉCNICOS NEM": [
        {
            "label": "ELETROTÉCNICA (2023-2025)",
            "link": "https://docs.google.com/spreadsheets/d/15xyt51ttXsHLMRctXAWgYlzdCAJEa39s/edit#gid=435143336"
        },
        {
            "label": "TÉC. EM SEGURANÇA (2023-2025)",
            "link": "https://docs.google.com/spreadsheets/d/15xyt51ttXsHLMRctXAWgYlzdCAJEa39s/edit#gid=1859341809#gid=1859341809"
        },
        {
            "label": "ENERGIA RENOVÁVEL (2024-2026)",
            "link": "https://docs.google.com/spreadsheets/d/15xyt51ttXsHLMRctXAWgYlzdCAJEa39s/edit#gid=1848588354#gid=1848588354"
        },
        {
            "label": "BUSCA ATIVA (NEM 2023-2026)",
            "link": "https://docs.google.com/spreadsheets/d/1IjSLQkJ1s2nNDPgrqeqWPdiK_WGIniA7/edit?gid=703051653#gid=703051653"
        },
    ],

    "FIC's (SENAI)  ": [
        {
            "label": "APERFEIÇOAMENTO PROFISSIONAL",
            "link": "https://docs.google.com/spreadsheets/d/1vX35JOwsYnmFEOacJNPijK3q1OLfXiZ6/edit?gid=1354816975#gid=1354816975"
        },
        {
            "label": "QUALIFICAÇÃO PROFISSIONAL",
            "link": "https://docs.google.com/spreadsheets/d/1vX35JOwsYnmFEOacJNPijK3q1OLfXiZ6/edit?gid=601664707#gid=601664707"
        },
        {
            "label": "Busca Ativa (2025)",
            "link": "#"
        },
    ],

    "Técnicos SENAI": [
        {
            "label": "TÉC. EM SEGURANÇA - EAD (2023-2025)",
            "link": "https://docs.google.com/spreadsheets/d/1kyoLq4OjsAfvLVNHeKb7ZmsU2XYg6nrG/edit?gid=1925712139#gid=1925712139"
        },
        {
            "label": "TÉC. ELETROTÉCNICA (2025-2027)",
            "link": "https://docs.google.com/spreadsheets/d/1vX35JOwsYnmFEOacJNPijK3q1OLfXiZ6/edit?gid=624513768#gid=624513768"
        },
    ],

    "Aprendizagem": [
        {
            "label": "PROCESSOS LOGÍSTICOS - 2025",
            "link": "#"
        },
        {
            "label": "GESTÃO INDUSTRIAL - 2025",
            "link": "#"
        },
        {
            "label": "PROGRAMA EDIFICAÇÕES - 2025",
            "link": "https://docs.google.com/spreadsheets/d/1vX35JOwsYnmFEOacJNPijK3q1OLfXiZ6/edit?gid=1795228939#gid=1795228939"
        },
        {
            "label": "BUSCA ATIVA (2025)",
            "link": "https://docs.google.com/spreadsheets/d/1EegVLYMhoJzrO5jizmaZCH6gbjpS15jf/edit?gid=1368374156#gid=1368374156"
        },
    ],

    "BACKUP": [
        {
            "label": "BACKUP 2024",
            "link": "https://drive.google.com/drive/folders/1DO2T2gg2WV9B-s4ZrqzkgJTnqrPSuIp0"
        },
        {
            "label": "BACKUP 2025",
            "link": "#"
        },
    ]
}


# ============================================================
# DADOS PADRÃO — GESTÃO DE TURMAS
# ============================================================

DEFAULT_TURMAS = {

    "FIC'S (NEM) 2024": [
        {
            "label": "GESTÃO A  MANHÃ (2024)",
            "link": "https://docs.google.com/spreadsheets/d/1SiCncHnELxcCs2X5OKKVmhvDnlAgWxyLlF7lBB7dRAM/edit#gid=0"
        },
        {
            "label": "GESTÃO A  TARDE (2024)",
            "link": "https://docs.google.com/spreadsheets/d/1SiCncHnELxcCs2X5OKKVmhvDnlAgWxyLlF7lBB7dRAM/edit#gid=697238086"
        },
        {
            "label": "GESTÃO B  TARDE (2024)",
            "link": "https://docs.google.com/spreadsheets/d/1SiCncHnELxcCs2X5OKKVmhvDnlAgWxyLlF7lBB7dRAM/edit#gid=1124027835"
        },
    ],

    "FIC'S (NEM) 2025": [
        {
            "label": "TRILHA LOGÍSTICA - 1 MANHÃ (1º ANO)",
            "link": "https://docs.google.com/spreadsheets/d/1SiCncHnELxcCs2X5OKKVmhvDnlAgWxyLlF7lBB7dRAM/edit?gid=389234120#gid=389234120"
        },
        {
            "label": "TRILHA LOGÍSTICA - 2 TARDE (1º ANO)",
            "link": "https://docs.google.com/spreadsheets/d/1029141777#gid=1029141777"
        },
        {
            "label": "TRILHA LOGÍSTICA - 3 TARDE (1º ANO)",
            "link": "https://docs.google.com/spreadsheets/d/603235616#gid=603235616"
        },
        {
            "label": "TRILHA LOGÍSTICA - 4 TARDE (1º ANO)",
            "link": "https://docs.google.com/spreadsheets/d/417445561#gid=417445561"
        },
        {
            "label": "TRILHA LOGÍSTICA - 5 MANHÃ (2º ANO)",
            "link": "https://docs.google.com/spreadsheets/d/155259147#gid=155259147"
        },
        {
            "label": "TRILHA LOGÍSTICA - 6 TARDE (2º ANO)",
            "link": "https://docs.google.com/spreadsheets/d/924723208#gid=924723208"
        },
        {
            "label": "TRILHA LOGÍSTICA - 7 TARDE (2º ANO)",
            "link": "https://docs.google.com/spreadsheets/d/1285656207#gid=1285656207"
        },
        {
            "label": "TRILHA ENERGIAS - MANHÃ (2º ANO)",
            "link": "https://docs.google.com/spreadsheets/d/1622990027#gid=1622990027"
        },
    ],

    "TÉCNICOS NEM": [
        {
            "label": "TÉCNICO EM ELETROTÉCNICA (2023-2025)",
            "link": "https://docs.google.com/spreadsheets/d/15xyt51ttXsHLMRctXAWgYlzdCAJEa39s/edit#gid=435143336"
        },
        {
            "label": "TÉCNICO EM SEGURANÇA (2023-2025)",
            "link": "https://docs.google.com/spreadsheets/d/15xyt51ttXsHLMRctXAWgYlzdCAJEa39s/edit#gid=868615014"
        },
        {
            "label": "TÉCNICO EM ENERGIA RENOVÁVEL (2024-2026)",
            "link": "https://docs.google.com/spreadsheets/d/15xyt51ttXsHLMRctXAWgYlzdCAJEa39s/edit#gid=957305393"
        },
    ],

    "TÉCNICOS SENAI": [
        {
            "label": "TÉCNICO EM SEGURANÇA - EAD (2023-2025)",
            "link": "https://docs.google.com/spreadsheets/d/1kyoLq4OjsAfvLVNHeKb7ZmsU2XYg6nrG/edit?gid=307972768#gid=307972768"
        },
    ],

    "FIC'S (SENAI)": [
        {
            "label": "FREQUÊNCIAS FIC'S 2025",
            "link": "https://docs.google.com/spreadsheets/d/1l155mknMTu-6lzLb2OnGFHszqile8MI6GmH8-Cu4AK0/edit?gid=1356514585#gid=1356514585"
        },
    ],

    "APRENDIZAGEM (2025)": [
        {
            "label": "GESTÃO INDUSTRIAL 1 - MANHÃ",
            "link": "https://docs.google.com/spreadsheets/d/1lnLTVwv8dGuo9NGHOHaktLF6HVLW4i9KCsT5ttwhcwk/edit?gid=1484510770#gid=1484510770"
        },
        {
            "label": "GESTÃO INDUSTRIAL 2 - MANHÃ",
            "link": "https://docs.google.com/spreadsheets/d/1lnLTVwv8dGuo9NGHOHaktLF6HVLW4i9KCsT5ttwhcwk/edit?gid=1398337132#gid=1398337132"
        },
        {
            "label": "GESTÃO INDUSTRIAL 3 - TARDE",
            "link": "https://docs.google.com/spreadsheets/d/1806022898#gid=1806022898"
        },
        {
            "label": "GESTÃO INDUSTRIAL 4 - TARDE",
            "link": "https://docs.google.com/spreadsheets/d/298475697#gid=298475697"
        },
        {
            "label": "GESTÃO INDUSTRIAL 5 - TARDE",
            "link": "https://docs.google.com/spreadsheets/d/1375636971#gid=1375636971"
        },
        {
            "label": "OPERAÇÕES LOGÍSTICAS 1 - MANHÃ",
            "link": "https://docs.google.com/spreadsheets/d/309880873#gid=309880873"
        },
        {
            "label": "OPERAÇÕES LOGÍSTICAS 2 - MANHÃ",
            "link": "https://docs.google.com/spreadsheets/d/1886911715#gid=1886911715"
        },
        {
            "label": "OPERAÇÕES LOGÍSTICAS 3 - TARDE",
            "link": "https://docs.google.com/spreadsheets/d/1069851690#gid=1069851690"
        },
        {
            "label": "PROGRAMA DE EDIFICAÇÕES",
            "link": "https://docs.google.com/spreadsheets/d/583575371#gid=583575371"
        },
        {
            "label": "PROGRAMA DE GESTÃO C - MANHÃ",
            "link": "#"
        },
        {
            "label": "PROGRAMA DE GESTÃO C - TARDE",
            "link": "#"
        },
        {
            "label": "LOGÍSTICA MERCALE - TARDE",
            "link": "#"
        },
    ]
}


# ============================================================
# ACESSO SEGURO AOS SECRETS
# ============================================================

def get_streamlit_secrets():
    """
    Retorna st.secrets quando existe um secrets.toml válido.
    Em execução local sem secrets.toml, retorna um dicionário vazio.
    """
    try:
        return st.secrets
    except Exception:
        return {}


# ============================================================
# GOOGLE SHEETS — CONEXÃO
# ============================================================


@st.cache_resource
def get_gspread_client():

    secrets = get_streamlit_secrets()

    if "gcp_service_account" not in secrets:
        return None

    try:

        service_account = secrets["gcp_service_account"]

        if "json_content" in service_account:

            creds_dict = json.loads(
                service_account["json_content"],
                strict=False
            )

        else:

            creds_dict = dict(service_account)

            if "private_key" in creds_dict:
                creds_dict["private_key"] = (
                    creds_dict["private_key"]
                    .replace("\\n", "\n")
                )

        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]

        creds = ServiceAccountCredentials.from_json_keyfile_dict(
            creds_dict,
            scope
        )

        return gspread.authorize(creds)

    except Exception:
        return None


# ============================================================
# CARREGAMENTO DOS DADOS
# ============================================================

def load_data_from_sheet():

    client = get_gspread_client()

    if not client:

        return {
            "coordenacao": DEFAULT_COORDENACAO,
            "cronogramas": DEFAULT_CRONOGRAMAS,
            "turmas": DEFAULT_TURMAS
        }

    try:

        sheet = client.open(SHEET_NAME).sheet1
        records = sheet.get_all_records()

        if not records:

            default_data = {
                "coordenacao": DEFAULT_COORDENACAO,
                "cronogramas": DEFAULT_CRONOGRAMAS,
                "turmas": DEFAULT_TURMAS
            }

            save_data_to_sheet(default_data)

            return default_data

        db = {
            "coordenacao": [],
            "cronogramas": {},
            "turmas": {}
        }

        for row in records:

            if row["LABEL"] == "__EMPTY__":

                cat = row["CATEGORIA"]

                if row["ABA"] == "Cronogramas":

                    if cat not in db["cronogramas"]:
                        db["cronogramas"][cat] = []

                elif row["ABA"] == "Gestão de Turmas":

                    if cat not in db["turmas"]:
                        db["turmas"][cat] = []

                continue

            item = {
                "label": row["LABEL"],
                "link": row["LINK"]
            }

            if row["ICONE"]:
                item["icon"] = row["ICONE"]

            if row["ABA"] == "Coordenação":

                db["coordenacao"].append(item)

            elif row["ABA"] == "Cronogramas":

                cat = row["CATEGORIA"]

                if cat not in db["cronogramas"]:
                    db["cronogramas"][cat] = []

                db["cronogramas"][cat].append(item)

            elif row["ABA"] == "Gestão de Turmas":

                cat = row["CATEGORIA"]

                if cat not in db["turmas"]:
                    db["turmas"][cat] = []

                db["turmas"][cat].append(item)

        return db

    except Exception:

        return {
            "coordenacao": DEFAULT_COORDENACAO,
            "cronogramas": DEFAULT_CRONOGRAMAS,
            "turmas": DEFAULT_TURMAS
        }


# ============================================================
# SALVAMENTO DOS DADOS
# ============================================================

def save_data_to_sheet(data):

    client = get_gspread_client()

    if not client:
        return

    try:

        sheet = client.open(SHEET_NAME).sheet1

        rows = [
            ["ABA", "CATEGORIA", "LABEL", "LINK", "ICONE"]
        ]

        # Coordenação
        for item in data["coordenacao"]:

            rows.append([
                "Coordenação",
                "Geral",
                item["label"],
                item["link"],
                item.get("icon", "")
            ])

        # Cronogramas
        for cat, items in data["cronogramas"].items():

            if not items:

                rows.append([
                    "Cronogramas",
                    cat,
                    "__EMPTY__",
                    "",
                    ""
                ])

            else:

                for item in items:

                    rows.append([
                        "Cronogramas",
                        cat,
                        item["label"],
                        item["link"],
                        ""
                    ])

        # Gestão de Turmas
        for cat, items in data["turmas"].items():

            if not items:

                rows.append([
                    "Gestão de Turmas",
                    cat,
                    "__EMPTY__",
                    "",
                    ""
                ])

            else:

                for item in items:

                    rows.append([
                        "Gestão de Turmas",
                        cat,
                        item["label"],
                        item["link"],
                        ""
                    ])

        sheet.clear()
        sheet.update(rows)

    except Exception:
        pass


# ============================================================
# ESTILIZAÇÃO PROFISSIONAL
# ============================================================

st.markdown(
    """
    <style>

    /* O Streamlit controla o tema geral.
       Este CSS não força fundo claro/escuro. */

    :root {
        --primary: #0046ad;
        --primary-hover: #003b91;
        --card-border: rgba(128, 128, 128, 0.28);
        --shadow: rgba(0, 0, 0, 0.08);
    }

    .block-container {
        padding-top: 1.4rem;
        padding-bottom: 2rem;
        max-width: 1500px;
    }

    .main-header {
        text-align: center;
        margin-bottom: 1.5rem;
    }

    .main-header h1 {
        color: var(--primary);
        font-weight: 800;
        font-size: 2.2rem;
        margin: 0;
        letter-spacing: -0.5px;
        text-transform: uppercase;
    }

    .logo-wrapper {
        display: flex;
        justify-content: center;
        margin-bottom: 0.6rem;
    }

    .logo-wrapper img {
        max-width: 260px;
        width: 100%;
        height: auto;
        object-fit: contain;
    }

    .navigation-wrapper {
        width: 100%;
        margin: 0 auto 1.8rem auto;
    }

    div[data-testid="stButton"] > button {
        width: 100%;
        min-height: 3rem;
        border-radius: 9px;
        border: 1px solid var(--card-border);
        background-color: transparent;
        color: inherit;
        font-size: 14px;
        font-weight: 700;
        transition:
            background-color 0.15s ease,
            border-color 0.15s ease,
            transform 0.15s ease,
            box-shadow 0.15s ease;
    }

    div[data-testid="stButton"] > button:hover {
        border-color: var(--primary);
        background-color: rgba(128, 128, 128, 0.08);
        color: var(--primary);
        transform: translateY(-1px);
        box-shadow: 0 3px 10px var(--shadow);
    }

    div[data-testid="stButton"] > button:focus {
        border-color: var(--primary);
        box-shadow: 0 0 0 1px var(--primary);
    }

    div[data-testid="stLinkButton"] > a {
        width: 100% !important;
        min-height: 3.2em !important;
        height: auto !important;
        border-radius: 8px;
        border: 1px solid var(--card-border);
        background-color: transparent;
        color: inherit !important;
        text-decoration: none !important;
        transition:
            background-color 0.18s ease,
            border-color 0.18s ease,
            transform 0.18s ease,
            box-shadow 0.18s ease;
        display: flex !important;
        align-items: center !important;
        justify-content: flex-start !important;
        padding: 0.4rem 12px !important;
        font-size: 13.5px !important;
        line-height: 1.25 !important;
        white-space: normal !important;
    }

    div[data-testid="stLinkButton"] > a > div {
        justify-content: flex-start !important;
        text-align: left !important;
        width: 100%;
        color: inherit !important;
    }

    div[data-testid="stLinkButton"] > a:hover {
        border-color: var(--primary);
        background-color: rgba(128, 128, 128, 0.08);
        transform: translateY(-1px);
        box-shadow: 0 3px 8px var(--shadow);
        color: var(--primary) !important;
    }

    div[data-testid="stLinkButton"] > a:hover > div {
        color: var(--primary) !important;
    }

    .category-title {
        color: var(--primary);
        font-size: 0.95rem;
        font-weight: 700;
        margin-bottom: 8px;
        border-bottom: 1px solid var(--card-border);
        padding-bottom: 5px;
        margin-top: 15px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    [data-testid="stSidebar"] {
        border-right: 1px solid var(--card-border);
    }

    .app-footer {
        text-align: center;
        opacity: 0.65;
        font-size: 0.8em;
        padding: 0.4rem 0;
    }

    @media (max-width: 768px) {
        .logo-wrapper img {
            max-width: 180px;
        }

        .main-header h1 {
            font-size: 1.65rem;
        }

        div[data-testid="stButton"] > button {
            min-height: 2.8rem;
            font-size: 13px;
        }
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# CARREGA DADOS
# ============================================================

db_data = load_data_from_sheet()


# ============================================================
# VISUAL — CABEÇALHO
# ============================================================

def render_header():

    c_left, c_center, c_right = st.columns([1, 2, 1])

    with c_center:

        if os.path.exists("logo.png"):

            with open("logo.png", "rb") as img_file:

                img_base64 = base64.b64encode(
                    img_file.read()
                ).decode()

            st.markdown(
                f"""
                <div class="logo-wrapper">
                    <img src="data:image/png;base64,{img_base64}">
                </div>
                """,
                unsafe_allow_html=True
            )

        else:

            st.markdown(
                """
                <div class="logo-wrapper">
                    <strong>GESTÃO EDUCACIONAL</strong>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.markdown(
            """
            <div class="main-header">
                <h1>Gestão Educacional</h1>
            </div>
            """,
            unsafe_allow_html=True
        )


# ============================================================
# GRID DE CARDS
# ============================================================

def render_cards_grid(item_list, cols=2):

    if not item_list:

        st.info("Nenhum item disponível nesta categoria.")

        return

    for i in range(0, len(item_list), cols):

        row_items = item_list[i:i + cols]

        columns = st.columns(
            cols,
            gap="medium"
        )

        for index, item in enumerate(row_items):

            with columns[index]:

                st.link_button(
                    label=f"{item.get('icon', '➡️')}  {item['label']}",
                    url=item["link"],
                    use_container_width=True
                )


# ============================================================
# NAVEGAÇÃO PRINCIPAL
# ============================================================

def render_navigation():

    pages = [
        (
            "Coordenação Pedagógica",
            "Coordenação Pedagógica"
        ),
        (
            "Cronogramas",
            "Cronogramas"
        ),
        (
            "Gestão de Turmas",
            "Gestão de Turmas"
        )
    ]

    st.markdown(
        '<div class="navigation-wrapper">',
        unsafe_allow_html=True
    )

    columns = st.columns(
        len(pages),
        gap="medium"
    )

    for index, (page_key, label) in enumerate(pages):

        with columns[index]:

            # Mantemos o estado na memória da sessão.
            # Ao clicar, apenas uma página passa a ser renderizada.

            if st.button(
                label,
                key=f"navigation_{index}",
                use_container_width=True
            ):

                change_page(page_key)

    st.markdown(
        '</div>',
        unsafe_allow_html=True
    )


# ============================================================
# ÁREA ADMINISTRATIVA
# ============================================================

def admin_sidebar():

    st.sidebar.markdown("### 🔒 Área da Coordenação")

    # Mantém o comportamento original:
    # se não existir senha nem conta Google configurada,
    # a área administrativa não é exibida.

    secrets = get_streamlit_secrets()

    if (
        "admin_password" not in secrets
        and
        "gcp_service_account" not in secrets
    ):
        return

    password = st.sidebar.text_input(
        "Senha de Acesso",
        type="password"
    )

    if (
        "admin_password" in secrets
        and
        password == secrets["admin_password"]
    ):

        st.sidebar.success(
            "Conectado ao Banco de Dados"
        )

        st.sidebar.markdown("---")

        action = st.sidebar.radio(
            "Ação:",
            [
                "Adicionar Link",
                "Remover Link",
                "Nova Categoria",
                "Remover Categoria"
            ]
        )

        tab_choice = st.sidebar.selectbox(
            "Selecionar Aba:",
            [
                "Coordenação",
                "Cronogramas",
                "Gestão de Turmas"
            ]
        )

        db_key = ""

        if tab_choice == "Coordenação":
            db_key = "coordenacao"

        elif tab_choice == "Cronogramas":
            db_key = "cronogramas"

        elif tab_choice == "Gestão de Turmas":
            db_key = "turmas"


        # ====================================================
        # ADICIONAR LINK
        # ====================================================

        if action == "Adicionar Link":

            with st.sidebar.form("add"):

                label = st.text_input("Nome")

                link = st.text_input("Link")

                if db_key != "coordenacao":

                    categories = list(
                        db_data[db_key].keys()
                    )

                    cat = st.selectbox(
                        "Categoria",
                        categories
                    ) if categories else None

                else:

                    cat = None

                if st.form_submit_button("Salvar"):

                    if not label.strip():

                        st.sidebar.warning(
                            "Informe o nome do link."
                        )

                    elif not link.strip():

                        st.sidebar.warning(
                            "Informe o endereço do link."
                        )

                    elif (
                        db_key != "coordenacao"
                        and
                        cat is None
                    ):

                        st.sidebar.warning(
                            "Crie uma categoria antes de adicionar o link."
                        )

                    else:

                        item = {
                            "label": label.strip(),
                            "link": link.strip()
                        }

                        if db_key == "coordenacao":

                            item["icon"] = "📌"

                            db_data[db_key].append(
                                item
                            )

                        else:

                            db_data[db_key][cat].append(
                                item
                            )

                        save_data_to_sheet(
                            db_data
                        )

                        st.rerun()


        # ====================================================
        # REMOVER LINK
        # ====================================================

        elif action == "Remover Link":

            if db_key == "coordenacao":

                opts = [
                    x["label"]
                    for x in db_data[db_key]
                ]

                if opts:

                    delt = st.sidebar.selectbox(
                        "Remover",
                        opts
                    )

                    if st.sidebar.button(
                        "Confirmar",
                        key="confirm_remove_coord"
                    ):

                        db_data[db_key] = [
                            x
                            for x in db_data[db_key]
                            if x["label"] != delt
                        ]

                        save_data_to_sheet(
                            db_data
                        )

                        st.rerun()

                else:

                    st.sidebar.info(
                        "Nenhum link disponível."
                    )

            else:

                categories = list(
                    db_data[db_key].keys()
                )

                if categories:

                    cat = st.sidebar.selectbox(
                        "Categoria",
                        categories,
                        key="remove_category_select"
                    )

                    opts = [
                        x["label"]
                        for x in db_data[db_key][cat]
                    ]

                    if opts:

                        delt = st.sidebar.selectbox(
                            "Remover",
                            opts,
                            key="remove_link_select"
                        )

                        if st.sidebar.button(
                            "Confirmar",
                            key="confirm_remove_link"
                        ):

                            db_data[db_key][cat] = [
                                x
                                for x in db_data[db_key][cat]
                                if x["label"] != delt
                            ]

                            save_data_to_sheet(
                                db_data
                            )

                            st.rerun()

                    else:

                        st.sidebar.info(
                            "Nenhum link disponível nesta categoria."
                        )

                else:

                    st.sidebar.info(
                        "Nenhuma categoria disponível."
                    )


        # ====================================================
        # NOVA CATEGORIA
        # ====================================================

        if (
            action == "Nova Categoria"
            and
            db_key != "coordenacao"
        ):

            new_c = st.sidebar.text_input(
                "Nova Categoria"
            )

            if st.sidebar.button(
                "Criar",
                key="create_category"
            ):

                new_c = new_c.strip()

                if not new_c:

                    st.sidebar.warning(
                        "Informe o nome da categoria."
                    )

                elif new_c in db_data[db_key]:

                    st.sidebar.warning(
                        "Essa categoria já existe."
                    )

                else:

                    db_data[db_key][new_c] = []

                    save_data_to_sheet(
                        db_data
                    )

                    st.rerun()


        # ====================================================
        # REMOVER CATEGORIA
        # ====================================================

        if (
            action == "Remover Categoria"
            and
            db_key != "coordenacao"
        ):

            categories = list(
                db_data[db_key].keys()
            )

            if categories:

                del_c = st.sidebar.selectbox(
                    "Apagar Categoria",
                    categories
                )

                if st.sidebar.button(
                    "Apagar Tudo",
                    key="delete_category"
                ):

                    del db_data[db_key][del_c]

                    save_data_to_sheet(
                        db_data
                    )

                    st.rerun()

            else:

                st.sidebar.info(
                    "Nenhuma categoria disponível."
                )


# ============================================================
# PÁGINA — COORDENAÇÃO PEDAGÓGICA
# ============================================================

def render_coordenacao():

    s1, c, s2 = st.columns(
        [1, 3, 1]
    )

    with c:

        st.markdown(
            "<br>",
            unsafe_allow_html=True
        )

        render_cards_grid(
            db_data["coordenacao"],
            cols=2
        )


# ============================================================
# PÁGINA — CRONOGRAMAS
# ============================================================

def render_cronogramas():

    s1, c, s2 = st.columns(
        [0.5, 10, 0.5]
    )

    with c:

        st.markdown(
            "<br>",
            unsafe_allow_html=True
        )

        columns = st.columns(
            3,
            gap="medium"
        )

        items = list(
            db_data["cronogramas"].items()
        )

        # Coluna 1
        with columns[0]:

            for k, v in items[0::3]:

                st.markdown(
                    f"""
                    <div class="category-title">
                        📂 {k}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                render_cards_grid(
                    v,
                    cols=1
                )

                st.markdown(
                    "<br>",
                    unsafe_allow_html=True
                )

        # Coluna 2
        with columns[1]:

            for k, v in items[1::3]:

                st.markdown(
                    f"""
                    <div class="category-title">
                        📂 {k}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                render_cards_grid(
                    v,
                    cols=1
                )

                st.markdown(
                    "<br>",
                    unsafe_allow_html=True
                )

        # Coluna 3
        with columns[2]:

            for k, v in items[2::3]:

                st.markdown(
                    f"""
                    <div class="category-title">
                        📂 {k}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                render_cards_grid(
                    v,
                    cols=1
                )

                st.markdown(
                    "<br>",
                    unsafe_allow_html=True
                )


# ============================================================
# PÁGINA — GESTÃO DE TURMAS
# ============================================================

def render_turmas():

    s1, c, s2 = st.columns(
        [0.5, 10, 0.5]
    )

    with c:

        st.markdown(
            "<br>",
            unsafe_allow_html=True
        )

        columns = st.columns(
            3,
            gap="medium"
        )

        items = list(
            db_data["turmas"].items()
        )

        # Coluna 1
        with columns[0]:

            for k, v in items[0::3]:

                st.markdown(
                    f"""
                    <div class="category-title">
                        📂 {k}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                render_cards_grid(
                    v,
                    cols=1
                )

                st.markdown(
                    "<br>",
                    unsafe_allow_html=True
                )

        # Coluna 2
        with columns[1]:

            for k, v in items[1::3]:

                st.markdown(
                    f"""
                    <div class="category-title">
                        📂 {k}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                render_cards_grid(
                    v,
                    cols=1
                )

                st.markdown(
                    "<br>",
                    unsafe_allow_html=True
                )

        # Coluna 3
        with columns[2]:

            for k, v in items[2::3]:

                st.markdown(
                    f"""
                    <div class="category-title">
                        📂 {k}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                render_cards_grid(
                    v,
                    cols=1
                )

                st.markdown(
                    "<br>",
                    unsafe_allow_html=True
                )


# ============================================================
# RODAPÉ
# ============================================================

def render_footer():

    st.markdown("---")

    st.markdown(
        """
        <div class="app-footer">
            © 2026 SENAI HUB • GeEdu Cloud v1.0
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# MAIN
# ============================================================

def main():

    # Área administrativa
    admin_sidebar()

    # Cabeçalho
    render_header()

    # Menu próprio — substitui completamente o st.tabs()
    render_navigation()

    # ========================================================
    # RENDERIZAÇÃO EXCLUSIVA
    #
    # Somente UMA dessas funções é executada por vez.
    # ========================================================

    if st.session_state.active_page == "Coordenação Pedagógica":

        render_coordenacao()

    elif st.session_state.active_page == "Cronogramas":

        render_cronogramas()

    elif st.session_state.active_page == "Gestão de Turmas":

        render_turmas()

    # Rodapé
    render_footer()


# ============================================================
# EXECUÇÃO
# ============================================================

if __name__ == "__main__":
    main()