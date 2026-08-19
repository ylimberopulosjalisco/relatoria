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
# RELATORIA COINVIERTE — VERSION VERDE V3 — 2026-08-19
# ==========================================================

st.set_page_config(
    page_title="Relatoría | Economía Circular Jalisco",
    page_icon="♻️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Paleta ambiental ----------
FOREST = "#173D2E"
FOREST_2 = "#235A3F"
GREEN = "#3C8D40"
LEAF = "#8DBF45"
AQUA = "#2F7D8C"
MINT = "#E6F4E8"
CREAM = "#F7FAF4"
BORDER = "#D8E5D8"
TEXT = "#2F4138"
MUTED = "#66776D"

st.markdown(
    f"""
    <style>
    .stApp {{
        background:
          radial-gradient(circle at 10% 0%, rgba(141,191,69,.12), transparent 28%),
          radial-gradient(circle at 100% 10%, rgba(47,125,140,.10), transparent 25%),
          linear-gradient(180deg,#FBFDF9 0%,#F3F8F2 100%);
        color:{TEXT};
    }}
    .block-container {{
        max-width: 1450px;
        padding-top: 1.1rem;
        padding-bottom: 2.5rem;
    }}
    h1,h2,h3 {{ color:{FOREST}; }}

    [data-testid="stSidebar"] {{
        background:linear-gradient(180deg,#F7FBF6 0%,#EDF6EE 100%);
        border-right:1px solid {BORDER};
    }}
    [data-testid="stSidebar"] h2 {{
        color:{FOREST};
    }}

    .eco-hero {{
        background: linear-gradient(120deg,{FOREST} 0%,{FOREST_2} 48%,{AQUA} 100%);
        border-radius:24px;
        padding:22px 26px;
        color:white;
        box-shadow:0 18px 40px rgba(23,61,46,.18);
        min-height:148px;
        display:flex;
        flex-direction:column;
        justify-content:center;
        position:relative;
        overflow:hidden;
    }}
    .eco-hero:after {{
        content:"♻";
        position:absolute;
        right:25px;
        top:-18px;
        font-size:150px;
        opacity:.08;
        transform:rotate(-12deg);
    }}
    .eco-title {{
        font-size:2.25rem;
        font-weight:800;
        letter-spacing:-.02em;
        line-height:1.08;
        margin-bottom:.45rem;
    }}
    .eco-sub {{
        font-size:1rem;
        opacity:.92;
        max-width:780px;
    }}
    .eco-chip {{
        display:inline-block;
        margin:.9rem .35rem 0 0;
        padding:.36rem .72rem;
        border-radius:999px;
        background:rgba(255,255,255,.14);
        border:1px solid rgba(255,255,255,.18);
        font-size:.82rem;
    }}

    .logo-card {{
        background:white;
        border:1px solid {BORDER};
        border-radius:24px;
        padding:18px;
        min-height:148px;
        display:flex;
        align-items:center;
        box-shadow:0 10px 25px rgba(23,61,46,.06);
    }}

    .eco-card {{
        background:rgba(255,255,255,.94);
        border:1px solid {BORDER};
        border-radius:18px;
        padding:15px 17px;
        box-shadow:0 7px 20px rgba(23,61,46,.05);
        height:100%;
    }}
    .eco-card-label {{
        color:{AQUA};
        font-size:.76rem;
        font-weight:800;
        text-transform:uppercase;
        letter-spacing:.05em;
    }}
    .eco-card-value {{
        color:{FOREST};
        margin-top:.25rem;
        font-weight:750;
        font-size:.98rem;
    }}

    .eco-note {{
        background:linear-gradient(90deg,{MINT},#F2F9F2);
        border-left:5px solid {GREEN};
        border-radius:12px;
        padding:12px 15px;
        margin:.3rem 0 1rem 0;
    }}
    .eco-warning {{
        background:#FFF7DE;
        border-left:5px solid #D6A431;
        border-radius:12px;
        padding:12px 15px;
        margin-top:1rem;
    }}

    .stTabs [data-baseweb="tab-list"] {{ gap:.45rem; }}
    .stTabs [data-baseweb="tab"] {{
        border:1px solid {BORDER};
        background:rgba(255,255,255,.85);
        border-radius:999px;
        padding:.48rem .9rem;
        height:auto;
    }}
    .stTabs [aria-selected="true"] {{
        background:{FOREST} !important;
        border-color:{FOREST} !important;
        color:white !important;
    }}

    div[data-testid="stMetric"] {{
        background:white;
        border:1px solid {BORDER};
        border-radius:18px;
        padding:10px 14px;
        box-shadow:0 7px 20px rgba(23,61,46,.05);
    }}

    .stTextArea textarea, .stTextInput input {{
        background:#FCFEFC !important;
    }}

    div.stButton > button[kind="primary"] {{
        background:linear-gradient(120deg,{GREEN},{AQUA});
        border:none;
        border-radius:12px;
        font-weight:700;
    }}
    div.stButton > button[kind="primary"]:hover {{
        filter:brightness(.96);
    }}

    .version-badge {{
        font-size:.73rem;
        color:{MUTED};
        text-align:right;
        margin-top:.2rem;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"
LOGO_PATH = ASSETS_DIR / "logo_coinvierte.png"

# Si el logo no tiene exactamente ese nombre, toma automáticamente
# la primera imagen válida que exista dentro de /assets.
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
MESA_ICON = {
    MESAS[0]: "🧭",
    MESAS[1]: "♻️",
    MESAS[2]: "⚙️",
    MESAS[3]: "🤝",
}

GRUPOS = [
    "Sector primario",
    "Sector secundario",
    "Sector terciario",
    "Líderes gremiales",
]

BARRERAS = [
    "Sin clasificar", "Técnica", "Financiera", "Regulatoria", "Mercado",
    "Información / datos", "Capacidades", "Proveedores / infraestructura",
    "Coordinación", "Prioridad / gobernanza", "Otra",
]

ACTORES = [
    "Sin definir", "Empresa", "Gobierno estatal", "Gobierno municipal",
    "Cámara / organismo empresarial", "Academia / centro tecnológico",
    "Banca / financiador", "Proveedor", "Varias empresas", "Otro",
]

SECTORIALIDAD = ["No se sabe", "Sí, parece sectorial", "No, parece particular de la empresa"]
PRIORIDADES = ["Sin clasificar", "Alta", "Media", "Baja"]


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
            st.warning(f"No se pudo leer Supabase. Se usará almacenamiento local. Detalle: {e}")

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
            supabase.table("relatoria_hallazgos").delete().eq("id", int(record_id)).execute()
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
                .sort_values(["mesa", "grupo", "n"], ascending=[True, True, False])
            )
            resumen.to_excel(writer, index=False, sheet_name="Resumen")
    return out.getvalue()


def card(label, value):
    st.markdown(
        f"""
        <div class="eco-card">
          <div class="eco-card-label">{label}</div>
          <div class="eco-card-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------- Sidebar ----------
st.sidebar.markdown("## Datos de la ronda")
mesa = st.sidebar.selectbox("Mesa temática", MESAS)
grupo = st.sidebar.selectbox("Grupo / sector", GRUPOS)
ronda = st.sidebar.selectbox("Ronda", [1, 2, 3, 4])
relator = st.sidebar.text_input("Relator/a", placeholder="Nombre")
moderador = st.sidebar.text_input("Moderador/a", placeholder="Nombre")

st.sidebar.divider()
st.sidebar.caption("La mesa, moderador y relator permanecen anclados. Los grupos rotan.")
if supabase:
    st.sidebar.success("Base compartida: Supabase")
else:
    st.sidebar.warning("Modo local")


# ---------- Hero ----------
logo_col, hero_col = st.columns([1.1, 4.6], gap="large")

with logo_col:
    st.markdown('<div class="logo-card">', unsafe_allow_html=True)
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), use_container_width=True)
    else:
        st.markdown(
            "<div style='font-size:3.2rem;text-align:center;width:100%'>♻️</div>",
            unsafe_allow_html=True
        )
    st.markdown("</div>", unsafe_allow_html=True)

with hero_col:
    st.markdown(
        f"""
        <div class="eco-hero">
          <div class="eco-title">Relatoría · Economía Circular Jalisco</div>
          <div class="eco-sub">
            Captura ágil de hallazgos para identificar barreras, oportunidades,
            actores habilitadores y soluciones con potencial de escalamiento.
          </div>
          <div>
            <span class="eco-chip">{MESA_ICON.get(mesa,"♻️")} {mesa}</span>
            <span class="eco-chip">👥 {grupo}</span>
            <span class="eco-chip">🔁 Ronda {ronda}</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown('<div class="version-badge">Diseño ambiental · versión 2026-08-19-B</div>', unsafe_allow_html=True)

# Cards de contexto
a, b, c, d = st.columns(4)
with a:
    card("Mesa activa", f"{MESA_ICON.get(mesa,'♻️')} {mesa}")
with b:
    card("Grupo actual", grupo)
with c:
    card("Ronda", str(ronda))
with d:
    card("Base de datos", "Supabase" if supabase else "Local")


tab_captura, tab_hallazgos, tab_resumen = st.tabs(
    ["✍️ Captura", "📋 Hallazgos", "📊 Resumen de mesa"]
)

with tab_captura:
    st.markdown("## Registrar hallazgo")
    st.markdown(
        '<div class="eco-note"><b>Regla simple:</b> un registro = un hallazgo. '
        'Captura el punto útil, la barrera y qué podría destrabarlo.</div>',
        unsafe_allow_html=True,
    )

    with st.form("hallazgo_form", clear_on_submit=True):
        hallazgo = st.text_area(
            "Problema / oportunidad *",
            placeholder="Ej. Se generan subproductos orgánicos sin una salida comercial estable.",
            height=95,
        )

        c1, c2, c3 = st.columns(3)
        with c1:
            barrera = st.selectbox("Barrera principal", BARRERAS)
            barrera_otra = st.text_input("Otra barrera", disabled=barrera != "Otra")
        with c2:
            actor = st.selectbox("Actor que puede habilitar", ACTORES)
            actor_otro = st.text_input("Otro actor", disabled=actor != "Otro")
        with c3:
            prioridad = st.selectbox("Prioridad percibida", PRIORIDADES)
            sectorialidad = st.selectbox("¿Parece sectorial?", SECTORIALIDAD)

        ejemplo = st.text_area(
            "Ejemplo concreto",
            placeholder="Caso, experiencia o situación mencionada por el participante.",
            height=80,
        )
        apoyo = st.text_area(
            "Apoyo / solución sugerida",
            placeholder="Diagnóstico, capacitación, financiamiento, coinversión, piloto, regulación, vinculación, etc.",
            height=80,
        )

        c4, c5 = st.columns(2)
        with c4:
            frase = st.text_area("Frase clave (sin atribución)", height=70)
        with c5:
            notas = st.text_area("Notas breves", height=70)

        submitted = st.form_submit_button(
            "Guardar hallazgo",
            type="primary",
            use_container_width=True,
        )

        if submitted:
            if not hallazgo.strip():
                st.error("Captura el problema u oportunidad antes de guardar.")
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
                    "hallazgo": hallazgo.strip(),
                    "barrera": barrera,
                    "barrera_otra": barrera_otra.strip() if barrera == "Otra" else "",
                    "ejemplo": ejemplo.strip(),
                    "actor": actor,
                    "actor_otro": actor_otro.strip() if actor == "Otro" else "",
                    "apoyo_solucion": apoyo.strip(),
                    "sectorialidad": sectorialidad,
                    "prioridad": prioridad,
                    "frase_clave": frase.strip(),
                    "notas": notas.strip(),
                }
                ok, msg = save_record(rec)
                if ok:
                    st.success("Hallazgo guardado correctamente.")
                else:
                    st.error(msg)

    st.markdown(
        '<div class="eco-warning"><b>Si una empresa no está haciendo nada:</b> '
        'también es un hallazgo. Si surge en la conversación, registra por qué no ha empezado: '
        'prioridad, conocimiento, presupuesto, liderazgo, proveedores, información u otra causa.</div>',
        unsafe_allow_html=True,
    )

with tab_hallazgos:
    df = load_data()
    st.markdown("## Hallazgos registrados")

    f1, f2, f3 = st.columns(3)
    with f1:
        filtro_mesa = st.selectbox("Filtrar por mesa", ["Todas"] + MESAS, key="f_mesa")
    with f2:
        filtro_grupo = st.selectbox("Filtrar por grupo", ["Todos"] + GRUPOS, key="f_grupo")
    with f3:
        filtro_barrera = st.selectbox("Filtrar por barrera", ["Todas"] + BARRERAS[1:], key="f_barrera")

    view = df.copy()
    if not view.empty:
        if filtro_mesa != "Todas":
            view = view[view["mesa"] == filtro_mesa]
        if filtro_grupo != "Todos":
            view = view[view["grupo"] == filtro_grupo]
        if filtro_barrera != "Todas":
            view = view[view["barrera"] == filtro_barrera]

    st.dataframe(
        view,
        use_container_width=True,
        hide_index=True,
        column_config={
            "hallazgo": st.column_config.TextColumn("Hallazgo", width="large"),
            "apoyo_solucion": st.column_config.TextColumn("Apoyo / solución", width="large"),
        },
    )

    d1, d2 = st.columns(2)
    with d1:
        st.download_button(
            "Descargar CSV",
            data=view.to_csv(index=False).encode("utf-8-sig"),
            file_name="relatoria_economia_circular.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with d2:
        st.download_button(
            "Descargar Excel",
            data=to_excel_bytes(view),
            file_name="relatoria_economia_circular.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )

    with st.expander("Borrar un registro"):
        if view.empty or "id" not in view.columns:
            st.caption("No hay registros disponibles.")
        else:
            ids = view["id"].dropna().tolist()
            rid = st.selectbox("ID del registro", ids)
            if st.button("Borrar registro"):
                if delete_record(rid):
                    st.success("Registro borrado.")
                    st.rerun()

with tab_resumen:
    df = load_data()
    mesa_df = (
        df[df["mesa"] == mesa].copy()
        if not df.empty and "mesa" in df.columns
        else pd.DataFrame()
    )

    st.markdown(f"## Resumen · {MESA_ICON.get(mesa,'♻️')} {mesa}")

    m1, m2, m3, m4 = st.columns(4)
    total = len(mesa_df)
    sectores = mesa_df["grupo"].nunique() if not mesa_df.empty else 0
    altas = (
        (mesa_df["prioridad"] == "Alta").sum()
        if not mesa_df.empty and "prioridad" in mesa_df
        else 0
    )
    sectoriales = (
        (mesa_df["sectorialidad"] == "Sí, parece sectorial").sum()
        if not mesa_df.empty and "sectorialidad" in mesa_df
        else 0
    )

    m1.metric("Hallazgos", total)
    m2.metric("Grupos escuchados", sectores)
    m3.metric("Prioridad alta", int(altas))
    m4.metric("Parecen sectoriales", int(sectoriales))

    if mesa_df.empty:
        st.info("Todavía no hay hallazgos registrados para esta mesa.")
    else:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("### Barreras más mencionadas")
            barr = (
                mesa_df["barrera"]
                .fillna("Sin clasificar")
                .value_counts()
                .rename_axis("Barrera")
                .reset_index(name="N")
            )
            st.bar_chart(barr.set_index("Barrera"))
        with c2:
            st.markdown("### Hallazgos por grupo")
            grp = (
                mesa_df["grupo"]
                .fillna("Sin grupo")
                .value_counts()
                .rename_axis("Grupo")
                .reset_index(name="N")
            )
            st.bar_chart(grp.set_index("Grupo"))

        st.markdown("### Prioridad alta / media")
        prioritarios = mesa_df[
            mesa_df["prioridad"].isin(["Alta", "Media"])
        ][
            [
                c for c in
                ["grupo", "hallazgo", "barrera", "actor", "apoyo_solucion", "prioridad"]
                if c in mesa_df.columns
            ]
        ]
        st.dataframe(prioritarios, use_container_width=True, hide_index=True)

        st.markdown("### Notas para la cosecha plenaria")
        st.text_area(
            "Escribe aquí 2–3 hallazgos, tensiones o necesidades recurrentes de la mesa",
            placeholder="1. ...\n2. ...\n3. ...",
            height=130,
            key=f"cosecha_{mesa}",
        )

st.divider()
st.caption(
    "COINVIERTE · Herramienta de apoyo para la sistematización cualitativa "
    "de la Línea Base de Economía Circular en Jalisco"
)
