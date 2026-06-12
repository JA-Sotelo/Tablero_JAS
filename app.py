"""
╔══════════════════════════════════════════════════════════════════════╗
║          TEMPLATE BASE — DASHBOARD PROFESIONAL STREAMLIT             ║
║          Javier Sotelo — Consultoría BI & Automatización             ║
╠══════════════════════════════════════════════════════════════════════╣
║  PARA ADAPTAR A CADA CLIENTE:                                        ║
║  1. Cambiar EMPRESA_* (nombre, logo, colores)                        ║
║  2. Reemplazar datos demo por lectura real (Excel, DB, API)          ║
║  3. Ajustar USUARIOS con credenciales reales                         ║
║  4. Actualizar config.toml con primaryColor del logo                 ║
╚══════════════════════════════════════════════════════════════════════╝
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
import hashlib
import base64
from pathlib import Path
from datetime import datetime, date

# ─────────────────────────────────────────────────────────────────────
# 0. CONFIGURACIÓN DEL CLIENTE  ← EDITAR AQUÍ PARA CADA PROYECTO
# ─────────────────────────────────────────────────────────────────────
EMPRESA_NOMBRE  = "Empresa del Cliente"
EMPRESA_SUBTITULO = "Sistema de Gestión y Análisis"

# Paleta del cliente — extraída del logo
COLOR_PRIMARIO   = "#1A6EBF"   # botones, títulos, acentos
COLOR_SECUNDARIO = "#0D4A8C"   # hover, sidebar header
COLOR_ACENTO     = "#F0A500"   # KPIs destacados, badges
COLOR_FONDO_CARD = "#FFFFFF"
COLOR_TEXTO      = "#1C2333"
COLOR_EXITO      = "#28A745"
COLOR_PELIGRO    = "#DC3545"

# Credenciales — en producción reemplazar por DB o archivo externo
USUARIOS = {
    "admin":    {"hash": hashlib.sha256("admin123".encode()).hexdigest(), "rol": "Administrador"},
    "consulta": {"hash": hashlib.sha256("ver2024".encode()).hexdigest(),  "rol": "Solo Lectura"},
}


# ─────────────────────────────────────────────────────────────────────
# 0b. LOGO LOCAL — sin requests externas
# Colocar el logo en:  assets/logo.png  (también acepta .jpg, .jpeg, .svg)
# ─────────────────────────────────────────────────────────────────────
def cargar_logo(ruta: str = "assets/logo.png") -> str:
    """Devuelve el logo como data URI base64 — sin ninguna request externa."""
    logo_path = Path(ruta)
    if not logo_path.exists():
        return ""
    mime = {
        ".png":  "image/png",
        ".jpg":  "image/jpeg",
        ".jpeg": "image/jpeg",
        ".svg":  "image/svg+xml",
    }.get(logo_path.suffix.lower(), "image/png")
    with open(logo_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    return f"data:{mime};base64,{b64}"


# ─────────────────────────────────────────────────────────────────────
# 1. CSS GLOBAL — toda la customización visual centralizada
# ─────────────────────────────────────────────────────────────────────
def aplicar_estilos():
    st.markdown(f"""
    <style>
    /* ── Fuentes del sistema — sin requests externas ── */
    html, body, [class*="css"] {{
        font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
        color: {COLOR_TEXTO};
    }}

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, {COLOR_SECUNDARIO} 0%, {COLOR_PRIMARIO} 100%);
    }}
    [data-testid="stSidebar"] * {{
        color: #FFFFFF !important;
    }}
    [data-testid="stSidebar"] .stRadio label {{
        background: rgba(255,255,255,0.08);
        border-radius: 8px;
        padding: 8px 14px;
        margin: 3px 0;
        cursor: pointer;
        transition: background 0.2s;
        display: block;
    }}
    [data-testid="stSidebar"] .stRadio label:hover {{
        background: rgba(255,255,255,0.18);
    }}

    /* ── Header principal ── */
    .app-header {{
        background: linear-gradient(135deg, {COLOR_PRIMARIO} 0%, {COLOR_SECUNDARIO} 100%);
        color: white;
        padding: 20px 28px;
        border-radius: 12px;
        margin-bottom: 24px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }}
    .app-header h1 {{
        font-size: 1.6rem;
        font-weight: 700;
        margin: 0;
        color: white;
    }}
    .app-header p {{
        font-size: 0.85rem;
        opacity: 0.85;
        margin: 4px 0 0 0;
        color: white;
    }}
    .header-badge {{
        background: rgba(255,255,255,0.2);
        border-radius: 20px;
        padding: 6px 14px;
        font-size: 0.8rem;
        font-weight: 500;
        color: white;
    }}

    /* ── KPI Cards ── */
    .kpi-card {{
        background: {COLOR_FONDO_CARD};
        border-radius: 12px;
        padding: 20px 24px;
        border-left: 5px solid {COLOR_PRIMARIO};
        box-shadow: 0 2px 8px rgba(0,0,0,0.07);
        margin-bottom: 16px;
        transition: transform 0.15s, box-shadow 0.15s;
    }}
    .kpi-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(0,0,0,0.12);
    }}
    .kpi-card.acento {{ border-left-color: {COLOR_ACENTO}; }}
    .kpi-card.exito  {{ border-left-color: {COLOR_EXITO}; }}
    .kpi-card.peligro{{ border-left-color: {COLOR_PELIGRO}; }}
    .kpi-label {{
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #6B7280;
        margin-bottom: 6px;
    }}
    .kpi-valor {{
        font-size: 2rem;
        font-weight: 700;
        color: {COLOR_PRIMARIO};
        line-height: 1.1;
    }}
    .kpi-delta {{
        font-size: 0.8rem;
        margin-top: 4px;
        color: #6B7280;
    }}
    .kpi-delta.sube {{ color: {COLOR_EXITO}; }}
    .kpi-delta.baja {{ color: {COLOR_PELIGRO}; }}

    /* ── Section title ── */
    .section-title {{
        font-size: 1.05rem;
        font-weight: 600;
        color: {COLOR_PRIMARIO};
        border-bottom: 2px solid {COLOR_PRIMARIO};
        padding-bottom: 6px;
        margin: 24px 0 16px 0;
    }}

    /* ── Login card ── */
    .login-wrapper {{
        max-width: 420px;
        margin: 60px auto;
        background: white;
        border-radius: 16px;
        padding: 40px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.12);
    }}
    .login-title {{
        text-align: center;
        font-size: 1.5rem;
        font-weight: 700;
        color: {COLOR_PRIMARIO};
        margin-bottom: 4px;
    }}
    .login-sub {{
        text-align: center;
        font-size: 0.85rem;
        color: #6B7280;
        margin-bottom: 28px;
    }}

    /* ── Botones ── */
    .stButton > button {{
        background: {COLOR_PRIMARIO};
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        padding: 8px 20px;
        transition: background 0.2s;
    }}
    .stButton > button:hover {{
        background: {COLOR_SECUNDARIO};
        color: white;
    }}

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab"] {{
        font-weight: 500;
        font-size: 0.9rem;
    }}
    .stTabs [aria-selected="true"] {{
        color: {COLOR_PRIMARIO} !important;
        border-bottom: 3px solid {COLOR_PRIMARIO} !important;
    }}

    /* ── Footer ── */
    .app-footer {{
        text-align: center;
        font-size: 0.75rem;
        color: #9CA3AF;
        padding: 24px 0 8px 0;
        border-top: 1px solid #E5E7EB;
        margin-top: 40px;
    }}

    /* ── Ocultar elementos Streamlit ── */
    #MainMenu, footer, header {{ visibility: hidden; }}
    </style>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────
# 2. AUTENTICACIÓN
# ─────────────────────────────────────────────────────────────────────
def hash_password(pwd: str) -> str:
    return hashlib.sha256(pwd.encode()).hexdigest()

def pantalla_login():
    aplicar_estilos()
    st.markdown(f"""
    <div class="login-wrapper">
        <div class="login-title">🔐 {EMPRESA_NOMBRE}</div>
        <div class="login-sub">{EMPRESA_SUBTITULO}</div>
    </div>
    """, unsafe_allow_html=True)

    with st.container():
        col_c, col_f, col_d = st.columns([1, 2, 1])
        with col_f:
            st.markdown("<br>", unsafe_allow_html=True)
            usuario = st.text_input("👤 Usuario", placeholder="Ingresá tu usuario")
            password = st.text_input("🔑 Contraseña", type="password", placeholder="Ingresá tu contraseña")
            if st.button("Ingresar", use_container_width=True):
                if usuario in USUARIOS and USUARIOS[usuario]["hash"] == hash_password(password):
                    st.session_state["autenticado"] = True
                    st.session_state["usuario"]     = usuario
                    st.session_state["rol"]         = USUARIOS[usuario]["rol"]
                    st.rerun()
                else:
                    st.error("Usuario o contraseña incorrectos.")

def logout():
    for k in ["autenticado", "usuario", "rol"]:
        st.session_state.pop(k, None)
    st.rerun()


# ─────────────────────────────────────────────────────────────────────
# 3. CARGA DE DATOS DESDE EXCEL
# ─────────────────────────────────────────────────────────────────────
# Para cambiar de cliente: reemplazar el archivo Excel en datos/
# sin tocar ninguna línea de código.
#
# Columnas requeridas en hoja "Detalle":
#   Fecha | Categoría | Concepto | Importe | Estado
#
# Para renombrar el archivo: cambiar solo RUTA_DATOS aquí abajo.
# ─────────────────────────────────────────────────────────────────────
RUTA_DATOS = Path("datos/datos_demo_template.xlsx")

@st.cache_data
def cargar_datos_demo():
    if not RUTA_DATOS.exists():
        st.error(f"⚠️ Archivo no encontrado: {RUTA_DATOS}  —  Verificar carpeta datos/")
        st.stop()

    df_detalle = pd.read_excel(RUTA_DATOS, sheet_name="Detalle")
    df_detalle["Fecha"] = pd.to_datetime(df_detalle["Fecha"])

    df_mensual = (df_detalle
                  .groupby([df_detalle["Fecha"].dt.to_period("M"), "Categoría"])["Importe"]
                  .sum().reset_index())
    df_mensual["Fecha"] = df_mensual["Fecha"].dt.to_timestamp()

    return df_detalle, df_mensual


# ─────────────────────────────────────────────────────────────────────
# 4. HELPER: KPI card HTML
# ─────────────────────────────────────────────────────────────────────
def kpi_card(label: str, valor: str, delta: str = "", tipo: str = ""):
    delta_class = ""
    if delta.startswith("+"):  delta_class = "sube"
    elif delta.startswith("-"): delta_class = "baja"
    delta_html = f'<div class="kpi-delta {delta_class}">{delta}</div>' if delta else ""
    st.markdown(f"""
    <div class="kpi-card {tipo}">
        <div class="kpi-label">{label}</div>
        <div class="kpi-valor">{valor}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────
# 5. EXPORTAR A EXCEL
# ─────────────────────────────────────────────────────────────────────
def exportar_excel(df: pd.DataFrame, nombre_hoja: str = "Datos") -> bytes:
    buf = BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name=nombre_hoja)
    return buf.getvalue()


# ─────────────────────────────────────────────────────────────────────
# 6. SECCIONES DE LA APP
# ─────────────────────────────────────────────────────────────────────

def seccion_kpis(df: pd.DataFrame):
    st.markdown('<div class="section-title">📊 Indicadores Clave</div>', unsafe_allow_html=True)
    total    = df["Importe"].sum()
    promedio = df["Importe"].mean()
    aprobados = df[df["Estado"] == "Aprobado"]["Importe"].sum()
    pendientes = df[df["Estado"] == "Pendiente"].shape[0]

    c1, c2, c3, c4 = st.columns(4)
    with c1: kpi_card("Total General",    f"$ {total:,.0f}",    "+12.4% vs período ant.", "")
    with c2: kpi_card("Promedio por Op.", f"$ {promedio:,.0f}", "+3.1% vs período ant.",  "acento")
    with c3: kpi_card("Total Aprobado",  f"$ {aprobados:,.0f}","",                        "exito")
    with c4: kpi_card("Pendientes",      f"{pendientes}",      "-5 vs período ant.",      "peligro")


def seccion_graficos(df_detalle: pd.DataFrame, df_mensual: pd.DataFrame):
    st.markdown('<div class="section-title">📈 Análisis Visual</div>', unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📅 Evolución mensual", "🏷️ Por categoría", "🔵 Distribución"])

    colores = [COLOR_PRIMARIO, COLOR_ACENTO, COLOR_EXITO, "#9B59B6"]

    with tab1:
        fig = px.line(df_mensual, x="Fecha", y="Importe", color="Categoría",
                      color_discrete_sequence=colores,
                      labels={"Importe": "Importe ($)", "Fecha": "Mes"})
        fig.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                          legend=dict(orientation="h", y=-0.2),
                          margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        cat_sum = df_detalle.groupby("Categoría")["Importe"].sum().reset_index()
        fig = px.bar(cat_sum, x="Categoría", y="Importe",
                     color="Categoría", color_discrete_sequence=colores,
                     labels={"Importe": "Importe ($)"})
        fig.update_layout(showlegend=False, plot_bgcolor="white", paper_bgcolor="white",
                          margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

    with tab3:
        est_sum = df_detalle.groupby("Estado")["Importe"].sum().reset_index()
        fig = px.pie(est_sum, names="Estado", values="Importe",
                     color_discrete_sequence=[COLOR_EXITO, COLOR_ACENTO, COLOR_PELIGRO],
                     hole=0.45)
        fig.update_layout(margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)


def seccion_tabla(df: pd.DataFrame):
    st.markdown('<div class="section-title">🔍 Detalle con Filtros</div>', unsafe_allow_html=True)

    f1, f2, f3 = st.columns([2, 2, 2])
    with f1:
        categorias = ["Todas"] + sorted(df["Categoría"].unique().tolist())
        cat_sel = st.selectbox("Categoría", categorias)
    with f2:
        estados = ["Todos"] + sorted(df["Estado"].unique().tolist())
        est_sel = st.selectbox("Estado", estados)
    with f3:
        rango = st.date_input("Rango de fechas",
                              value=(df["Fecha"].min().date(), df["Fecha"].max().date()))

    df_f = df.copy()
    if cat_sel != "Todas":
        df_f = df_f[df_f["Categoría"] == cat_sel]
    if est_sel != "Todos":
        df_f = df_f[df_f["Estado"] == est_sel]
    if len(rango) == 2:
        df_f = df_f[(df_f["Fecha"].dt.date >= rango[0]) & (df_f["Fecha"].dt.date <= rango[1])]

    st.info(f"Mostrando **{len(df_f):,}** registros  |  Total: **$ {df_f['Importe'].sum():,.2f}**")
    st.dataframe(
        df_f.sort_values("Fecha", ascending=False).reset_index(drop=True),
        use_container_width=True,
        height=380,
        column_config={
            "Importe": st.column_config.NumberColumn("Importe ($)", format="$ %.2f"),
            "Fecha":   st.column_config.DateColumn("Fecha", format="DD/MM/YYYY"),
        }
    )

    col_exp, _ = st.columns([1, 3])
    with col_exp:
        excel_bytes = exportar_excel(df_f)
        st.download_button(
            label="⬇️ Exportar a Excel",
            data=excel_bytes,
            file_name=f"datos_export_{date.today().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )


# ─────────────────────────────────────────────────────────────────────
# 7. APP PRINCIPAL
# ─────────────────────────────────────────────────────────────────────
def main():
    st.set_page_config(
        page_title=EMPRESA_NOMBRE,
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    aplicar_estilos()

    # ── Verificar autenticación ──
    if not st.session_state.get("autenticado"):
        pantalla_login()
        return

    # ── Cargar datos y logo ──
    df_detalle, df_mensual = cargar_datos_demo()
    logo_src = cargar_logo("assets/logo.png")  # ← ruta relativa al proyecto

    # ── SIDEBAR ──
    with st.sidebar:
        # Logo: si existe el archivo lo muestra, si no muestra emoji como fallback
        if logo_src:
            st.markdown(f"""
            <div style="text-align:center; padding: 16px 0 12px 0;">
                <img src="{logo_src}"
                     style="max-width:160px; max-height:80px; object-fit:contain;">
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="text-align:center; padding: 16px 0 8px 0;">
                <div style="font-size:2rem;">📊</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style="text-align:center; padding: 0 0 20px 0;">
            <div style="font-size:1rem; font-weight:700;">{EMPRESA_NOMBRE}</div>
            <div style="font-size:0.75rem; opacity:0.75;">{EMPRESA_SUBTITULO}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("**MENÚ PRINCIPAL**")
        pagina = st.radio("", [
            "🏠 Dashboard",
            "📈 Gráficos",
            "🔍 Detalle",
        ], label_visibility="collapsed")

        st.markdown("---")
        st.markdown(f"""
        <div style="font-size:0.78rem; opacity:0.8;">
            👤 <b>{st.session_state['usuario']}</b><br>
            🏷️ {st.session_state['rol']}
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚪 Cerrar sesión", use_container_width=True):
            logout()

    # ── HEADER ──
    logo_header = f'<img src="{logo_src}" style="height:48px; object-fit:contain;">' if logo_src else "📊"
    st.markdown(f"""
    <div class="app-header">
        <div style="display:flex; align-items:center; gap:16px;">
            {logo_header}
            <div>
                <h1>{EMPRESA_NOMBRE}</h1>
                <p>{EMPRESA_SUBTITULO} — {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
            </div>
        </div>
        <div class="header-badge">🟢 En línea</div>
    </div>
    """, unsafe_allow_html=True)

    # ── CONTENIDO POR PÁGINA ──
    if pagina == "🏠 Dashboard":
        seccion_kpis(df_detalle)
        st.markdown("<br>", unsafe_allow_html=True)
        seccion_graficos(df_detalle, df_mensual)

    elif pagina == "📈 Gráficos":
        seccion_graficos(df_detalle, df_mensual)

    elif pagina == "🔍 Detalle":
        seccion_tabla(df_detalle)

    # ── FOOTER ──
    st.markdown(f"""
    <div class="app-footer">
        {EMPRESA_NOMBRE} · Desarrollado por <b>Javier Sotelo — Consultoría BI</b> · {datetime.now().year}
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
