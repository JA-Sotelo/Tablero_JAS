"""
╔══════════════════════════════════════════════════════════════════════╗
║        TEMPLATE BASE — DASHBOARD PROFESIONAL STREAMLIT               ║
║        Javier Sotelo · Consultoría BI & Automatización               ║
╠══════════════════════════════════════════════════════════════════════╣
║  CHECKLIST POR CLIENTE                                               ║
║  [ ] EMPRESA_NOMBRE / EMPRESA_SUBTITULO                              ║
║  [ ] COLOR_PRIMARIO / COLOR_SECUNDARIO / COLOR_ACENTO (del logo)     ║
║  [ ] USUARIOS — generar hash con: hashlib.sha256(b"pwd").hexdigest() ║
║  [ ] COLUMNAS_REQUERIDAS — según estructura del Excel del cliente    ║
║  [ ] COLUMNAS_SENSIBLES  — columnas a descartar antes de procesar    ║
║  [ ] assets/logo.png — reemplazar con logo del cliente               ║
║  [ ] config.toml — primaryColor igual a COLOR_PRIMARIO               ║
╠══════════════════════════════════════════════════════════════════════╣
║  ARQUITECTURA DE SEGURIDAD                                           ║
║  1. Login con hash SHA-256 (contraseña nunca en texto plano)         ║
║  2. Upload Excel dentro de sesión autenticada                        ║
║  3. Columnas sensibles eliminadas antes de cualquier proceso         ║
║  4. Datos solo en st.session_state — nunca se escriben a disco       ║
║  5. Sesión stateless: al cerrar sesión, memoria limpia               ║
╚══════════════════════════════════════════════════════════════════════╝
"""

import hashlib
import base64
from pathlib import Path
from datetime import datetime, date
from io import BytesIO

import streamlit as st
import pandas as pd
import plotly.express as px

# ─────────────────────────────────────────────────────────────────────
# CONFIGURACIÓN DEL CLIENTE  ← único bloque a editar por proyecto
# ─────────────────────────────────────────────────────────────────────
EMPRESA_NOMBRE    = "Empresa del Cliente"
EMPRESA_SUBTITULO = "Sistema de Gestión y Análisis"

COLOR_PRIMARIO   = "#1A6EBF"   # color principal del logo
COLOR_SECUNDARIO = "#0D4A8C"   # tono más oscuro del primario
COLOR_ACENTO     = "#F0A500"   # color secundario del logo
COLOR_TEXTO      = "#1C2333"
COLOR_EXITO      = "#28A745"
COLOR_PELIGRO    = "#DC3545"

# Hash generado con: hashlib.sha256("tu_contraseña".encode()).hexdigest()
USUARIOS = {
    "admin":    {"hash": hashlib.sha256("admin123".encode()).hexdigest(), "rol": "Administrador"},
    "consulta": {"hash": hashlib.sha256("ver2024".encode()).hexdigest(),  "rol": "Solo Lectura"},
}

COLUMNAS_REQUERIDAS = ["Fecha", "Categoría", "Concepto", "Importe", "Estado"]
COLUMNAS_SENSIBLES  = []


# ─────────────────────────────────────────────────────────────────────
# CSS — variables Python → un solo lugar para cambiar colores
# ─────────────────────────────────────────────────────────────────────
CSS = f"""
<style>
html, body, [class*="css"] {{
    font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
    color: {COLOR_TEXTO};
}}
[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, {COLOR_SECUNDARIO} 0%, {COLOR_PRIMARIO} 100%);
}}
[data-testid="stSidebar"] * {{ color: #FFFFFF !important; }}
[data-testid="stSidebar"] .stRadio label {{
    background: rgba(255,255,255,0.08); border-radius: 8px;
    padding: 8px 14px; margin: 3px 0; display: block; transition: background .2s;
}}
[data-testid="stSidebar"] .stRadio label:hover {{ background: rgba(255,255,255,0.18); }}

.app-header {{
    background: linear-gradient(135deg, {COLOR_PRIMARIO}, {COLOR_SECUNDARIO});
    padding: 20px 28px; border-radius: 12px; margin-bottom: 24px;
    display: flex; align-items: center; justify-content: space-between;
}}
.app-header h1 {{ font-size: 1.5rem; font-weight: 700; margin: 0; color: white; }}
.app-header p  {{ font-size: 0.85rem; opacity: .85; margin: 4px 0 0; color: white; }}
.header-badge  {{
    background: rgba(255,255,255,0.2); border-radius: 20px;
    padding: 5px 14px; font-size: 0.8rem; color: white; white-space: nowrap;
    overflow: hidden; text-overflow: ellipsis; max-width: 260px;
}}

.kpi-card {{
    background: #fff; border-radius: 10px; padding: 18px 22px;
    border-left: 5px solid {COLOR_PRIMARIO};
    box-shadow: 0 1px 6px rgba(0,0,0,0.06); margin-bottom: 14px;
}}
.kpi-card.acento  {{ border-left-color: {COLOR_ACENTO}; }}
.kpi-card.exito   {{ border-left-color: {COLOR_EXITO}; }}
.kpi-card.peligro {{ border-left-color: {COLOR_PELIGRO}; }}
.kpi-label {{ font-size: .72rem; font-weight: 600; text-transform: uppercase;
              letter-spacing: .07em; color: #6B7280; margin-bottom: 5px; }}
.kpi-valor {{ font-size: 1.9rem; font-weight: 700; color: {COLOR_PRIMARIO}; line-height: 1.1; }}
.kpi-delta {{ font-size: .78rem; margin-top: 3px; color: #6B7280; }}
.kpi-delta.sube {{ color: {COLOR_EXITO}; }}
.kpi-delta.baja {{ color: {COLOR_PELIGRO}; }}

.section-title {{
    font-size: 1rem; font-weight: 600; color: {COLOR_PRIMARIO};
    border-bottom: 2px solid {COLOR_PRIMARIO}; padding-bottom: 5px; margin: 22px 0 14px;
}}
.upload-hint {{
    background: #F0F7FF; border: 2px dashed {COLOR_PRIMARIO}; border-radius: 12px;
    padding: 28px; text-align: center; margin-bottom: 18px;
}}
.upload-hint h3 {{ color: {COLOR_PRIMARIO}; margin: 0 0 6px; font-size: 1.1rem; }}
.upload-hint p  {{ color: #6B7280; margin: 0; font-size: .85rem; }}

.stButton > button {{
    background: {COLOR_PRIMARIO}; color: white; border: none;
    border-radius: 8px; font-weight: 600; transition: background .2s;
}}
.stButton > button:hover {{ background: {COLOR_SECUNDARIO}; color: white; }}
.stTabs [aria-selected="true"] {{
    color: {COLOR_PRIMARIO} !important;
    border-bottom: 3px solid {COLOR_PRIMARIO} !important;
}}
.app-footer {{
    text-align: center; font-size: .73rem; color: #9CA3AF;
    padding: 20px 0 6px; border-top: 1px solid #E5E7EB; margin-top: 36px;
}}
#MainMenu, footer, header {{ visibility: hidden; }}
</style>
"""


# ─────────────────────────────────────────────────────────────────────
# UTILIDADES
# ─────────────────────────────────────────────────────────────────────
def logo_base64(ruta: Path) -> str:
    """Devuelve data URI del logo — sin ninguna request externa."""
    if not ruta.exists():
        return ""
    mime = {".png": "image/png", ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg", ".svg": "image/svg+xml"}.get(ruta.suffix.lower(), "image/png")
    return f"data:{mime};base64,{base64.b64encode(ruta.read_bytes()).decode()}"


def kpi_card(label: str, valor: str, delta: str = "", tipo: str = ""):
    clase_delta = "sube" if delta.startswith("+") else ("baja" if delta.startswith("-") else "")
    delta_html  = f'<div class="kpi-delta {clase_delta}">{delta}</div>' if delta else ""
    st.markdown(f"""
    <div class="kpi-card {tipo}">
        <div class="kpi-label">{label}</div>
        <div class="kpi-valor">{valor}</div>
        {delta_html}
    </div>""", unsafe_allow_html=True)


def exportar_excel(df: pd.DataFrame) -> bytes:
    buf = BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as w:
        df.to_excel(w, index=False, sheet_name="Datos")
    return buf.getvalue()


def sidebar_logo_header(logo_src: str):
    if logo_src:
        st.markdown(
            f'<div style="text-align:center;padding:14px 0 8px">'
            f'<img src="{logo_src}" style="max-width:150px;max-height:58px;object-fit:contain"></div>',
            unsafe_allow_html=True)
    st.markdown(f"""
    <div style="text-align:center;padding:0 0 18px">
        <div style="font-weight:700">{EMPRESA_NOMBRE}</div>
        <div style="font-size:.74rem;opacity:.75">{EMPRESA_SUBTITULO}</div>
    </div>""", unsafe_allow_html=True)


def sidebar_usuario():
    st.markdown("---")
    st.markdown(f"""
    <div style="font-size:.76rem;opacity:.85">
        👤 <b>{st.session_state['usuario']}</b><br>
        🏷️ {st.session_state['rol']}
    </div>""", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🚪 Cerrar sesión", use_container_width=True):
        st.session_state.clear()
        st.rerun()


# ─────────────────────────────────────────────────────────────────────
# CAPA 1 — LOGIN
# ─────────────────────────────────────────────────────────────────────
def pantalla_login(logo_src: str):
    _, col, _ = st.columns([1, 2, 1])
    with col:
        if logo_src:
            st.markdown(
                f'<div style="text-align:center;margin-bottom:14px">'
                f'<img src="{logo_src}" style="max-height:68px;object-fit:contain"></div>',
                unsafe_allow_html=True)
        st.markdown(f'<div style="text-align:center;font-size:1.4rem;font-weight:700;color:{COLOR_PRIMARIO}">'
                    f'{EMPRESA_NOMBRE}</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="text-align:center;font-size:.84rem;color:#6B7280;margin-bottom:22px">'
                    f'{EMPRESA_SUBTITULO}</div>', unsafe_allow_html=True)

        usuario  = st.text_input("👤 Usuario",    placeholder="Ingresá tu usuario")
        password = st.text_input("🔑 Contraseña", placeholder="Ingresá tu contraseña", type="password")

        if st.button("Ingresar", use_container_width=True):
            datos = USUARIOS.get(usuario)
            if datos and datos["hash"] == hashlib.sha256(password.encode()).hexdigest():
                st.session_state.update(
                    autenticado=True, usuario=usuario,
                    rol=datos["rol"], df=None, archivo=""
                )
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos.")


# ─────────────────────────────────────────────────────────────────────
# CAPA 2 — UPLOAD
# ─────────────────────────────────────────────────────────────────────
def pantalla_upload(logo_src: str):
    with st.sidebar:
        sidebar_logo_header(logo_src)
        sidebar_usuario()

    st.markdown('<div class="section-title">📂 Cargar datos</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="upload-hint">
        <h3>📊 Subir Excel del cliente</h3>
        <p>Los datos se procesan en memoria y no se almacenan en ningún servidor.<br>
        Columnas requeridas: <b>{" &nbsp;|&nbsp; ".join(COLUMNAS_REQUERIDAS)}</b></p>
    </div>""", unsafe_allow_html=True)

    archivo = st.file_uploader("Seleccionar archivo Excel",
                               type=["xlsx", "xls"], label_visibility="collapsed")
    if not archivo:
        return

    try:
        df = pd.read_excel(archivo, engine="openpyxl")

        # Privacidad — eliminar columnas sensibles antes de cualquier operación
        if COLUMNAS_SENSIBLES:
            df.drop(columns=COLUMNAS_SENSIBLES, errors="ignore", inplace=True)

        # Validar estructura
        faltantes = [c for c in COLUMNAS_REQUERIDAS if c not in df.columns]
        if faltantes:
            st.error(f"⚠️ Columnas faltantes: {', '.join(faltantes)}")
            return

        # Tipado
        df["Fecha"]   = pd.to_datetime(df["Fecha"], errors="coerce")
        df["Importe"] = pd.to_numeric(df["Importe"], errors="coerce").fillna(0)
        df = df.dropna(subset=["Fecha"]).reset_index(drop=True)

        st.session_state["df"]      = df
        st.session_state["archivo"] = archivo.name
        st.rerun()

    except Exception as e:
        st.error(f"❌ Error al leer el archivo: {e}")


# ─────────────────────────────────────────────────────────────────────
# CAPA 3 — DASHBOARD
# ─────────────────────────────────────────────────────────────────────
COLORES_GRAFICOS = [COLOR_PRIMARIO, COLOR_ACENTO, COLOR_EXITO, "#9B59B6"]

def seccion_kpis(df: pd.DataFrame):
    st.markdown('<div class="section-title">📊 Indicadores Clave</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1: kpi_card("Total General",    f"$ {df['Importe'].sum():,.0f}")
    with c2: kpi_card("Promedio por Op.", f"$ {df['Importe'].mean():,.0f}", tipo="acento")
    with c3: kpi_card("Total Aprobado",
                      f"$ {df[df['Estado']=='Aprobado']['Importe'].sum():,.0f}", tipo="exito")
    with c4: kpi_card("Pendientes",
                      str(df[df["Estado"] == "Pendiente"].shape[0]), tipo="peligro")


def seccion_graficos(df: pd.DataFrame):
    st.markdown('<div class="section-title">📈 Análisis Visual</div>', unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs(["📅 Evolución mensual", "🏷️ Por categoría", "🔵 Por estado"])

    layout_base = dict(plot_bgcolor="white", paper_bgcolor="white",
                       margin=dict(l=10, r=10, t=10, b=10))

    with tab1:
        df_m = (df.assign(Mes=df["Fecha"].dt.to_period("M"))
                  .groupby(["Mes", "Categoría"])["Importe"].sum().reset_index())
        df_m["Mes"] = df_m["Mes"].dt.to_timestamp()
        fig = px.line(df_m, x="Mes", y="Importe", color="Categoría",
                      color_discrete_sequence=COLORES_GRAFICOS,
                      labels={"Importe": "Importe ($)", "Mes": ""})
        fig.update_layout(**layout_base, legend=dict(orientation="h", y=-0.2))
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        cat = df.groupby("Categoría")["Importe"].sum().reset_index()
        fig = px.bar(cat, x="Categoría", y="Importe",
                     color="Categoría", color_discrete_sequence=COLORES_GRAFICOS,
                     labels={"Importe": "Importe ($)"})
        fig.update_layout(**layout_base, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with tab3:
        est = df.groupby("Estado")["Importe"].sum().reset_index()
        fig = px.pie(est, names="Estado", values="Importe", hole=0.45,
                     color_discrete_sequence=[COLOR_EXITO, COLOR_ACENTO, COLOR_PELIGRO])
        fig.update_layout(**layout_base)
        st.plotly_chart(fig, use_container_width=True)


def seccion_tabla(df: pd.DataFrame):
    st.markdown('<div class="section-title">🔍 Detalle con Filtros</div>', unsafe_allow_html=True)

    f1, f2, f3 = st.columns(3)
    with f1:
        cat_sel = st.selectbox("Categoría", ["Todas"] + sorted(df["Categoría"].unique()))
    with f2:
        est_sel = st.selectbox("Estado",    ["Todos"] + sorted(df["Estado"].unique()))
    with f3:
        rango = st.date_input("Rango", (df["Fecha"].min().date(), df["Fecha"].max().date()))

    df_f = df.copy()
    if cat_sel != "Todas": df_f = df_f[df_f["Categoría"] == cat_sel]
    if est_sel != "Todos": df_f = df_f[df_f["Estado"]    == est_sel]
    if len(rango) == 2:
        df_f = df_f[(df_f["Fecha"].dt.date >= rango[0]) & (df_f["Fecha"].dt.date <= rango[1])]

    st.info(f"**{len(df_f):,}** registros  ·  Total: **$ {df_f['Importe'].sum():,.2f}**")
    st.dataframe(
        df_f.sort_values("Fecha", ascending=False).reset_index(drop=True),
        use_container_width=True, height=380,
        column_config={
            "Importe": st.column_config.NumberColumn("Importe ($)", format="$ %.2f"),
            "Fecha":   st.column_config.DateColumn("Fecha", format="DD/MM/YYYY"),
        }
    )
    col_btn, _ = st.columns([1, 3])
    with col_btn:
        st.download_button(
            "⬇️ Exportar a Excel", data=exportar_excel(df_f),
            file_name=f"export_{date.today():%Y%m%d}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )


def pantalla_dashboard(df: pd.DataFrame, logo_src: str):
    with st.sidebar:
        sidebar_logo_header(logo_src)
        st.markdown("**MENÚ PRINCIPAL**")
        pagina = st.radio("", ["🏠 Dashboard", "📈 Gráficos", "🔍 Detalle"],
                          label_visibility="collapsed")
        st.markdown("---")
        st.markdown(f"""
        <div style="font-size:.74rem;opacity:.85">
            📄 <b>{st.session_state['archivo']}</b><br>
            📋 {len(df):,} registros
        </div>""", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("📂 Cambiar archivo", use_container_width=True):
            st.session_state["df"] = None
            st.session_state["archivo"] = ""
            st.rerun()
        sidebar_usuario()

    # Header
    logo_tag = f'<img src="{logo_src}" style="height:46px;object-fit:contain">' if logo_src else "📊"
    st.markdown(f"""
    <div class="app-header">
        <div style="display:flex;align-items:center;gap:16px">
            {logo_tag}
            <div>
                <h1>{EMPRESA_NOMBRE}</h1>
                <p>{EMPRESA_SUBTITULO} &nbsp;·&nbsp; {datetime.now():%d/%m/%Y %H:%M}</p>
            </div>
        </div>
        <div class="header-badge">🟢 {st.session_state['archivo']}</div>
    </div>""", unsafe_allow_html=True)

    if pagina == "🏠 Dashboard":
        seccion_kpis(df)
        seccion_graficos(df)
    elif pagina == "📈 Gráficos":
        seccion_graficos(df)
    elif pagina == "🔍 Detalle":
        seccion_tabla(df)

    st.markdown(f"""
    <div class="app-footer">
        {EMPRESA_NOMBRE} &nbsp;·&nbsp;
        Desarrollado por <b>Javier Sotelo — Consultoría BI</b> &nbsp;·&nbsp;
        {datetime.now().year}
    </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────────────
def main():
    st.set_page_config(
        page_title=EMPRESA_NOMBRE, page_icon="📊",
        layout="wide", initial_sidebar_state="expanded"
    )
    st.markdown(CSS, unsafe_allow_html=True)

    logo_src = logo_base64(Path(__file__).parent / "assets" / "logo.png")

    if not st.session_state.get("autenticado"):
        pantalla_login(logo_src)
        return

    df = st.session_state.get("df")

    if df is None:
        pantalla_upload(logo_src)
        return

    pantalla_dashboard(df, logo_src)


if __name__ == "__main__":
    main()
