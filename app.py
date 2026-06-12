"""
╔══════════════════════════════════════════════════════════════════════╗
║          TEMPLATE BASE — DASHBOARD PROFESIONAL STREAMLIT             ║
║          Javier Sotelo — Consultoría BI & Automatización             ║
╠══════════════════════════════════════════════════════════════════════╣
║  PARA ADAPTAR A CADA CLIENTE:                                        ║
║  1. Cambiar EMPRESA_* (nombre, logo, colores)                        ║
║  2. Ajustar USUARIOS con credenciales reales                         ║
║  3. Ajustar COLUMNAS_REQUERIDAS según el Excel del cliente           ║
║  4. Actualizar config.toml con primaryColor del logo                 ║
║  5. Colocar logo en assets/logo.png                                  ║
╠══════════════════════════════════════════════════════════════════════╣
║  ARQUITECTURA DE SEGURIDAD:                                          ║
║  Capa 1 — Login usuario/contraseña (hash SHA-256)                    ║
║  Capa 2 — Upload Excel en sesión autenticada                         ║
║  Capa 3 — Datos solo en st.session_state (memoria, no disco)         ║
║  Capa 4 — Sesión stateless: al cerrar, no queda nada                 ║
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
EMPRESA_NOMBRE    = "Empresa del Cliente"
EMPRESA_SUBTITULO = "Sistema de Gestión y Análisis"

# Paleta del cliente — extraída del logo
COLOR_PRIMARIO   = "#1A6EBF"
COLOR_SECUNDARIO = "#0D4A8C"
COLOR_ACENTO     = "#F0A500"
COLOR_FONDO_CARD = "#FFFFFF"
COLOR_TEXTO      = "#1C2333"
COLOR_EXITO      = "#28A745"
COLOR_PELIGRO    = "#DC3545"

# Credenciales (las contraseñas NUNCA en texto plano)
# Para generar un hash: hashlib.sha256("tu_contraseña".encode()).hexdigest()
USUARIOS = {
    "admin":    {"hash": hashlib.sha256("admin123".encode()).hexdigest(), "rol": "Administrador"},
    "consulta": {"hash": hashlib.sha256("ver2024".encode()).hexdigest(),  "rol": "Solo Lectura"},
}

# Columnas requeridas en el Excel del cliente
# Ajustar según la estructura real del archivo
COLUMNAS_REQUERIDAS = ["Fecha", "Categoría", "Concepto", "Importe", "Estado"]

# Columnas a eliminar por contener datos sensibles (privacidad)
# Agregar aquí cualquier columna que NO deba procesarse
COLUMNAS_SENSIBLES = []


# ─────────────────────────────────────────────────────────────────────
# 1. LOGO — sin requests externas
# ─────────────────────────────────────────────────────────────────────
def cargar_logo(ruta=None) -> str:
    if ruta is None:
        ruta = Path(__file__).parent / "assets" / "logo.png"
    logo_path = Path(ruta)
    if not logo_path.exists():
        return ""
    mime = {".png": "image/png", ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg", ".svg": "image/svg+xml"}.get(logo_path.suffix.lower(), "image/png")
    with open(logo_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    return f"data:{mime};base64,{b64}"


# ─────────────────────────────────────────────────────────────────────
# 2. CSS GLOBAL
# ─────────────────────────────────────────────────────────────────────
def aplicar_estilos():
    st.markdown(f"""
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
        background: rgba(255,255,255,0.08);
        border-radius: 8px; padding: 8px 14px;
        margin: 3px 0; cursor: pointer;
        transition: background 0.2s; display: block;
    }}
    [data-testid="stSidebar"] .stRadio label:hover {{
        background: rgba(255,255,255,0.18);
    }}
    .app-header {{
        background: linear-gradient(135deg, {COLOR_PRIMARIO} 0%, {COLOR_SECUNDARIO} 100%);
        color: white; padding: 20px 28px; border-radius: 12px;
        margin-bottom: 24px; display: flex;
        align-items: center; justify-content: space-between;
    }}
    .app-header h1 {{ font-size: 1.6rem; font-weight: 700; margin: 0; color: white; }}
    .app-header p  {{ font-size: 0.85rem; opacity: 0.85; margin: 4px 0 0 0; color: white; }}
    .header-badge  {{
        background: rgba(255,255,255,0.2); border-radius: 20px;
        padding: 6px 14px; font-size: 0.8rem; font-weight: 500; color: white;
    }}
    .kpi-card {{
        background: {COLOR_FONDO_CARD}; border-radius: 12px;
        padding: 20px 24px; border-left: 5px solid {COLOR_PRIMARIO};
        box-shadow: 0 2px 8px rgba(0,0,0,0.07); margin-bottom: 16px;
        transition: transform 0.15s, box-shadow 0.15s;
    }}
    .kpi-card:hover {{ transform: translateY(-2px); box-shadow: 0 6px 16px rgba(0,0,0,0.12); }}
    .kpi-card.acento  {{ border-left-color: {COLOR_ACENTO}; }}
    .kpi-card.exito   {{ border-left-color: {COLOR_EXITO}; }}
    .kpi-card.peligro {{ border-left-color: {COLOR_PELIGRO}; }}
    .kpi-label {{ font-size: 0.75rem; font-weight: 600; text-transform: uppercase;
                  letter-spacing: 0.08em; color: #6B7280; margin-bottom: 6px; }}
    .kpi-valor {{ font-size: 2rem; font-weight: 700; color: {COLOR_PRIMARIO}; line-height: 1.1; }}
    .kpi-delta {{ font-size: 0.8rem; margin-top: 4px; color: #6B7280; }}
    .kpi-delta.sube {{ color: {COLOR_EXITO}; }}
    .kpi-delta.baja {{ color: {COLOR_PELIGRO}; }}
    .section-title {{
        font-size: 1.05rem; font-weight: 600; color: {COLOR_PRIMARIO};
        border-bottom: 2px solid {COLOR_PRIMARIO};
        padding-bottom: 6px; margin: 24px 0 16px 0;
    }}
    .upload-box {{
        background: white; border-radius: 16px; padding: 40px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        border: 2px dashed {COLOR_PRIMARIO}; text-align: center;
        margin: 20px 0;
    }}
    .upload-title {{ font-size: 1.2rem; font-weight: 700; color: {COLOR_PRIMARIO}; margin-bottom: 8px; }}
    .upload-sub   {{ font-size: 0.85rem; color: #6B7280; margin-bottom: 20px; }}
    .login-card {{
        background: white; border-radius: 16px; padding: 40px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.12); max-width: 420px; margin: 60px auto;
    }}
    .login-title {{ text-align: center; font-size: 1.5rem; font-weight: 700;
                    color: {COLOR_PRIMARIO}; margin-bottom: 4px; }}
    .login-sub   {{ text-align: center; font-size: 0.85rem; color: #6B7280; margin-bottom: 28px; }}
    .stButton > button {{
        background: {COLOR_PRIMARIO}; color: white; border: none;
        border-radius: 8px; font-weight: 600; padding: 8px 20px; transition: background 0.2s;
    }}
    .stButton > button:hover {{ background: {COLOR_SECUNDARIO}; color: white; }}
    .stTabs [data-baseweb="tab"] {{ font-weight: 500; font-size: 0.9rem; }}
    .stTabs [aria-selected="true"] {{
        color: {COLOR_PRIMARIO} !important;
        border-bottom: 3px solid {COLOR_PRIMARIO} !important;
    }}
    .app-footer {{
        text-align: center; font-size: 0.75rem; color: #9CA3AF;
        padding: 24px 0 8px 0; border-top: 1px solid #E5E7EB; margin-top: 40px;
    }}
    #MainMenu, footer, header {{ visibility: hidden; }}
    </style>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────
# 3. AUTENTICACIÓN
# ─────────────────────────────────────────────────────────────────────
def hash_password(pwd: str) -> str:
    return hashlib.sha256(pwd.encode()).hexdigest()

def pantalla_login(logo_src: str):
    aplicar_estilos()
    col_l, col_c, col_r = st.columns([1, 2, 1])
    with col_c:
        # Logo si existe
        if logo_src:
            st.markdown(f'<div style="text-align:center; margin-bottom:16px;">'
                        f'<img src="{logo_src}" style="max-height:70px; object-fit:contain;"></div>',
                        unsafe_allow_html=True)
        st.markdown(f'<div class="login-title">{EMPRESA_NOMBRE}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="login-sub">{EMPRESA_SUBTITULO}</div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        usuario  = st.text_input("👤 Usuario",     placeholder="Ingresá tu usuario")
        password = st.text_input("🔑 Contraseña",  placeholder="Ingresá tu contraseña", type="password")
        if st.button("Ingresar", use_container_width=True):
            if usuario in USUARIOS and USUARIOS[usuario]["hash"] == hash_password(password):
                st.session_state["autenticado"] = True
                st.session_state["usuario"]     = usuario
                st.session_state["rol"]         = USUARIOS[usuario]["rol"]
                st.session_state["df"]          = None
                st.session_state["nombre_archivo"] = ""
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos.")

def logout():
    st.session_state.clear()
    st.rerun()


# ─────────────────────────────────────────────────────────────────────
# 4. CARGA Y VALIDACIÓN DEL EXCEL
# Los datos viven solo en st.session_state — nunca se guardan en disco.
# ─────────────────────────────────────────────────────────────────────
def pantalla_upload():
    st.markdown('<div class="section-title">📂 Cargar archivo de datos</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="upload-box">
        <div class="upload-title">📊 Subir Excel del cliente</div>
        <div class="upload-sub">
            Los datos se procesan en memoria y no se almacenan en ningún servidor.<br>
            Columnas requeridas: <b>{" | ".join(COLUMNAS_REQUERIDAS)}</b>
        </div>
    </div>
    """, unsafe_allow_html=True)

    archivo = st.file_uploader(
        "Seleccionar archivo",
        type=["xlsx", "xls"],
        label_visibility="collapsed"
    )

    if archivo:
        try:
            df = pd.read_excel(archivo, engine="openpyxl")

            # Eliminar columnas sensibles antes de cualquier proceso
            if COLUMNAS_SENSIBLES:
                df.drop(columns=COLUMNAS_SENSIBLES, errors="ignore", inplace=True)

            # Validar columnas requeridas
            faltantes = [c for c in COLUMNAS_REQUERIDAS if c not in df.columns]
            if faltantes:
                st.error(f"⚠️ Columnas faltantes en el archivo: {', '.join(faltantes)}")
                return

            # Tipado
            df["Fecha"]   = pd.to_datetime(df["Fecha"], errors="coerce")
            df["Importe"] = pd.to_numeric(df["Importe"], errors="coerce").fillna(0)
            df = df.dropna(subset=["Fecha"])

            # Guardar en sesión
            st.session_state["df"]             = df
            st.session_state["nombre_archivo"] = archivo.name
            st.success(f"✅ Archivo cargado: **{archivo.name}** — {len(df):,} registros")
            st.rerun()

        except Exception as e:
            st.error(f"❌ Error al leer el archivo: {e}")


# ─────────────────────────────────────────────────────────────────────
# 5. HELPERS
# ─────────────────────────────────────────────────────────────────────
def kpi_card(label: str, valor: str, delta: str = "", tipo: str = ""):
    delta_class = "sube" if delta.startswith("+") else ("baja" if delta.startswith("-") else "")
    delta_html  = f'<div class="kpi-delta {delta_class}">{delta}</div>' if delta else ""
    st.markdown(f"""
    <div class="kpi-card {tipo}">
        <div class="kpi-label">{label}</div>
        <div class="kpi-valor">{valor}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)

def exportar_excel(df: pd.DataFrame, nombre_hoja: str = "Datos") -> bytes:
    buf = BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name=nombre_hoja)
    return buf.getvalue()


# ─────────────────────────────────────────────────────────────────────
# 6. SECCIONES DEL DASHBOARD
# ─────────────────────────────────────────────────────────────────────
def seccion_kpis(df: pd.DataFrame):
    st.markdown('<div class="section-title">📊 Indicadores Clave</div>', unsafe_allow_html=True)
    total      = df["Importe"].sum()
    promedio   = df["Importe"].mean()
    aprobados  = df[df["Estado"] == "Aprobado"]["Importe"].sum()
    pendientes = df[df["Estado"] == "Pendiente"].shape[0]

    c1, c2, c3, c4 = st.columns(4)
    with c1: kpi_card("Total General",    f"$ {total:,.0f}",    "", "")
    with c2: kpi_card("Promedio por Op.", f"$ {promedio:,.0f}", "", "acento")
    with c3: kpi_card("Total Aprobado",  f"$ {aprobados:,.0f}","", "exito")
    with c4: kpi_card("Pendientes",      f"{pendientes}",       "", "peligro")


def seccion_graficos(df: pd.DataFrame):
    st.markdown('<div class="section-title">📈 Análisis Visual</div>', unsafe_allow_html=True)
    colores = [COLOR_PRIMARIO, COLOR_ACENTO, COLOR_EXITO, "#9B59B6"]

    tab1, tab2, tab3 = st.tabs(["📅 Evolución mensual", "🏷️ Por categoría", "🔵 Por estado"])

    with tab1:
        df_m = (df.groupby([df["Fecha"].dt.to_period("M"), "Categoría"])["Importe"]
                  .sum().reset_index())
        df_m["Fecha"] = df_m["Fecha"].dt.to_timestamp()
        fig = px.line(df_m, x="Fecha", y="Importe", color="Categoría",
                      color_discrete_sequence=colores,
                      labels={"Importe": "Importe ($)", "Fecha": "Mes"})
        fig.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                          legend=dict(orientation="h", y=-0.2),
                          margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        cat_sum = df.groupby("Categoría")["Importe"].sum().reset_index()
        fig = px.bar(cat_sum, x="Categoría", y="Importe",
                     color="Categoría", color_discrete_sequence=colores,
                     labels={"Importe": "Importe ($)"})
        fig.update_layout(showlegend=False, plot_bgcolor="white", paper_bgcolor="white",
                          margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

    with tab3:
        est_sum = df.groupby("Estado")["Importe"].sum().reset_index()
        fig = px.pie(est_sum, names="Estado", values="Importe",
                     color_discrete_sequence=[COLOR_EXITO, COLOR_ACENTO, COLOR_PELIGRO],
                     hole=0.45)
        fig.update_layout(margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)


def seccion_tabla(df: pd.DataFrame):
    st.markdown('<div class="section-title">🔍 Detalle con Filtros</div>', unsafe_allow_html=True)

    f1, f2, f3 = st.columns([2, 2, 2])
    with f1:
        cats    = ["Todas"] + sorted(df["Categoría"].unique().tolist())
        cat_sel = st.selectbox("Categoría", cats)
    with f2:
        ests    = ["Todos"] + sorted(df["Estado"].unique().tolist())
        est_sel = st.selectbox("Estado", ests)
    with f3:
        rango = st.date_input("Rango de fechas",
                              value=(df["Fecha"].min().date(), df["Fecha"].max().date()))

    df_f = df.copy()
    if cat_sel != "Todas":  df_f = df_f[df_f["Categoría"] == cat_sel]
    if est_sel != "Todos":  df_f = df_f[df_f["Estado"]    == est_sel]
    if len(rango) == 2:
        df_f = df_f[(df_f["Fecha"].dt.date >= rango[0]) & (df_f["Fecha"].dt.date <= rango[1])]

    st.info(f"Mostrando **{len(df_f):,}** registros  |  Total: **$ {df_f['Importe'].sum():,.2f}**")
    st.dataframe(
        df_f.sort_values("Fecha", ascending=False).reset_index(drop=True),
        use_container_width=True, height=380,
        column_config={
            "Importe": st.column_config.NumberColumn("Importe ($)", format="$ %.2f"),
            "Fecha":   st.column_config.DateColumn("Fecha", format="DD/MM/YYYY"),
        }
    )

    col_exp, _ = st.columns([1, 3])
    with col_exp:
        st.download_button(
            label="⬇️ Exportar a Excel",
            data=exportar_excel(df_f),
            file_name=f"export_{date.today().strftime('%Y%m%d')}.xlsx",
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

    logo_src = cargar_logo()

    # ── Capa 1: Login ──
    if not st.session_state.get("autenticado"):
        pantalla_login(logo_src)
        return

    df = st.session_state.get("df")

    # ── Capa 2: Upload (si no hay datos cargados aún) ──
    if df is None:
        # Sidebar mínimo mientras no hay datos
        with st.sidebar:
            if logo_src:
                st.markdown(f'<div style="text-align:center; padding:16px 0;">'
                            f'<img src="{logo_src}" style="max-width:150px; max-height:60px; object-fit:contain;"></div>',
                            unsafe_allow_html=True)
            st.markdown(f"""
            <div style="text-align:center; padding:0 0 20px 0;">
                <div style="font-weight:700;">{EMPRESA_NOMBRE}</div>
                <div style="font-size:0.75rem; opacity:0.75;">{EMPRESA_SUBTITULO}</div>
            </div>
            """, unsafe_allow_html=True)
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

        pantalla_upload()
        return

    # ── Capa 3: Dashboard con datos en memoria ──
    with st.sidebar:
        if logo_src:
            st.markdown(f'<div style="text-align:center; padding:16px 0 12px 0;">'
                        f'<img src="{logo_src}" style="max-width:150px; max-height:60px; object-fit:contain;"></div>',
                        unsafe_allow_html=True)
        st.markdown(f"""
        <div style="text-align:center; padding:0 0 20px 0;">
            <div style="font-weight:700;">{EMPRESA_NOMBRE}</div>
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
        nombre_archivo = st.session_state.get("nombre_archivo", "")
        st.markdown(f"""
        <div style="font-size:0.75rem; opacity:0.8;">
            📄 <b>{nombre_archivo}</b><br>
            📋 {len(df):,} registros
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("📂 Cambiar archivo", use_container_width=True):
            st.session_state["df"] = None
            st.session_state["nombre_archivo"] = ""
            st.rerun()

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

    # Header
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
        <div class="header-badge">🟢 {st.session_state.get('nombre_archivo', '')}</div>
    </div>
    """, unsafe_allow_html=True)

    # Contenido
    if pagina == "🏠 Dashboard":
        seccion_kpis(df)
        st.markdown("<br>", unsafe_allow_html=True)
        seccion_graficos(df)
    elif pagina == "📈 Gráficos":
        seccion_graficos(df)
    elif pagina == "🔍 Detalle":
        seccion_tabla(df)

    st.markdown(f"""
    <div class="app-footer">
        {EMPRESA_NOMBRE} · Desarrollado por <b>Javier Sotelo — Consultoría BI</b> · {datetime.now().year}
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
