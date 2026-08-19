import io
import os
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

try:
    from supabase import create_client
except Exception:
    create_client = None

st.set_page_config(
    page_title="Relatoría | Economía Circular Jalisco",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------
# Configuración visual COINVIERTE
# -----------------------------
COINV_BLUE = "#1F4E78"
COINV_DARK = "#163A5B"
COINV_LIGHT = "#EAF2F8"
COINV_GREEN = "#2E7D32"
COINV_GRAY = "#5F6B73"

st.markdown(
    f"""
    <style>
      .stApp {{ background: #F7F9FB; }}
      .block-container {{ padding-top: 1.2rem; padding-bottom: 3rem; max-width: 1450px; }}
      h1, h2, h3 {{ color: {COINV_BLUE}; }}
      [data-testid="stSidebar"] {{ background: #FFFFFF; border-right: 1px solid #E7EBEF; }}
      .coinv-card {{
        background: white; border: 1px solid #E7EBEF; border-radius: 14px;
        padding: 18px 20px; margin-bottom: 14px; box-shadow: 0 1px 2px rgba(0,0,0,.03);
      }}
      .coinv-note {{
        background: {COINV_LIGHT}; border-left: 5px solid {COINV_BLUE}; border-radius: 8px;
        padding: 12px 14px; margin: 8px 0 18px 0;
      }}
      .coinv-small {{ color: {COINV_GRAY}; font-size: .9rem; }}
      div.stButton > button[kind="primary"] {{ background: {COINV_BLUE}; border-color: {COINV_BLUE}; }}
      div.stButton > button[kind="primary"]:hover {{ background: {COINV_DARK}; border-color: {COINV_DARK}; }}
      [data-testid="stMetric"] {{ background:white; border:1px solid #E7EBEF; padding:10px 14px; border-radius:12px; }}
    </style>
    """,
    unsafe_allow_html=True,
)

BASE_DIR = Path(__file__).resolve().parent
LOGO_PATH = BASE_DIR / "assets" / "logo_coinvierte.png"
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
LOCAL_CSV = DATA_DIR / "relatoria_hallazgos.csv"

MESAS = [
    "Estrategia, gobernanza y capacidades",
    "Operación circular, recursos y cadenas de valor",
    "Innovación, tecnología, inversión y financiamiento",
    "Entorno habilitante, regulación y colaboración",
]

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

SECTORIALIDAD = ["No se sabe", "Sí, parece sectorial", "No, parece particular de la empresa"]
PRIORIDADES = ["Sin clasificar", "Alta", "Media", "Baja"]

# -----------------------------
# Persistencia: Supabase si existe, CSV si no
# -----------------------------
@st.cache_resource
def get_supabase():
    if create_client is None:
        return None
    try:
        url = st.secrets.get("SUPABASE_URL", "")
        key = st.secrets.get("SUPABASE_PUBLISHABLE_KEY", st.secrets.get("SUPABASE_KEY", ""))
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
            rows = supabase.table("relatoria_hallazgos").select("*").order("created_at", desc=False).execute().data or []
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
    new_id = int(pd.to_numeric(df.get("id", pd.Series(dtype=float)), errors="coerce").max() or 0) + 1 if not df.empty else 1
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
                .size().reset_index(name="n")
                .sort_values(["mesa", "grupo", "n"], ascending=[True, True, False])
            )
            resumen.to_excel(writer, index=False, sheet_name="Resumen")
    return out.getvalue()

# -----------------------------
# Encabezado
# -----------------------------
head1, head2 = st.columns([1, 5])
with head1:
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), use_container_width=True)
with head2:
    st.title("Relatoría · Economía Circular Jalisco")
    st.caption("Captura estructurada de hallazgos de las mesas de trabajo")

if not LOGO_PATH.exists():
    st.info("Logo: coloca el archivo usado en el tablero institucional en `assets/logo_coinvierte.png`.")

# -----------------------------
# Datos de la ronda en sidebar
# -----------------------------
st.sidebar.header("Datos de la ronda")
mesa = st.sidebar.selectbox("Mesa temática", MESAS)
grupo = st.sidebar.selectbox("Grupo / sector", GRUPOS)
ronda = st.sidebar.selectbox("Ronda", [1, 2, 3, 4])
relator = st.sidebar.text_input("Relator/a")
moderador = st.sidebar.text_input("Moderador/a")

st.sidebar.divider()
st.sidebar.caption("La mesa, el moderador y el relator permanecen anclados. Los grupos rotan.")
if supabase:
    st.sidebar.success("Base compartida: Supabase")
else:
    st.sidebar.warning("Modo local: los datos se guardan en esta computadora.")

# -----------------------------
# Navegación
# -----------------------------
tab_captura, tab_hallazgos, tab_resumen = st.tabs(["✍️ Captura", "📋 Hallazgos", "📊 Resumen de mesa"])

with tab_captura:
    st.subheader("Registrar hallazgo")
    st.markdown(
        '<div class="coinv-note"><b>Regla simple:</b> un registro = un hallazgo. '
        'No transcribas toda la conversación; captura el punto útil.</div>',
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

        submitted = st.form_submit_button("Guardar hallazgo", type="primary", use_container_width=True)

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

    st.markdown("### Cuando una empresa no esté haciendo nada")
    st.caption(
        "Registra la ausencia de acción como hallazgo y, si emerge en la conversación, la razón: "
        "falta de prioridad, conocimiento, presupuesto, liderazgo, proveedores, información u otra."
    )

with tab_hallazgos:
    df = load_data()
    st.subheader("Hallazgos registrados")

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
            if st.button("Borrar registro", type="secondary"):
                if delete_record(rid):
                    st.success("Registro borrado.")
                    st.rerun()

with tab_resumen:
    df = load_data()
    mesa_df = df[df["mesa"] == mesa].copy() if not df.empty and "mesa" in df.columns else pd.DataFrame()

    st.subheader(f"Resumen · {mesa}")
    m1, m2, m3, m4 = st.columns(4)
    total = len(mesa_df)
    sectores = mesa_df["grupo"].nunique() if not mesa_df.empty else 0
    altas = (mesa_df["prioridad"] == "Alta").sum() if not mesa_df.empty and "prioridad" in mesa_df else 0
    sectoriales = (mesa_df["sectorialidad"] == "Sí, parece sectorial").sum() if not mesa_df.empty and "sectorialidad" in mesa_df else 0
    m1.metric("Hallazgos", total)
    m2.metric("Grupos escuchados", sectores)
    m3.metric("Prioridad alta", int(altas))
    m4.metric("Parecen sectoriales", int(sectoriales))

    if mesa_df.empty:
        st.info("Todavía no hay hallazgos registrados para esta mesa.")
    else:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### Barreras más mencionadas")
            barr = mesa_df["barrera"].fillna("Sin clasificar").value_counts().rename_axis("Barrera").reset_index(name="N")
            st.dataframe(barr, hide_index=True, use_container_width=True)
        with c2:
            st.markdown("#### Hallazgos por grupo")
            grp = mesa_df["grupo"].fillna("Sin grupo").value_counts().rename_axis("Grupo").reset_index(name="N")
            st.dataframe(grp, hide_index=True, use_container_width=True)

        st.markdown("#### Prioridad alta / media")
        prioritarios = mesa_df[mesa_df["prioridad"].isin(["Alta", "Media"])][
            [c for c in ["grupo", "hallazgo", "barrera", "actor", "apoyo_solucion", "prioridad"] if c in mesa_df.columns]
        ]
        st.dataframe(prioritarios, use_container_width=True, hide_index=True)

        st.markdown("#### Notas para la cosecha plenaria")
        st.text_area(
            "Escribe aquí 2–3 hallazgos, tensiones o necesidades recurrentes de la mesa",
            placeholder="1. ...\n2. ...\n3. ...",
            height=130,
            key=f"cosecha_{mesa}",
        )

st.divider()
st.caption("COINVIERTE · Herramienta de apoyo para la sistematización cualitativa de la Línea Base de Economía Circular en Jalisco")
