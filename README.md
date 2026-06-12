# Dashboard Profesional — Template Base
**Javier Sotelo · Consultoría BI & Automatización**

---

## Estructura del proyecto

```
mi_proyecto/
├── app.py                  ← toda la lógica y configuración
├── requirements.txt
├── assets/
│   └── logo.png            ← logo del cliente (.png .jpg .svg)
└── .streamlit/
    └── config.toml         ← paleta base (primaryColor)
```

---

## Adaptación por cliente — checklist

**Bloque de configuración en `app.py` (primeras ~30 líneas):**

| Variable | Qué cambiar |
|---|---|
| `EMPRESA_NOMBRE` | Nombre del cliente |
| `EMPRESA_SUBTITULO` | Descripción del sistema |
| `COLOR_PRIMARIO` | Color principal del logo (hex) |
| `COLOR_SECUNDARIO` | Tono más oscuro del primario |
| `COLOR_ACENTO` | Color secundario del logo |
| `USUARIOS` | Reemplazar hashes por los del cliente |
| `COLUMNAS_REQUERIDAS` | Según estructura del Excel del cliente |
| `COLUMNAS_SENSIBLES` | Columnas a descartar antes de procesar |

**Generar hash de contraseña:**
```python
import hashlib
print(hashlib.sha256("mi_contraseña".encode()).hexdigest())
```

**Actualizar también `.streamlit/config.toml`:**
```toml
primaryColor = "#XXXXXX"   # igual a COLOR_PRIMARIO
```

---

## Ejecutar localmente

```bash
pip install -r requirements.txt
streamlit run app.py
```

Abrir en el navegador: `http://localhost:8501`

---

## Arquitectura de seguridad

| Capa | Mecanismo |
|---|---|
| Acceso | Login con hash SHA-256 · contraseña nunca en texto plano |
| Datos | Upload en sesión autenticada · procesados en memoria |
| Privacidad | Columnas sensibles eliminadas antes de cualquier operación |
| Persistencia | Ninguna · sesión stateless · sin escritura a disco |

---

## Secciones incluidas

- Login con hash SHA-256 y cierre de sesión
- Pantalla de upload con validación de columnas
- Sidebar con navegación, info de archivo y usuario
- Header corporativo con logo y fecha/hora en vivo
- KPI cards con tipología por color (primario, acento, éxito, peligro)
- Gráficos Plotly en tabs: evolución mensual, por categoría, por estado
- Tabla con filtros dinámicos y exportación a Excel
- Footer con marca del desarrollador
