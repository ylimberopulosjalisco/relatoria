
import io
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

try:
    from supabase import create_client
except Exception:
    create_client = None


# ==========================================================
# RELATORÍA COINVIERTE — PROPUESTA 4 + PREGUNTA DE REFERENCIA
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
        border-radius: 34px;
        min-height: 185px;
        padding: 28px 34px 24px 34px;
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
        font-size: 2.15rem;
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

    /* ---------- Logo ---------- */
    .logo-panel {{
        min-height: 185px;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 14px;
    }}
    .logo-panel img {{
        max-width: 245px;
        width: 100%;
        height: auto;
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
LOGO_PATH = ASSETS_DIR / "logo_coinvierte.png"

# Si el logo no tiene exactamente ese nombre, toma la primera imagen disponible.
if not LOGO_PATH.exists() and ASSETS_DIR.exists():
    for candidate in sorted(ASSETS_DIR.iterdir()):
        if candidate.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}:
            LOGO_PATH = candidate
            break

DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
LOCAL_CSV = DATA_DIR / "relatoria_hallazgos.csv"

MESAS = [
    "Estrategia, gobernanza y capacidades",
    "Operación circular, recursos y cadenas de valor",
    "Innovación, tecnología, inversión y financiamiento",
    "Entorno habilitante, regulación y colaboración",
]

TIPOS_PREGUNTA = [
    "Pregunta detonadora",
    "Pregunta central",
    "Cierre",
    "Seguimiento / repregunta",
]

PREGUNTAS_POR_MESA = {
    "Estrategia, gobernanza y capacidades": {
        "Pregunta detonadora": [
            "Pensando en su organización, ¿en qué medida la economía circular ya forma parte de la manera en que toman decisiones y operan, y en qué medida sigue siendo algo incipiente?"
        ],
        "Pregunta central": [
            "P1. ¿Su organización tiene hoy alguna práctica o iniciativa relacionada con economía circular, aunque sea incipiente o no la llamen así?",
            "P2. Cuando aparece una oportunidad de circularidad, ¿quién puede realmente impulsarla o detenerla dentro de la organización?",
            "P3. ¿Qué les hace falta dentro de la organización para poder avanzar más rápido?",
            "P4. ¿Qué información tendría que llegar a su escritorio para que ustedes dijeran: “sí, vale la pena hacer esta inversión”?",
        ],
        "Cierre": [
            "Si pudieran fortalecer una sola capacidad interna durante los próximos dos años, ¿cuál tendría mayor impacto?"
        ],
    },
    "Operación circular, recursos y cadenas de valor": {
        "Pregunta detonadora": [
            "Si recorriéramos hoy su operación completa, ¿en qué parte encontraríamos la mayor pérdida de valor: materiales, residuos, agua, energía, empaques, inventarios o logística?"
        ],
        "Pregunta central": [
            "P1. ¿Qué flujo de recursos consideran que tendría mayor potencial de mejora, aun si todavía no han iniciado acciones para atenderlo?",
            "P2. ¿Qué les impide aprovechar ese material, reducir ese consumo o cerrar ese ciclo actualmente?",
            "P3. ¿Identifican algún residuo o subproducto que potencialmente pudiera aprovechar otra empresa, o algún material externo que ustedes pudieran aprovechar, aunque hoy ese intercambio no exista?",
            "P4. ¿Qué tendría que cambiar en su cadena de proveedores o clientes para que ustedes pudieran ser más circulares?",
        ],
        "Cierre": [
            "¿Cuál sería la oportunidad operativa más tangible que podríamos comenzar a resolver en Jalisco?"
        ],
    },
    "Innovación, tecnología, inversión y financiamiento": {
        "Pregunta detonadora": [
            "¿Qué problema de su empresa saben que podría resolverse con tecnología o innovación, pero todavía no han podido resolver?"
        ],
        "Pregunta central": [
            "P1. ¿Qué tecnologías o soluciones conocen, han explorado o creen que podrían ser relevantes para avanzar hacia una economía más circular? Si ninguna está hoy en el radar, ¿por qué?",
            "P2. ¿Qué hace que una solución técnicamente viable no termine implementándose?",
            "P3. ¿Qué tendría que demostrar o resolver un proyecto para que su empresa considerara invertir recursos propios, incluso si hoy no existe disposición de inversión?",
            "P4. ¿Qué parte del riesgo tendría que compartir alguien más para que el proyecto ocurriera?",
            "P5. Si el gobierno quisiera ayudar a destrabar estas inversiones, ¿qué sería más útil y por qué?",
        ],
        "Cierre": [
            "¿Qué inversión circular creen que hoy no está ocurriendo en Jalisco pero podría ocurrir en los próximos dos o tres años si se elimina la barrera correcta?"
        ],
    },
    "Entorno habilitante, regulación y colaboración": {
        "Pregunta detonadora": [
            "Pensando fuera de su empresa, ¿cuál es hoy el principal obstáculo del entorno para avanzar hacia una economía circular?"
        ],
        "Pregunta central": [
            "P1. ¿Hay alguna regulación, trámite o falta de claridad regulatoria que esté dificultando una solución circular?",
            "P2. ¿Qué tendría que cambiar en el mercado para que las soluciones circulares fueran más competitivas?",
            "P3. ¿Qué problema no puede resolver una empresa sola y requeriría colaboración entre varias organizaciones?",
            "P4. ¿Qué debería hacer el Gobierno de Jalisco para acelerar la economía circular que hoy no está haciendo, o debería hacer de manera diferente?",
        ],
        "Cierre": [
            "Si pudiéramos modificar una sola condición del ecosistema de Jalisco durante los próximos tres años, ¿cuál tendría mayor efecto?"
        ],
    },
}

PREGUNTAS_SEGUIMIENTO = [
    "¿Esto que estamos escuchando es algo particular de su empresa, o creen que es común en su sector?",
    "¿Esto cambia mucho entre una empresa grande y una pyme?",
    "¿Tienen un ejemplo concreto que nos ayude a entender mejor el problema?",
    "¿Qué actor podría habilitar o destrabar esta situación?",
    "¿Qué faltó o qué no deberíamos perder antes de cerrar esta ronda?",
]

for _mesa in PREGUNTAS_POR_MESA:
    PREGUNTAS_POR_MESA[_mesa]["Seguimiento / repregunta"] = PREGUNTAS_SEGUIMIENTO

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
        "apoyo_solucion", "sectorialidad", "prioridad", "frase_clave", "notas"
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
# Sidebar
# ==========================================================
st.sidebar.markdown("## Datos de la ronda")

mesa = st.sidebar.selectbox("Mesa temática", MESAS)
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
logo_col, hero_col = st.columns([1.1, 4.9], gap="large")

with logo_col:
    st.markdown('<div class="logo-panel">', unsafe_allow_html=True)
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), use_container_width=True)
    else:
        st.markdown(
            f"""
            <div style="
                width:100%;
                padding:22px;
                text-align:center;
                color:{MUTED};
                border:1px dashed {BORDER};
                border-radius:18px;">
                COINVIERTE
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)

with hero_col:
    st.markdown(
        f"""
        <div class="hero-shell">
            <div class="hero-title">
                Relatoría · Economía Circular Jalisco
            </div>
            <div class="hero-sub">
                Captura ágil de hallazgos para identificar barreras,
                oportunidades, actores habilitadores y soluciones con
                potencial de escalamiento.
            </div>
            <div class="pill-row">
                <span class="soft-pill pill-sage">🌿 {mesa}</span>
                <span class="soft-pill pill-sand">👥 {grupo}</span>
                <span class="soft-pill pill-aqua">🗓️ Ronda {ronda}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.write("")

# Context cards
c1, c2, c3, c4 = st.columns(4)

with c1:
    info_card(
        "👥",
        "icon-sage",
        "Mesa activa",
        mesa,
    )

with c2:
    info_card(
        "👤",
        "icon-sand",
        "Grupo actual",
        grupo,
    )

with c3:
    info_card(
        "🗓️",
        "icon-aqua",
        "Ronda",
        str(ronda),
    )

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

    with st.form("hallazgo_form", clear_on_submit=True):
        st.markdown("### Referencia de la conversación")
        q1, q2 = st.columns([1, 2.35])

        with q1:
            tipo_pregunta = st.selectbox(
                "Tipo de intervención *",
                TIPOS_PREGUNTA,
                help="Permite distinguir detonadoras, preguntas centrales, cierre y preguntas de seguimiento."
            )

        preguntas_disponibles = PREGUNTAS_POR_MESA[mesa][tipo_pregunta]

        with q2:
            pregunta_referencia = st.selectbox(
                "Pregunta de referencia *",
                preguntas_disponibles,
                help="Cada hallazgo quedará asociado a esta pregunta para facilitar la sistematización posterior."
            )

        st.caption(
            "La pregunta se ajusta automáticamente a la mesa seleccionada. "
            "Registra un hallazgo por cada idea sustantiva que surja alrededor de ella."
        )

        hallazgo = st.text_area(
            "Problema / oportunidad *",
            placeholder=(
                "Ej. Se generan subproductos orgánicos sin una salida "
                "comercial estable."
            ),
            height=100,
        )

        c1, c2, c3 = st.columns(3)

        with c1:
            barrera = st.selectbox(
                "Barrera principal",
                BARRERAS
            )

        with c2:
            actor = st.selectbox(
                "Actor que puede habilitar",
                ACTORES
            )

        with c3:
            prioridad = st.selectbox(
                "Prioridad percibida",
                PRIORIDADES
            )

        c4, c5, c6 = st.columns(3)

        with c4:
            barrera_otra = st.text_input(
                "Otra barrera",
                placeholder="Describe otra barrera si aplica",
                disabled=barrera != "Otra",
            )

        with c5:
            actor_otro = st.text_input(
                "Otro actor",
                placeholder="Menciona otro actor si aplica",
                disabled=actor != "Otro",
            )

        with c6:
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
                rec = {
                    "fecha_hora": datetime.now().isoformat(
                        timespec="seconds"
                    ),
                    "mesa": mesa,
                    "grupo": grupo,
                    "ronda": int(ronda),
                    "relator": relator.strip(),
                    "moderador": moderador.strip(),
                    "tipo_pregunta": tipo_pregunta,
                    "pregunta_referencia": pregunta_referencia,
                    "hallazgo": hallazgo.strip(),
                    "barrera": barrera,
                    "barrera_otra": (
                        barrera_otra.strip()
                        if barrera == "Otra"
                        else ""
                    ),
                    "ejemplo": ejemplo.strip(),
                    "actor": actor,
                    "actor_otro": (
                        actor_otro.strip()
                        if actor == "Otro"
                        else ""
                    ),
                    "apoyo_solucion": apoyo.strip(),
                    "sectorialidad": sectorialidad,
                    "prioridad": prioridad,
                    "frase_clave": frase.strip(),
                    "notas": notas.strip(),
                }

                ok, msg = save_record(rec)

                if ok:
                    st.success(
                        "Hallazgo guardado correctamente."
                    )
                else:
                    st.error(msg)

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
            key="f_mesa"
        )

    with f2:
        filtro_grupo = st.selectbox(
            "Filtrar por grupo",
            ["Todos"] + GRUPOS,
            key="f_grupo"
        )

    with f3:
        filtro_tipo = st.selectbox(
            "Filtrar por tipo",
            ["Todos"] + TIPOS_PREGUNTA,
            key="f_tipo"
        )

    preguntas_filtro = []
    if filtro_mesa != "Todas":
        for _tipo in TIPOS_PREGUNTA:
            preguntas_filtro.extend(PREGUNTAS_POR_MESA[filtro_mesa][_tipo])
    elif not df.empty and "pregunta_referencia" in df.columns:
        preguntas_filtro = sorted(
            [x for x in df["pregunta_referencia"].dropna().astype(str).unique().tolist() if x]
        )

    with f4:
        filtro_pregunta = st.selectbox(
            "Filtrar por pregunta",
            ["Todas"] + preguntas_filtro,
            key="f_pregunta"
        )

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
            filtro_tipo != "Todos"
            and "tipo_pregunta" in view.columns
        ):
            view = view[
                view["tipo_pregunta"] == filtro_tipo
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
                view["barrera"] == filtro_barrera
            ]

    st.dataframe(
        view,
        use_container_width=True,
        hide_index=True,
        column_config={
            "tipo_pregunta": st.column_config.TextColumn(
                "Tipo",
                width="medium"
            ),
            "pregunta_referencia": st.column_config.TextColumn(
                "Pregunta de referencia",
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
                    st.success(
                        "Registro borrado."
                    )
                    st.rerun()


# ==========================================================
# Resumen
# ==========================================================
with tab_resumen:
    df = load_data()

    mesa_df = (
        df[df["mesa"] == mesa].copy()
        if not df.empty and "mesa" in df.columns
        else pd.DataFrame()
    )

    st.markdown(f"## Resumen · {mesa}")

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
            barr = (
                mesa_df["barrera"]
                .fillna("Sin clasificar")
                .value_counts()
                .rename_axis("Barrera")
                .reset_index(name="N")
            )
            st.bar_chart(
                barr.set_index("Barrera")
            )

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
