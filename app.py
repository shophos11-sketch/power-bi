import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------------------------------------------------
# 1. Configuración inicial
# ---------------------------------------------------------
st.set_page_config(
    page_title="Plataforma de Análisis de Comercio Exterior", 
    page_icon="📊", 
    layout="wide"
)

# ---------------------------------------------------------
# 2. Lógica Ansoff (Tabla D1)
# ---------------------------------------------------------
def calcular_estrategia_ansoff(x_peru, m_destino, x_directo, vcrn, crcn):
    c_x = bool(x_peru > 0)
    c_m = bool(m_destino > 0)
    c_x_dir = bool(x_directo > 0)
    c_vcrn = bool(vcrn > 0)
    c_crcn = bool(crcn > 0)

    if c_x and c_m and c_x_dir and c_vcrn and c_crcn:
        return "🎯 Penetración de Mercado"
    elif (not c_x) and c_m and (not c_x_dir) and (not c_vcrn) and c_crcn:
        return "🔬 Desarrollo de Producto"
    elif c_x and c_m and (not c_x_dir) and c_vcrn and c_crcn:
        return "🚀 Desarrollo de Mercado - Caso 1"
    elif c_x and (not c_m) and (not c_x_dir) and c_vcrn and (not c_crcn):
        return "🌐 Desarrollo de Mercado - Caso 2"
    else:
        return "⚪ Sin Estrategia"

# ---------------------------------------------------------
# 3. Carga de datos desde TablaPrincipal.xlsx
# ---------------------------------------------------------
@st.cache_data(ttl=300)
def cargar_datos():
    # Carga del Excel especificando la fila de encabezados
    try:
        df = pd.read_excel("TablaPrincipal.xlsx", header=0)
    except Exception:
        df = pd.read_csv("partidas_sector.csv")

    # Renombrar 'HS 6' a 'Partida' si existe para estandarizar
    col_hs = [c for c in df.columns if 'hs' in str(c).lower() or 'partida' in str(c).lower()]
    if col_hs:
        df = df.rename(columns={col_hs[0]: 'Partida'})
        
    if 'Partida' in df.columns:
        df['Partida'] = df['Partida'].astype(str).str.replace("'", "").str.strip()
        
    return df

try:
    df_data = cargar_datos()
except Exception as e:
    st.error(f"Error al cargar la base de datos: {e}")
    st.stop()

# ---------------------------------------------------------
# 4. Navegación
# ---------------------------------------------------------
st.sidebar.title("🔍 Navegación")
opcion_busqueda = st.sidebar.radio(
    "Selecciona el módulo de búsqueda:",
    ["📦 Búsqueda por Producto (Partida)", "🏭 Búsqueda por Sector", "🌍 Búsqueda por País Destino"]
)

AÑOS = [str(a) for a in range(2015, 2025)]

# ---------------------------------------------------------
# MÓDULO 1: BÚSQUEDA POR PRODUCTO (PARTIDA)
# ---------------------------------------------------------
if opcion_busqueda == "📦 Búsqueda por Producto (Partida)":
    st.title("📦 Análisis por Producto / Partida Arancelaria")
    
    partida_input = st.text_input("Ingrese la partida arancelaria (HS 6):", placeholder="Ej: 010121").strip()

    if partida_input:
        resultado = df_data[df_data['Partida'].str.contains(partida_input, na=False)]

        if not resultado.empty:
            fila = resultado.iloc[0]
            
            # Mapeo de columnas con soporte para fallbacks
            sector_asociado = fila.get('Sector', 'No especificado')
            descripcion = fila.get('Descripción de la partida arancelaria', fila.get('Descripción', 'Sin descripción'))

            st.success(f"**Partida seleccionada:** {partida_input} - {descripcion}")
            st.caption(f"📌 **Sector Exportador perteneciente:** {sector_asociado}")

            st.markdown("### 📈 Tendencias Históricas")
            col_vcrn, col_crcn = st.columns(2)

            # Extraer tendencias buscando patrones de VCRn y CRCn
            cols_vcrn = [c for c in df_data.columns if 'VCRn' in str(c)]
            cols_crcn = [c for c in df_data.columns if 'CRCn' in str(c)]

            if cols_vcrn:
                # Tomar los valores de los años para VCRn
                valores_vcrn = [fila.get(c, 0) for c in cols_vcrn[:10]]
                df_vcrn = pd.DataFrame({'Año': AÑOS[:len(valores_vcrn)], 'VCRn': valores_vcrn})
                fig_vcrn = px.line(df_vcrn, x='Año', y='VCRn', title="Oferta Perú (VCRn)", markers=True)
                fig_vcrn.add_hline(y=0, line_dash="dash", line_color="gray")
                col_vcrn.plotly_chart(fig_vcrn, use_container_width=True)

            if cols_crcn:
                # Tomar los valores de los años para CRCn
                valores_crcn = [fila.get(c, 0) for c in cols_crcn[:10]]
                df_crcn = pd.DataFrame({'Año': AÑOS[:len(valores_crcn)], 'CRCn': valores_crcn})
                fig_crcn = px.line(df_crcn, x='Año', y='CRCn', title="Demanda Mercado (CRCn)", markers=True)
                fig_crcn.add_hline(y=0, line_dash="dash", line_color="gray")
                col_crcn.plotly_chart(fig_crcn, use_container_width=True)

            st.divider()

            # --- ESTRATEGIA ANSOFF ---
            st.markdown(f"### 🏭 Estrategia Ansoff: **{sector_asociado}**")

            # Matriz Histórica
            x_peru_hist = fila.get('Promedio X Perú', 0)
            m_dest_hist = fila.get('Promedio M Dinamarca', 0)
            x_dir_hist = fila.get('Promedio X Perú a Dinamarca', 0)
            vcrn_hist = fila.get('Promedio VCRn', 0)
            crcn_hist = fila.get('Promedio CRCn', 0)

            est_historica = calcular_estrategia_ansoff(x_peru_hist, m_dest_hist, x_dir_hist, vcrn_hist, crcn_hist)

            # Matriz 2024
            x_peru_2024 = fila.get('2024', 0) if isinstance(fila.get('2024'), (int, float)) else 0
            m_dest_2024 = fila.get('2024.1', 0) if isinstance(fila.get('2024.1'), (int, float)) else 0
            x_dir_2024 = fila.get('2024.2', 0) if isinstance(fila.get('2024.2'), (int, float)) else 0
            vcrn_2024 = fila.get('2024.3', 0) if isinstance(fila.get('2024.3'), (int, float)) else 0
            crcn_2024 = fila.get('2024.4', 0) if isinstance(fila.get('2024.4'), (int, float)) else 0

            est_2024 = calcular_estrategia_ansoff(x_peru_2024, m_dest_2024, x_dir_2024, vcrn_2024, crcn_2024)

            c_ansoff_hist, c_ansoff_2024 = st.columns(2)
            with c_ansoff_hist:
                st.subheader("🏛️ ANSOFF Histórica (2015 - 2024)")
                st.info(f"**Estrategia:** {est_historica}")

            with c_ansoff_2024:
                st.subheader("⚡ ANSOFF Reciente (2024)")
                st.success(f"**Estrategia:** {est_2024}")

        else:
            st.warning(f"No se encontró la partida **{partida_input}** en `TablaPrincipal.xlsx`.")

# ---------------------------------------------------------
# MÓDULOS SECUNDARIOS
# ---------------------------------------------------------
elif opcion_busqueda == "🏭 Búsqueda por Sector":
    st.title("🏭 Búsqueda por Sector Exportador")
    st.info("Módulo en preparación.")

elif opcion_busqueda == "🌍 Búsqueda por País Destino":
    st.title("🌍 Búsqueda por País Destino")
    st.info("Módulo en preparación.")
