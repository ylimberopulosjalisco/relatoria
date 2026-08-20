
import io
import re
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

try:
    from supabase import create_client
except Exception:
    create_client = None


# ==========================================================
# RELATORÍA COINVIERTE — OTRA BARRERA Y OTRO ACTOR SIEMPRE HABILITADOS
# ==========================================================

st.set_page_config(
    page_title="Relatoría | Economía Circular Jalisco",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Paleta ----------
INK = "#173B2E"
INK_2 = "#285843"
SAGE = "#DCEBCB"
SAGE_2 = "#EEF5E8"
MINT = "#EAF4F1"
AQUA = "#D9EFF1"
AQUA_STRONG = "#3C8791"
SAND = "#F4E6C8"
CREAM = "#FBFAF5"
WHITE = "#FFFFFF"
BORDER = "#DDE5DA"
TEXT = "#2D3C33"
MUTED = "#6E7B73"
GREEN = "#2F6E4A"
GREEN_DARK = "#24583B"
SHADOW = "rgba(38, 72, 51, 0.08)"

st.markdown(
    f"""
    <style>
    /* ---------- Ocultar chrome superior de Streamlit ---------- */
    header[data-testid="stHeader"] {{
        display: none !important;
        height: 0 !important;
        min-height: 0 !important;
    }}
    [data-testid="stToolbar"],
    [data-testid="stDecoration"],
    [data-testid="stStatusWidget"] {{
        display: none !important;
    }}

    /* ---------- Página ---------- */
    .stApp {{
        background:
            radial-gradient(circle at 75% 0%, rgba(217,239,241,.55), transparent 28%),
            radial-gradient(circle at 8% 100%, rgba(220,235,203,.48), transparent 24%),
            linear-gradient(180deg, #FFFDF9 0%, #FBFCF8 100%);
        color: {TEXT};
    }}
    .block-container {{
        max-width: 1460px;
        padding-top: 0.75rem !important;
        padding-bottom: 2.5rem;
    }}

    h1, h2, h3 {{
        color: {INK};
        letter-spacing: -0.02em;
    }}

    /* ---------- Sidebar ---------- */
    [data-testid="stSidebar"] {{
        background:
            linear-gradient(180deg, rgba(255,253,248,.98), rgba(249,250,244,.98));
        border-right: 1px solid {BORDER};
        position: relative;
        overflow: hidden;
        min-width: 340px !important;
        width: 340px !important;
    }}
    [data-testid="stSidebar"] > div:first-child {{
        width: 340px !important;
    }}
    [data-testid="stSidebar"]::after {{
        content: "";
        position: absolute;
        left: -70px;
        bottom: -90px;
        width: 330px;
        height: 210px;
        background:
            radial-gradient(ellipse at 60% 80%, rgba(60,135,145,.18) 0 32%, transparent 33%),
            radial-gradient(ellipse at 28% 78%, rgba(220,235,203,.95) 0 36%, transparent 37%),
            radial-gradient(ellipse at 5% 80%, rgba(244,230,200,.95) 0 40%, transparent 41%);
        border-radius: 45% 55% 0 0 / 80% 80% 0 0;
        pointer-events: none;
        z-index: 0;
    }}
    [data-testid="stSidebar"] > div {{
        position: relative;
        z-index: 1;
    }}
    [data-testid="stSidebar"] h2 {{
        color: {INK};
        font-weight: 800;
        margin-bottom: .9rem;
    }}
    [data-testid="stSidebar"] label {{
        color: {TEXT} !important;
        font-weight: 650 !important;
    }}
    [data-testid="stSidebar"] .stSelectbox > div > div,
    [data-testid="stSidebar"] .stTextInput input {{
        background: rgba(255,255,255,.95) !important;
        border-color: {BORDER} !important;
        border-radius: 12px !important;
    }}

    /* ---------- Hero ---------- */
    .hero-shell {{
        position: relative;
        background:
            radial-gradient(circle at 88% 5%, rgba(255,255,255,.55), transparent 18%),
            linear-gradient(120deg, #FFFDF7 0%, #FFF9ED 48%, #EFF7F5 100%);
        border: 1px solid rgba(221,229,218,.65);
        border-radius: 28px;
        min-height: 205px;
        padding: 34px 42px 30px 42px;
        overflow: hidden;
        box-shadow: 0 10px 28px {SHADOW};
    }}
    .hero-shell::before {{
        content: "";
        position: absolute;
        right: -120px;
        bottom: -95px;
        width: 520px;
        height: 255px;
        border-radius: 55% 45% 0 0 / 70% 70% 0 0;
        background:
            radial-gradient(ellipse at 65% 80%, rgba(60,135,145,.14) 0 42%, transparent 43%),
            radial-gradient(ellipse at 38% 80%, rgba(220,235,203,.45) 0 49%, transparent 50%);
    }}
    .hero-shell::after {{
        content: "";
        position: absolute;
        right: 76px;
        top: 35px;
        width: 105px;
        height: 105px;
        border: 13px solid rgba(47,110,74,.13);
        border-radius: 50%;
        clip-path: polygon(0 0,100% 0,100% 38%,60% 38%,60% 100%,0 100%);
        transform: rotate(15deg);
        opacity: .85;
    }}
    .hero-title {{
        position: relative;
        z-index: 2;
        color: {INK};
        font-size: 2.45rem;
        font-weight: 850;
        line-height: 1.05;
        margin-bottom: .55rem;
        max-width: 850px;
    }}
    .hero-sub {{
        position: relative;
        z-index: 2;
        color: {TEXT};
        font-size: 1rem;
        max-width: 820px;
        line-height: 1.55;
    }}
    .pill-row {{
        position: relative;
        z-index: 2;
        margin-top: 1.05rem;
    }}
    .soft-pill {{
        display: inline-block;
        margin: 0 .42rem .35rem 0;
        padding: .45rem .8rem;
        border-radius: 999px;
        font-size: .83rem;
        font-weight: 650;
        color: {INK};
    }}
    .pill-sage {{ background: {SAGE}; }}
    .pill-sand {{ background: {SAND}; }}
    .pill-aqua {{ background: {AQUA}; }}

    /* ---------- Franja institucional de logos ---------- */
    .brand-separator {{
        width: 1px;
        height: 48px;
        background: {BORDER};
        margin: 0 auto;
    }}

    /* ---------- Tarjetas ---------- */
    .info-card {{
        background: rgba(255,255,255,.96);
        border: 1px solid {BORDER};
        border-radius: 18px;
        padding: 16px 18px;
        min-height: 98px;
        box-shadow: 0 6px 18px {SHADOW};
        display: flex;
        align-items: center;
        gap: 13px;
    }}
    .info-icon {{
        width: 48px;
        height: 48px;
        border-radius: 50%;
        display:flex;
        align-items:center;
        justify-content:center;
        font-size: 1.35rem;
        flex: 0 0 auto;
    }}
    .icon-sage {{ background: {SAGE}; }}
    .icon-sand {{ background: {SAND}; }}
    .icon-aqua {{ background: {AQUA}; }}
    .info-label {{
        font-size: .72rem;
        letter-spacing: .05em;
        color: {MUTED};
        font-weight: 800;
        text-transform: uppercase;
        margin-bottom: .2rem;
    }}
    .info-value {{
        color: {INK};
        font-size: 1.03rem;
        font-weight: 800;
        line-height: 1.25;
    }}

    /* ---------- Tabs ---------- */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 0.1rem;
        border-bottom: 1px solid {BORDER};
    }}
    .stTabs [data-baseweb="tab"] {{
        height: auto;
        padding: .55rem .95rem;
        background: transparent;
        border-radius: 10px 10px 0 0;
        color: {TEXT};
        font-weight: 650;
    }}
    .stTabs [aria-selected="true"] {{
        color: {INK} !important;
        background: rgba(238,245,232,.7) !important;
        border-bottom: 3px solid {GREEN} !important;
    }}

    /* ---------- Formulario ---------- */
    .rule-note {{
        background: linear-gradient(90deg, rgba(220,235,203,.75), rgba(238,245,232,.72));
        border-radius: 14px;
        padding: 12px 16px;
        margin-bottom: 14px;
        border: 1px solid rgba(221,229,218,.85);
        color: {TEXT};
    }}

    [data-testid="stForm"] {{
        background: rgba(255,255,255,.90);
        border: 1px solid {BORDER};
        border-radius: 20px;
        padding: 16px 18px 18px 18px;
        box-shadow: 0 7px 20px {SHADOW};
    }}
    .stTextArea textarea,
    .stTextInput input,
    .stSelectbox > div > div {{
        background: #FFFDF9 !important;
        border-color: {BORDER} !important;
        border-radius: 12px !important;
    }}

    /* ---------- Botones ---------- */
    div.stButton > button,
    div[data-testid="stFormSubmitButton"] > button {{
        border-radius: 13px !important;
        min-height: 46px;
        font-weight: 750 !important;
    }}
    div[data-testid="stFormSubmitButton"] > button[kind="primary"] {{
        background: linear-gradient(120deg, {GREEN}, {INK_2}) !important;
        color: white !important;
        border: none !important;
    }}
    div[data-testid="stFormSubmitButton"] > button[kind="primary"]:hover {{
        background: linear-gradient(120deg, {GREEN_DARK}, {INK}) !important;
    }}

    /* ---------- Sidebar notes ---------- */
    .sidebar-note {{
        background: linear-gradient(120deg, rgba(234,244,241,.96), rgba(255,255,255,.92));
        border: 1px solid {BORDER};
        border-radius: 14px;
        padding: 13px 14px;
        color: {MUTED};
        line-height: 1.45;
        margin-bottom: .75rem;
    }}
    .sidebar-db {{
        background: linear-gradient(120deg, rgba(220,235,203,.92), rgba(238,245,232,.95));
        border: 1px solid {BORDER};
        border-radius: 14px;
        padding: 13px 14px;
        color: {INK};
        font-weight: 750;
    }}

    /* ---------- Métricas / tablas ---------- */
    div[data-testid="stMetric"] {{
        background: rgba(255,255,255,.96);
        border: 1px solid {BORDER};
        border-radius: 17px;
        padding: 10px 14px;
        box-shadow: 0 6px 18px {SHADOW};
    }}

    /* ---------- Footer ---------- */
    .app-footer {{
        text-align:center;
        color:{MUTED};
        font-size:.82rem;
        margin-top:.8rem;
    }}

    /* ---------- Responsive ---------- */
    @media (max-width: 900px) {{
        .hero-title {{ font-size: 1.75rem; }}
        .hero-shell {{ border-radius: 24px; padding: 22px; }}
        .logo-panel {{ min-height: auto; }}
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"

def buscar_logo(preferidos=None, terminos=None):
    preferidos = preferidos or []
    terminos = terminos or []
    if not ASSETS_DIR.exists():
        return None

    # 1) Buscar por nombres preferidos exactos
    for nombre in preferidos:
        p = ASSETS_DIR / nombre
        if p.exists():
            return p

    # 2) Buscar por términos en nombre de archivo
    for candidate in sorted(ASSETS_DIR.iterdir()):
        if candidate.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}:
            nombre = candidate.name.lower()
            if all(t in nombre for t in terminos):
                return candidate

    # 3) Buscar por cualquier término
    for candidate in sorted(ASSETS_DIR.iterdir()):
        if candidate.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}:
            nombre = candidate.name.lower()
            if any(t in nombre for t in terminos):
                return candidate

    return None

LOGO_COINVIERTE = buscar_logo(
    preferidos=[
        "logo_coinvierte.png",
        "logo_coinvierte.jpg",
        "logo_coinvierte.jpeg",
        "logo_coinvierte.webp",
    ],
    terminos=["coinvierte"]
)

LOGO_TEC = buscar_logo(
    preferidos=[
        "logo_tec_monterrey.png",
        "logo_tec_monterrey.jpg",
        "logo_tec_monterrey.jpeg",
        "logo_tec.png",
        "tec_monterrey.png",
        "tecnologico_de_monterrey.png",
        "tecnologico_de_monterrey.jpg",
    ],
    terminos=["tec", "monterrey"]
)

# Fallback por si el logo del Tec sólo contiene "tec" o "tecnologico"
if LOGO_TEC is None:
    LOGO_TEC = buscar_logo(
        terminos=["tecnologico"]
    ) or buscar_logo(terminos=["tec"])

DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
LOCAL_CSV = DATA_DIR / "relatoria_hallazgos.csv"

MESAS = [
    "Estrategia, gobernanza y capacidades",
    "Operación circular, recursos y cadenas de valor",
    "Innovación, tecnología, inversión y financiamiento",
    "Entorno habilitante, regulación y colaboración",
]

PREGUNTAS_POR_MESA = {
    "Estrategia, gobernanza y capacidades": [
        "Detonadora. Pensando en su organización, ¿en qué medida la economía circular ya forma parte de la manera en que toman decisiones y operan, y en qué medida sigue siendo algo incipiente?",
        "P1. ¿Su organización tiene hoy alguna práctica o iniciativa relacionada con economía circular, aunque sea incipiente o no la llamen así?",
        "P2. Cuando aparece una oportunidad de circularidad, ¿quién puede realmente impulsarla o detenerla dentro de la organización?",
        "P3. ¿Qué les hace falta dentro de la organización para poder avanzar más rápido?",
        "P4. ¿Qué información tendría que llegar a su escritorio para que ustedes dijeran: “sí, vale la pena hacer esta inversión”?",
        "Cierre. Si pudieran fortalecer una sola capacidad interna durante los próximos dos años, ¿cuál tendría mayor impacto?",
    ],
    "Operación circular, recursos y cadenas de valor": [
        "Detonadora. Si recorriéramos hoy su operación completa, ¿en qué parte encontraríamos la mayor pérdida de valor: materiales, residuos, agua, energía, empaques, inventarios o logística?",
        "P1. ¿Qué flujo de recursos consideran que tendría mayor potencial de mejora, aun si todavía no han iniciado acciones para atenderlo?",
        "P2. ¿Qué les impide aprovechar ese material, reducir ese consumo o cerrar ese ciclo actualmente?",
        "P3. ¿Identifican algún residuo o subproducto que potencialmente pudiera aprovechar otra empresa, o algún material externo que ustedes pudieran aprovechar, aunque hoy ese intercambio no exista?",
        "P4. ¿Qué tendría que cambiar en su cadena de proveedores o clientes para que ustedes pudieran ser más circulares?",
        "Cierre. ¿Cuál sería la oportunidad operativa más tangible que podríamos comenzar a resolver en Jalisco?",
    ],
    "Innovación, tecnología, inversión y financiamiento": [
        "Detonadora. ¿Qué problema de su empresa saben que podría resolverse con tecnología o innovación, pero todavía no han podido resolver?",
        "P1. ¿Qué tecnologías o soluciones conocen, han explorado o creen que podrían ser relevantes para avanzar hacia una economía más circular? Si ninguna está hoy en el radar, ¿por qué?",
        "P2. ¿Qué hace que una solución técnicamente viable no termine implementándose?",
        "P3. ¿Qué tendría que demostrar o resolver un proyecto para que su empresa considerara invertir recursos propios, incluso si hoy no existe disposición de inversión?",
        "P4. ¿Qué parte del riesgo tendría que compartir alguien más para que el proyecto ocurriera?",
        "P5. Si el gobierno quisiera ayudar a destrabar estas inversiones, ¿qué sería más útil y por qué?",
        "Cierre. ¿Qué inversión circular creen que hoy no está ocurriendo en Jalisco pero podría ocurrir en los próximos dos o tres años si se elimina la barrera correcta?",
    ],
    "Entorno habilitante, regulación y colaboración": [
        "Detonadora. Pensando fuera de su empresa, ¿cuál es hoy el principal obstáculo del entorno para avanzar hacia una economía circular?",
        "P1. ¿Hay alguna regulación, trámite o falta de claridad regulatoria que esté dificultando una solución circular?",
        "P2. ¿Qué tendría que cambiar en el mercado para que las soluciones circulares fueran más competitivas?",
        "P3. ¿Qué problema no puede resolver una empresa sola y requeriría colaboración entre varias organizaciones?",
        "P4. ¿Qué debería hacer el Gobierno de Jalisco para acelerar la economía circular que hoy no está haciendo, o debería hacer de manera diferente?",
        "Cierre. Si pudiéramos modificar una sola condición del ecosistema de Jalisco durante los próximos tres años, ¿cuál tendría mayor efecto?",
    ],
}

PREGUNTAS_LIDERES_GREMIALES = {
    "Estrategia, gobernanza y capacidades": [
        "Detonadora. Desde su posición gremial, ¿qué tan incorporada está hoy la economía circular en la agenda de las empresas de su sector?",
        "P1. ¿Qué tipo de empresas están avanzando más y cuáles se están quedando atrás? ¿Por qué?",
        "P2. ¿Cuáles son hoy las principales brechas de capacidades del sector: conocimiento técnico, información, talento, liderazgo, indicadores u otras?",
        "P3. ¿Qué tendría que cambiar para que más empresas incorporen la circularidad como una decisión estratégica y no sólo como cumplimiento o una iniciativa aislada?",
        "P4. ¿Qué papel podrían jugar las cámaras y asociaciones empresariales para acelerar esa transición?",
        "Cierre. Si pudiera fortalecerse una sola capacidad sectorial en los próximos dos años, ¿cuál tendría mayor efecto?",
    ],
    "Operación circular, recursos y cadenas de valor": [
        "Detonadora. Desde una perspectiva sectorial, ¿dónde están hoy las mayores pérdidas de valor en materiales, agua, energía, residuos o logística?",
        "P1. ¿Qué flujos de residuos o subproductos tienen mayor potencial de aprovechamiento entre empresas del sector o entre sectores?",
        "P2. ¿Qué está impidiendo que esos intercambios ocurran hoy de manera sistemática?",
        "P3. ¿Qué problemas de escala, logística, calidad, trazabilidad o regulación aparecen de manera recurrente entre sus afiliados?",
        "P4. ¿Qué tipo de infraestructura o mecanismo compartido podría generar mayor impacto: centros de acopio, plataformas de intercambio, logística conjunta, servicios especializados u otro?",
        "Cierre. ¿Cuál sería la oportunidad de simbiosis o articulación empresarial más viable para comenzar a trabajar en Jalisco?",
    ],
    "Innovación, tecnología, inversión y financiamiento": [
        "Detonadora. ¿Qué tecnologías o soluciones circulares considera que tienen mayor potencial de adopción en las empresas de su sector durante los próximos años?",
        "P1. ¿Qué tecnologías están maduras, pero siguen sin escalar entre las empresas? ¿Qué las frena?",
        "P2. ¿Qué tipo de riesgo perciben las empresas: tecnológico, financiero, comercial, regulatorio o de implementación?",
        "P3. ¿Qué características tendría que tener un instrumento de apoyo para que realmente movilizara inversión privada?",
        "P4. ¿Qué hace más sentido para su sector: coinversión, crédito, garantías, asistencia técnica, pilotos, compras agregadas, vinculación con proveedores u otro mecanismo?",
        "P5. ¿Qué tipo de proyectos podrían estructurarse de manera colectiva o sectorial, en lugar de empresa por empresa?",
        "Cierre. Si Jalisco pudiera habilitar una sola línea de inversión circular para su sector, ¿cuál tendría mayor capacidad de movilizar capital privado?",
    ],
    "Entorno habilitante, regulación y colaboración": [
        "Detonadora. ¿Cuáles son hoy las principales condiciones del entorno que frenan la economía circular en su sector?",
        "P1. ¿Qué regulación, trámite, falta de claridad o ausencia de estándares está generando mayores obstáculos?",
        "P2. ¿Qué incentivos o señales de mercado podrían acelerar la adopción de prácticas circulares?",
        "P3. ¿Qué problemas requieren coordinación entre gobierno, empresas, academia, banca y organizaciones empresariales?",
        "P4. ¿Qué debería hacer el Gobierno de Jalisco que hoy no está haciendo para acelerar la transición circular?",
        "P5. ¿Qué podría hacer mejor el propio sector organizado —cámaras, asociaciones y organismos empresariales— para facilitar esa transición?",
        "Cierre. Si pudiera cambiar una sola condición de política pública o del ecosistema empresarial en Jalisco, ¿cuál tendría mayor impacto?",
    ],
}


GRUPOS = [
    "Sector primario",
    "Sector secundario",
    "Sector terciario",
    "Líderes gremiales",
]

BARRERAS = [
    "Sin clasificar",
    "Técnica",
    "Financiera",
    "Regulatoria",
    "Mercado",
    "Información / datos",
    "Capacidades",
    "Proveedores / infraestructura",
    "Coordinación",
    "Prioridad / gobernanza",
    "Otra",
]

ACTORES = [
    "Sin definir",
    "Empresa",
    "Gobierno estatal",
    "Gobierno municipal",
    "Cámara / organismo empresarial",
    "Academia / centro tecnológico",
    "Banca / financiador",
    "Proveedor",
    "Varias empresas",
    "Otro",
]


TIPOS_HALLAZGO_GREMIAL = [
    "Barrera sistémica",
    "Brecha de capacidades",
    "Regulación / trámite",
    "Mercado / demanda",
    "Infraestructura",
    "Financiamiento",
    "Tecnología / innovación",
    "Coordinación entre actores",
    "Oportunidad sectorial",
    "Otro",
]

AFECTACION_GREMIAL = [
    "PyMEs",
    "Grandes empresas",
    "Todo el sector",
    "Ciertos subsectores",
    "No se sabe",
    "Otro",
]

ACTORES_GREMIALES = [
    "Gobierno estatal",
    "Gobierno municipal",
    "Gobierno federal",
    "Cámaras / asociaciones",
    "Empresas",
    "Academia",
    "Banca / financiadores",
    "Proveedores",
    "Otro",
]

INSTRUMENTOS_GREMIALES = [
    "Regulación / simplificación",
    "Incentivo",
    "Coinversión",
    "Crédito / garantía",
    "Asistencia técnica",
    "Capacitación",
    "Infraestructura compartida",
    "Plataforma / coordinación",
    "Piloto",
    "Otro",
]

SECTORIALIDAD = [
    "No se sabe",
    "Sí, parece sectorial",
    "No, parece particular de la empresa",
]

PRIORIDADES = ["Sin clasificar", "Alta", "Media", "Baja"]


# ==========================================================
# Persistencia
# ==========================================================
@st.cache_resource
def get_supabase():
    if create_client is None:
        return None
    try:
        url = st.secrets.get("SUPABASE_URL", "")
        key = st.secrets.get(
            "SUPABASE_PUBLISHABLE_KEY",
            st.secrets.get("SUPABASE_KEY", "")
        )
        if url and key:
            return create_client(url, key)
    except Exception:
        pass
    return None


supabase = get_supabase()


def load_data():
    cols = [
        "id", "fecha_hora", "mesa", "grupo", "ronda", "relator", "moderador",
        "tipo_pregunta", "pregunta_referencia",
        "hallazgo", "barrera", "barrera_otra", "ejemplo", "actor", "actor_otro",
        "apoyo_solucion", "sectorialidad", "prioridad", "frase_clave", "notas",
        "tipo_hallazgo_gremial", "afectacion_gremial", "instrumento_gremial"
    ]

    if supabase:
        try:
            rows = (
                supabase.table("relatoria_hallazgos")
                .select("*")
                .order("created_at", desc=False)
                .execute()
                .data or []
            )
            df = pd.DataFrame(rows)
            if not df.empty:
                if "created_at" in df.columns and "fecha_hora" not in df.columns:
                    df["fecha_hora"] = df["created_at"]
                return df
        except Exception as e:
            st.warning(
                f"No se pudo leer Supabase. Se usará almacenamiento local. Detalle: {e}"
            )

    if LOCAL_CSV.exists():
        try:
            return pd.read_csv(LOCAL_CSV)
        except Exception:
            pass

    return pd.DataFrame(columns=cols)


def save_record(record):
    if supabase:
        payload = {k: v for k, v in record.items() if k != "id"}
        payload["created_at"] = datetime.now().isoformat(timespec="seconds")
        try:
            supabase.table("relatoria_hallazgos").insert(payload).execute()
            return True, "Guardado en Supabase."
        except Exception as e:
            return False, f"No se pudo guardar en Supabase: {e}"

    df = load_data()

    if df.empty:
        new_id = 1
    else:
        ids = pd.to_numeric(df.get("id", pd.Series(dtype=float)), errors="coerce")
        new_id = int(ids.max()) + 1 if ids.notna().any() else 1

    record = dict(record)
    record["id"] = new_id
    df = pd.concat([df, pd.DataFrame([record])], ignore_index=True)
    df.to_csv(LOCAL_CSV, index=False)
    return True, "Guardado localmente."


def delete_record(record_id):
    if supabase:
        try:
            supabase.table("relatoria_hallazgos").delete().eq(
                "id", int(record_id)
            ).execute()
            return True
        except Exception as e:
            st.error(f"No se pudo borrar: {e}")
            return False

    df = load_data()
    if "id" in df.columns:
        df = df[df["id"].astype(str) != str(record_id)]
        df.to_csv(LOCAL_CSV, index=False)
        return True
    return False


def to_excel_bytes(df):
    out = io.BytesIO()
    with pd.ExcelWriter(out, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Hallazgos")
        if not df.empty:
            resumen = (
                df.groupby(["mesa", "grupo", "barrera"], dropna=False)
                .size()
                .reset_index(name="n")
                .sort_values(
                    ["mesa", "grupo", "n"],
                    ascending=[True, True, False]
                )
            )
            resumen.to_excel(writer, index=False, sheet_name="Resumen")
    return out.getvalue()


def info_card(icon, icon_class, label, value):
    st.markdown(
        f"""
        <div class="info-card">
            <div class="info-icon {icon_class}">{icon}</div>
            <div>
                <div class="info-label">{label}</div>
                <div class="info-value">{value}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ==========================================================
# Estado compartido entre Hallazgos y Resumen
# ==========================================================
if "mesa_contexto" not in st.session_state or st.session_state["mesa_contexto"] not in MESAS:
    st.session_state["mesa_contexto"] = MESAS[0]
if "mesa_resumen" not in st.session_state or st.session_state["mesa_resumen"] not in MESAS:
    st.session_state["mesa_resumen"] = st.session_state["mesa_contexto"]

def sync_mesa_from_sidebar():
    mesa_sel = st.session_state.get("mesa_contexto")
    if mesa_sel in MESAS:
        st.session_state["mesa_resumen"] = mesa_sel

def sync_mesa_from_hallazgos():
    mesa_sel = st.session_state.get("f_mesa")
    if mesa_sel in MESAS:
        st.session_state["mesa_resumen"] = mesa_sel

def nuevo_hallazgo():
    for key, default in {
        "barreras_live": [],
        "barrera_otra_live": "",
        "actores_live": [],
        "actor_otro_live": "",
        "tipo_hallazgo_gremial_live": [],
        "afectacion_gremial_live": [],
        "actores_gremiales_live": [],
        "instrumentos_gremiales_live": [],
        "otro_tipo_gremial_live": "",
        "otro_afectado_gremial_live": "",
        "otro_actor_gremial_live": "",
        "otro_instrumento_gremial_live": "",
    }.items():
        st.session_state[key] = default
    st.session_state["hallazgo_guardado"] = False


# ==========================================================
# Sidebar
# ==========================================================
st.sidebar.markdown(
    """
    <div style="margin-bottom:1rem;">
        <div style="font-size:1.15rem;font-weight:850;color:#173B2E;">Relatoría</div>
        <div style="font-size:.96rem;font-weight:700;color:#55675D;">Economía Circular Jalisco</div>
    </div>
    """,
    unsafe_allow_html=True,
)
st.sidebar.markdown("## Datos de la ronda")

mesa = st.sidebar.selectbox(
    "Mesa temática",
    MESAS,
    key="mesa_contexto",
    on_change=sync_mesa_from_sidebar,
)
st.sidebar.caption(f"Mesa seleccionada: {mesa}")
grupo = st.sidebar.selectbox("Grupo / sector", GRUPOS)
ronda = st.sidebar.selectbox("Ronda", [1, 2, 3, 4])
relator = st.sidebar.text_input("Relator/a", placeholder="Nombre")
moderador = st.sidebar.text_input("Moderador/a", placeholder="Nombre")

st.sidebar.divider()

st.sidebar.markdown(
    """
    <div class="sidebar-note">
        👥 La mesa, moderador y relator permanecen anclados.
        Los grupos rotan.
    </div>
    """,
    unsafe_allow_html=True,
)

if grupo == "Líderes gremiales":
    st.sidebar.info(
        "Modo gremial activo: preguntas con enfoque sectorial y de política pública."
    )

if supabase:
    st.sidebar.markdown(
        """
        <div class="sidebar-db">
            🗄️ Base compartida:<br>
            <span style="font-size:1.05rem;">Supabase</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    st.sidebar.warning("Modo local")


# ==========================================================
# Encabezado
# ==========================================================

# Franja superior con las dos instituciones
with st.container(border=True):
    b1, bd, b2, spacer = st.columns(
        [1.15, 0.08, 0.95, 3.2],
        vertical_alignment="center"
    )

    with b1:
        if LOGO_COINVIERTE is not None:
            st.image(str(LOGO_COINVIERTE), width=190)
        else:
            st.markdown(
                f"<div style='color:{MUTED};font-weight:800;'>COINVIERTE</div>",
                unsafe_allow_html=True,
            )

    with bd:
        st.markdown(
            '<div class="brand-separator"></div>',
            unsafe_allow_html=True,
        )

    with b2:
        if LOGO_TEC is not None:
            # Mantener proporciones del archivo oficial sin alterar/redibujar el logotipo.
            st.image(str(LOGO_TEC), width=120)
        else:
            st.markdown(
                f"<div style='color:{MUTED};font-weight:800;'>Tecnológico de Monterrey</div>",
                unsafe_allow_html=True,
            )

    with spacer:
        st.write("")

st.write("")

# Hero principal
hero_html = f"""<div class="hero-shell">
<div style="display:inline-block;background:{SAGE_2};color:{GREEN_DARK};border-radius:999px;padding:.38rem .75rem;font-size:.78rem;font-weight:800;margin-bottom:.8rem;">🌿 Relatoría</div>
<div class="hero-title">Economía Circular Jalisco</div>
<div style="width:54px;height:4px;border-radius:99px;background:{GREEN};margin:.7rem 0 1rem 0;"></div>
<div class="hero-sub">Captura ágil de hallazgos para identificar barreras, oportunidades, actores habilitadores y soluciones con potencial de escalamiento.</div>
<div class="pill-row">
<span class="soft-pill pill-sage">🌿 {mesa}</span>
<span class="soft-pill pill-sand">👥 {grupo}</span>
<span class="soft-pill pill-aqua">🗓️ Ronda {ronda}</span>
</div>
</div>"""

st.markdown(hero_html, unsafe_allow_html=True)

st.write("")

# Context cards compactas
c1, c2, c3, c4 = st.columns(4)

with c1:
    info_card("👥", "icon-sage", "Mesa activa", mesa)

with c2:
    info_card("👤", "icon-sand", "Grupo actual", grupo)

with c3:
    info_card("🗓️", "icon-aqua", "Ronda", str(ronda))

with c4:
    info_card(
        "🗄️",
        "icon-sage",
        "Base de datos",
        "Supabase" if supabase else "Local",
    )


# ==========================================================
# Tabs
# ==========================================================
tab_captura, tab_hallazgos, tab_resumen = st.tabs(
    ["✎ Captura", "☷ Hallazgos", "▥ Resumen de mesa"]
)


# ==========================================================
# Captura
# ==========================================================
with tab_captura:
    st.markdown("## Registrar hallazgo")

    st.markdown(
        """
        <div class="rule-note">
            💡 <b>Regla simple:</b> un registro = un hallazgo.
            Captura el punto útil, la barrera y qué podría destrabarlo.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### Referencia de la conversación")
    preguntas_activas = (
        PREGUNTAS_LIDERES_GREMIALES[mesa]
        if grupo == "Líderes gremiales"
        else PREGUNTAS_POR_MESA[mesa]
    )

    pregunta_referencia = st.selectbox(
        "Pregunta de referencia *",
        preguntas_activas,
        help=(
            "La lista cambia según la mesa y el tipo de grupo. "
            "Para líderes gremiales se usa una batería sectorial y de política pública."
        )
    )

    if grupo == "Líderes gremiales":
        st.caption(
            "Bloque para líderes gremiales: enfocado en patrones sectoriales, barreras sistémicas, "
            "instrumentos, coordinación y condiciones para escalar la economía circular."
        )
    else:
        st.caption(
            "Selecciona la pregunta que originó el hallazgo. "
            "Así podremos sistematizar después por mesa, pregunta, sector y barrera."
        )

    es_cierre = pregunta_referencia.startswith("Cierre.")

    if es_cierre:
        # Cierre: una síntesis directa, sin clasificaciones adicionales.
        with st.form("cierre_form", clear_on_submit=True):
            respuesta_cierre = st.text_area(
                "Respuesta / síntesis de cierre *",
                placeholder="Captura aquí la conclusión principal del grupo para esta pregunta de cierre.",
                height=150,
            )

            guardar_cierre = st.form_submit_button(
                "💾 Guardar cierre",
                type="primary",
                use_container_width=True,
            )

            if guardar_cierre:
                if not respuesta_cierre.strip():
                    st.error("Captura la respuesta o síntesis de cierre.")
                elif not relator.strip():
                    st.error("Escribe el nombre del relator/a en la barra lateral.")
                else:
                    rec = {
                        "fecha_hora": datetime.now().isoformat(timespec="seconds"),
                        "mesa": mesa,
                        "grupo": grupo,
                        "ronda": int(ronda),
                        "relator": relator.strip(),
                        "moderador": moderador.strip(),
                        "tipo_pregunta": "",
                        "pregunta_referencia": pregunta_referencia,
                        "hallazgo": respuesta_cierre.strip(),
                        "barrera": "",
                        "barrera_otra": "",
                        "ejemplo": "",
                        "actor": "",
                        "actor_otro": "",
                        "apoyo_solucion": "",
                        "sectorialidad": "",
                        "prioridad": "",
                        "frase_clave": "",
                        "notas": "",
                        "tipo_hallazgo_gremial": "",
                        "afectacion_gremial": "",
                        "instrumento_gremial": "",
                    }

                    ok, msg = save_record(rec)
                    if ok:
                        _msg_guardado = st.success("Cierre guardado correctamente.")
                    else:
                        _msg_error = st.error(msg)

    elif grupo == "Líderes gremiales":
        # Formulario especial: patrón sectorial + política pública.
        st.markdown(
            """
            <div style="
                background:#EEF5E8;
                border:1px solid #DDE5DA;
                border-radius:12px;
                padding:10px 13px;
                margin-bottom:12px;">
                <b>Captura gremial:</b> registra el patrón sectorial, a quién afecta,
                qué actores deben intervenir y qué instrumento podría destrabarlo.
            </div>
            """,
            unsafe_allow_html=True,
        )

        tipo_hallazgo_sel = st.multiselect(
            "Tipo de hallazgo",
            TIPOS_HALLAZGO_GREMIAL,
            placeholder="Selecciona una o varias categorías",
            key="tipo_hallazgo_gremial_live",
        )

        afectacion_sel = st.multiselect(
            "¿A quién afecta principalmente?",
            AFECTACION_GREMIAL,
            placeholder="Selecciona una o varias opciones",
            key="afectacion_gremial_live",
        )

        actores_gremiales_sel = st.multiselect(
            "Actores que tendrían que intervenir",
            ACTORES_GREMIALES,
            placeholder="Selecciona uno o varios actores",
            key="actores_gremiales_live",
        )

        instrumentos_sel = st.multiselect(
            "Instrumento o acción que podría destrabarlo",
            INSTRUMENTOS_GREMIALES,
            placeholder="Selecciona una o varias opciones",
            key="instrumentos_gremiales_live",
        )

        otro_tipo = st.text_input(
            "Otro tipo de hallazgo",
            placeholder="Agrega otra categoría o precisión",
            key="otro_tipo_gremial_live",
        )

        otro_afectado = st.text_input(
            "Otro grupo afectado",
            placeholder="Agrega otro grupo, subsector o precisión",
            key="otro_afectado_gremial_live",
        )

        otro_actor_gremial = st.text_input(
            "Otro actor",
            placeholder="Agrega otro actor o precisión",
            key="otro_actor_gremial_live",
        )

        otro_instrumento = st.text_input(
            "Otro instrumento o acción",
            placeholder="Agrega otro instrumento, acción o precisión",
            key="otro_instrumento_gremial_live",
        )

        with st.form("hallazgo_gremial_form", clear_on_submit=True):
            hallazgo_gremial = st.text_area(
                "Hallazgo / patrón sectorial *",
                placeholder="¿Qué patrón, problema u oportunidad identifica en el sector?",
                height=105,
            )

            evidencia_gremial = st.text_area(
                "Ejemplo o evidencia sectorial",
                placeholder="Caso recurrente, dato, experiencia de afiliados o diferencia entre tipos de empresa.",
                height=90,
            )

            prioridad_gremial = st.selectbox(
                "Prioridad",
                ["Sin clasificar", "Alta", "Media", "Baja"],
            )

            guardar_gremial = st.form_submit_button(
                "💾 Guardar hallazgo gremial",
                type="primary",
                use_container_width=True,
            )

            if guardar_gremial:
                if not hallazgo_gremial.strip():
                    st.error("Captura el hallazgo o patrón sectorial antes de guardar.")
                elif not relator.strip():
                    st.error("Escribe el nombre del relator/a en la barra lateral.")
                else:
                    tipo_txt = " | ".join(tipo_hallazgo_sel)
                    if otro_tipo.strip():
                        tipo_txt = f"{tipo_txt} | Otro: {otro_tipo.strip()}" if tipo_txt else f"Otro: {otro_tipo.strip()}"

                    afectacion_txt = " | ".join(afectacion_sel)
                    if otro_afectado.strip():
                        afectacion_txt = f"{afectacion_txt} | Otro: {otro_afectado.strip()}" if afectacion_txt else f"Otro: {otro_afectado.strip()}"

                    actor_txt = " | ".join(actores_gremiales_sel)
                    if otro_actor_gremial.strip():
                        actor_txt = f"{actor_txt} | Otro: {otro_actor_gremial.strip()}" if actor_txt else f"Otro: {otro_actor_gremial.strip()}"

                    instrumento_txt = " | ".join(instrumentos_sel)
                    if otro_instrumento.strip():
                        instrumento_txt = f"{instrumento_txt} | Otro: {otro_instrumento.strip()}" if instrumento_txt else f"Otro: {otro_instrumento.strip()}"

                    rec = {
                        "fecha_hora": datetime.now().isoformat(timespec="seconds"),
                        "mesa": mesa,
                        "grupo": grupo,
                        "ronda": int(ronda),
                        "relator": relator.strip(),
                        "moderador": moderador.strip(),
                        "tipo_pregunta": "",
                        "pregunta_referencia": pregunta_referencia,
                        "hallazgo": hallazgo_gremial.strip(),
                        "barrera": tipo_txt,
                        "barrera_otra": "",
                        "ejemplo": evidencia_gremial.strip(),
                        "actor": actor_txt,
                        "actor_otro": "",
                        "apoyo_solucion": instrumento_txt,
                        "sectorialidad": afectacion_txt,
                        "prioridad": prioridad_gremial,
                        "frase_clave": "",
                        "notas": "",
                        "tipo_hallazgo_gremial": tipo_txt,
                        "afectacion_gremial": afectacion_txt,
                        "instrumento_gremial": instrumento_txt,
                    }

                    ok, msg = save_record(rec)
                    if ok:
                        st.session_state["hallazgo_guardado"] = True
                    else:
                        _msg_error = st.error(msg)

        if st.session_state.get("hallazgo_guardado"):
            st.success("Hallazgo gremial guardado correctamente.")
            st.button(
                "+ Registrar nuevo hallazgo",
                type="primary",
                use_container_width=True,
                on_click=nuevo_hallazgo,
                key="btn_nuevo_hallazgo",
            )

    else:
        # Formulario estándar para sectores primario, secundario y terciario.
        pre1, pre2 = st.columns(2)

        with pre1:
            barreras_sel = st.multiselect(
                "Barreras",
                BARRERAS[1:],
                placeholder="Selecciona una o varias barreras",
                key="barreras_live"
            )
            barrera_otra = st.text_input(
                "Otra barrera",
                placeholder="Agrega otra barrera o precisión, aunque ya hayas seleccionado una categoría",
                key="barrera_otra_live"
            )

        with pre2:
            actores_sel = st.multiselect(
                "Actores que pueden habilitar",
                ACTORES[1:],
                placeholder="Selecciona uno o varios actores",
                key="actores_live"
            )
            actor_otro = st.text_input(
                "Otro actor",
                placeholder="Agrega otro actor o precisión, aunque ya hayas seleccionado uno",
                key="actor_otro_live"
            )

        with st.form("hallazgo_form", clear_on_submit=True):
            hallazgo = st.text_area(
                "Problema / oportunidad *",
                placeholder=(
                    "Ej. Se generan subproductos orgánicos sin una salida "
                    "comercial estable."
                ),
                height=100,
            )

            c1, c2 = st.columns(2)

            with c1:
                prioridad = st.selectbox(
                    "Prioridad percibida",
                    PRIORIDADES
                )

            with c2:
                sectorialidad = st.selectbox(
                    "¿Parece sectorial?",
                    SECTORIALIDAD
                )

            e1, e2 = st.columns(2)

            with e1:
                ejemplo = st.text_area(
                    "Ejemplo concreto",
                    placeholder=(
                        "Describe un caso, dato o situación que ilustre "
                        "el hallazgo."
                    ),
                    height=88,
                )

            with e2:
                apoyo = st.text_area(
                    "Apoyo / solución sugerida",
                    placeholder=(
                        "¿Qué apoyo, herramienta o solución podría ayudar "
                        "a destrabarlo?"
                    ),
                    height=88,
                )

            with st.expander("Campos adicionales"):
                x1, x2 = st.columns(2)
                with x1:
                    frase = st.text_area(
                        "Frase clave (sin atribución)",
                        height=70
                    )
                with x2:
                    notas = st.text_area(
                        "Notas breves",
                        height=70
                    )

            b1, b2 = st.columns([1, 2])

            with b1:
                limpiar = st.form_submit_button(
                    "↻ Limpiar formulario",
                    use_container_width=True,
                )

            with b2:
                guardar = st.form_submit_button(
                    "💾 Guardar hallazgo",
                    type="primary",
                    use_container_width=True,
                )

            if limpiar:
                st.rerun()

            if guardar:
                if not hallazgo.strip():
                    st.error(
                        "Captura el problema u oportunidad antes de guardar."
                    )

                elif not relator.strip():
                    st.error(
                        "Escribe el nombre del relator/a en la barra lateral."
                    )

                else:
                    barrera_txt = " | ".join(barreras_sel)
                    actor_txt = " | ".join(actores_sel)

                    rec = {
                        "fecha_hora": datetime.now().isoformat(
                            timespec="seconds"
                        ),
                        "mesa": mesa,
                        "grupo": grupo,
                        "ronda": int(ronda),
                        "relator": relator.strip(),
                        "moderador": moderador.strip(),
                        "tipo_pregunta": "",
                        "pregunta_referencia": pregunta_referencia,
                        "hallazgo": hallazgo.strip(),
                        "barrera": barrera_txt,
                        "barrera_otra": barrera_otra.strip(),
                        "ejemplo": ejemplo.strip(),
                        "actor": actor_txt,
                        "actor_otro": actor_otro.strip(),
                        "apoyo_solucion": apoyo.strip(),
                        "sectorialidad": sectorialidad,
                        "prioridad": prioridad,
                        "frase_clave": frase.strip(),
                        "notas": notas.strip(),
                        "tipo_hallazgo_gremial": "",
                        "afectacion_gremial": "",
                        "instrumento_gremial": "",
                    }

                    ok, msg = save_record(rec)

                    if ok:
                        st.session_state["hallazgo_guardado"] = True
                    else:
                        _msg_error = st.error(msg)

        if st.session_state.get("hallazgo_guardado"):
            st.success("Hallazgo guardado correctamente.")
            st.button(
                "+ Registrar nuevo hallazgo",
                type="primary",
                use_container_width=True,
                on_click=nuevo_hallazgo,
                key="btn_nuevo_hallazgo",
            )

    if grupo != "Líderes gremiales":
        st.markdown(
            """
            <div style="
                margin-top:14px;
                background:#FFF7E6;
                border-left:4px solid #D4A33D;
                border-radius:12px;
                padding:11px 14px;
                color:#5E543E;">
                <b>Si una empresa no está haciendo nada:</b>
                también es un hallazgo. Si surge en la conversación,
                registra por qué no ha empezado: prioridad, conocimiento,
                presupuesto, liderazgo, proveedores, información u otra causa.
            </div>
            """,
            unsafe_allow_html=True,
        )


# ==========================================================
# Hallazgos
# ==========================================================
with tab_hallazgos:
    df = load_data()

    st.markdown("## Hallazgos registrados")

    m1, m2, m3, m4 = st.columns(4)

    total = len(df)
    altas = (
        int((df["prioridad"] == "Alta").sum())
        if not df.empty and "prioridad" in df.columns
        else 0
    )
    sectoriales = (
        int(
            (
                df["sectorialidad"]
                == "Sí, parece sectorial"
            ).sum()
        )
        if not df.empty and "sectorialidad" in df.columns
        else 0
    )
    mesas_con_datos = (
        int(df["mesa"].nunique())
        if not df.empty and "mesa" in df.columns
        else 0
    )

    m1.metric("Registros", total)
    m2.metric("Prioridad alta", altas)
    m3.metric("Parecen sectoriales", sectoriales)
    m4.metric("Mesas con datos", mesas_con_datos)

    f1, f2, f3, f4 = st.columns(4)

    with f1:
        filtro_mesa = st.selectbox(
            "Filtrar por mesa",
            ["Todas"] + MESAS,
            key="f_mesa",
            on_change=sync_mesa_from_hallazgos,
            help="Al elegir una mesa, esa selección se conserva en Resumen de mesa.",
        )

    with f2:
        filtro_grupo = st.selectbox(
            "Filtrar por grupo",
            ["Todos"] + GRUPOS,
            key="f_grupo"
        )

    preguntas_filtro = []
    if filtro_mesa != "Todas":
        preguntas_filtro = (
            PREGUNTAS_LIDERES_GREMIALES[filtro_mesa]
            if filtro_grupo == "Líderes gremiales"
            else PREGUNTAS_POR_MESA[filtro_mesa]
        )
    elif not df.empty and "pregunta_referencia" in df.columns:
        preguntas_filtro = sorted(
            [
                x for x in
                df["pregunta_referencia"].dropna().astype(str).unique().tolist()
                if x
            ]
        )

    with f3:
        filtro_pregunta = st.selectbox(
            "Filtrar por pregunta",
            ["Todas"] + preguntas_filtro,
            key="f_pregunta"
        )

    with f4:
        filtro_barrera = st.selectbox(
            "Filtrar por barrera",
            ["Todas"] + BARRERAS[1:],
            key="f_barrera"
        )

    view = df.copy()

    if not view.empty:
        if filtro_mesa != "Todas":
            view = view[
                view["mesa"] == filtro_mesa
            ]

        if filtro_grupo != "Todos":
            view = view[
                view["grupo"] == filtro_grupo
            ]


        if (
            filtro_pregunta != "Todas"
            and "pregunta_referencia" in view.columns
        ):
            view = view[
                view["pregunta_referencia"] == filtro_pregunta
            ]

        if filtro_barrera != "Todas":
            view = view[
                view["barrera"].fillna("").astype(str).str.contains(
                    re.escape(filtro_barrera),
                    regex=True
                )
            ]

    st.dataframe(
        view,
        use_container_width=True,
        hide_index=True,
        column_config={
            "pregunta_referencia": st.column_config.TextColumn(
                "Pregunta de referencia",
                width="large"
            ),
            "tipo_hallazgo_gremial": st.column_config.TextColumn(
                "Tipo de hallazgo gremial",
                width="large"
            ),
            "afectacion_gremial": st.column_config.TextColumn(
                "Afectación gremial",
                width="medium"
            ),
            "instrumento_gremial": st.column_config.TextColumn(
                "Instrumento / acción gremial",
                width="large"
            ),
            "hallazgo": st.column_config.TextColumn(
                "Hallazgo",
                width="large"
            ),
            "apoyo_solucion": st.column_config.TextColumn(
                "Apoyo / solución",
                width="large"
            ),
        },
    )

    d1, d2 = st.columns(2)

    with d1:
        st.download_button(
            "Descargar CSV",
            data=view.to_csv(
                index=False
            ).encode("utf-8-sig"),
            file_name="relatoria_economia_circular.csv",
            mime="text/csv",
            use_container_width=True,
        )

    with d2:
        st.download_button(
            "Descargar Excel",
            data=to_excel_bytes(view),
            file_name="relatoria_economia_circular.xlsx",
            mime=(
                "application/vnd.openxmlformats-officedocument."
                "spreadsheetml.sheet"
            ),
            use_container_width=True,
        )

    with st.expander("Borrar un registro"):
        if view.empty or "id" not in view.columns:
            st.caption(
                "No hay registros disponibles."
            )
        else:
            ids = view["id"].dropna().tolist()
            rid = st.selectbox(
                "ID del registro",
                ids
            )

            if st.button("Borrar registro"):
                if delete_record(rid):
                    _msg_borrado = st.success(
                        "Registro borrado."
                    )
                    st.rerun()


# ==========================================================
# Resumen
# ==========================================================
with tab_resumen:
    df = load_data()

    st.markdown("## Resumen de mesa")
    mesa_resumen = st.selectbox(
        "Mesa a consultar",
        MESAS,
        key="mesa_resumen",
        help="Puedes elegir directamente una mesa. Si la filtraste antes en Hallazgos, se conserva esa selección.",
    )
    st.caption(f"Mostrando únicamente los hallazgos de: {mesa_resumen}")

    mesa_df = (
        df[df["mesa"] == mesa_resumen].copy()
        if not df.empty and "mesa" in df.columns
        else pd.DataFrame()
    )

    st.markdown(f"### {mesa_resumen}")

    r1, r2, r3, r4 = st.columns(4)

    total_mesa = len(mesa_df)
    sectores = (
        int(mesa_df["grupo"].nunique())
        if not mesa_df.empty
        else 0
    )
    altas_mesa = (
        int((mesa_df["prioridad"] == "Alta").sum())
        if not mesa_df.empty and "prioridad" in mesa_df.columns
        else 0
    )
    sectoriales_mesa = (
        int(
            (
                mesa_df["sectorialidad"]
                == "Sí, parece sectorial"
            ).sum()
        )
        if not mesa_df.empty
        and "sectorialidad" in mesa_df.columns
        else 0
    )

    r1.metric("Hallazgos", total_mesa)
    r2.metric("Grupos escuchados", sectores)
    r3.metric("Prioridad alta", altas_mesa)
    r4.metric(
        "Parecen sectoriales",
        sectoriales_mesa
    )

    if mesa_df.empty:
        st.info(
            "Todavía no hay hallazgos registrados para esta mesa."
        )

    else:
        g1, g2 = st.columns(2)

        with g1:
            st.markdown("### Barreras más mencionadas")
            barr_series = (
                mesa_df["barrera"]
                .fillna("")
                .astype(str)
                .str.split(" | ", regex=False)
                .explode()
            )
            barr_series = barr_series[barr_series != ""]
            barr = (
                barr_series
                .value_counts()
                .rename_axis("Barrera")
                .reset_index(name="N")
            )
            if not barr.empty:
                st.bar_chart(
                    barr.set_index("Barrera")
                )
            else:
                st.caption("Sin barreras clasificadas todavía.")

        with g2:
            st.markdown("### Hallazgos por grupo")
            grp = (
                mesa_df["grupo"]
                .fillna("Sin grupo")
                .value_counts()
                .rename_axis("Grupo")
                .reset_index(name="N")
            )
            st.bar_chart(
                grp.set_index("Grupo")
            )

        st.markdown("### Hallazgos por pregunta de referencia")
        if "pregunta_referencia" in mesa_df.columns:
            por_pregunta = (
                mesa_df["pregunta_referencia"]
                .fillna("Sin referencia")
                .replace("", "Sin referencia")
                .value_counts()
                .rename_axis("Pregunta")
                .reset_index(name="Hallazgos")
            )
            st.dataframe(
                por_pregunta,
                use_container_width=True,
                hide_index=True,
            )

        st.markdown("### Prioridad alta / media")

        prioritarios = mesa_df[
            mesa_df["prioridad"].isin(
                ["Alta", "Media"]
            )
        ][
            [
                c for c in [
                    "grupo",
                    "hallazgo",
                    "barrera",
                    "actor",
                    "apoyo_solucion",
                    "prioridad",
                ]
                if c in mesa_df.columns
            ]
        ]

        st.dataframe(
            prioritarios,
            use_container_width=True,
            hide_index=True,
        )

        st.markdown("### Notas para la cosecha plenaria")

        st.text_area(
            "Escribe aquí 2–3 hallazgos, tensiones o necesidades recurrentes de la mesa",
            placeholder="1. ...\n2. ...\n3. ...",
            height=130,
            key=f"cosecha_{mesa}",
        )


st.divider()

st.markdown(
    """
    <div class="app-footer">
        COINVIERTE · Herramienta de apoyo para la sistematización
        cualitativa de la Línea Base de Economía Circular en Jalisco
    </div>
    """,
    unsafe_allow_html=True,
)
