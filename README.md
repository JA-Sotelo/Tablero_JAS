# 📊 Template Base — Dashboard Profesional Streamlit
**Javier Sotelo — Consultoría BI & Automatización**

---

## Estructura del proyecto

```
mi_proyecto/
│
├── app.py                        ← App principal
├── requirements.txt
└── .streamlit/
    └── config.toml               ← Paleta de colores
```

---

## Adaptación a cada cliente (checklist)

### 1. Nombre y subtítulo (app.py, líneas ~25-26)
```python
EMPRESA_NOMBRE    = "Nombre del Cliente SA"
EMPRESA_SUBTITULO = "Sistema de Control de Gestión"
```

### 2. Paleta de colores (app.py, líneas ~29-35)
Extraer los colores del logo con cualquier color picker (ej: imagecolorpicker.com):
```python
COLOR_PRIMARIO   = "#XXXXXX"   # color principal del logo
COLOR_SECUNDARIO = "#XXXXXX"   # tono más oscuro del primario
COLOR_ACENTO     = "#XXXXXX"   # color secundario del logo
```
Y actualizar también `.streamlit/config.toml`:
```toml
primaryColor = "#XXXXXX"
```

### 3. Credenciales (app.py, líneas ~38-41)
```python
USUARIOS = {
    "usuario1": {"hash": hashlib.sha256("contraseña1".encode()).hexdigest(), "rol": "Administrador"},
    "usuario2": {"hash": hashlib.sha256("contraseña2".encode()).hexdigest(), "rol": "Solo Lectura"},
}
```

### 4. Datos reales (app.py, función `cargar_datos_demo`)
Reemplazar el bloque de datos demo por la carga real:
```python
# Ejemplo: desde Excel
df = pd.read_excel("datos/reporte.xlsx")

# Ejemplo: desde MySQL
import sqlalchemy as sa
engine = sa.create_engine("mysql+pymysql://user:pass@host/db")
df = pd.read_sql("SELECT * FROM tabla", engine)
```

---

## Ejecutar localmente
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Credenciales
Las contraseñas NUNCA se documentan en texto plano.
Para conocer las credenciales vigentes, consultar directamente
al administrador del proyecto.

---

## Secciones incluidas
- ✅ Login con hash SHA-256
- ✅ Sidebar con navegación + info de usuario + logout
- ✅ Header corporativo con fecha/hora en vivo
- ✅ KPI cards con variación (sube/baja)
- ✅ Gráficos Plotly: línea, barras, torta (tabs)
- ✅ Tabla con filtros dinámicos (categoría, estado, rango fechas)
- ✅ Exportar a Excel con un clic
- ✅ Footer con marca del desarrollador
- ✅ CSS 100% personalizable por cliente
