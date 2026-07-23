import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------------------------------------------------
# 1. Configuración inicial de la aplicación
# ---------------------------------------------------------
st.set_page_config(
    page_title="Plataforma de Análisis de Comercio Exterior", 
    page_icon="📊", 
    layout="wide"
)

# ---------------------------------------------------------
# 2. Función de Lógica Ansoff (Tabla D1)
# ---------------------------------------------------------
def calcular_estrategia_ansoff(x_peru, m_destino, x_directo, vcrn, crcn):
    """
    Evalúa los criterios de la Tabla D1 y retorna la estrategia correspondiente.
    """
    c_x = bool(x_peru > 0)
    c_m = bool(m_destino > 0)
    c_x_dir = bool(x_directo > 0)
    c_vcrn = bool(vcrn > 0)
    c_crcn = bool(crcn > 0)

    # 1. Penetración de Mercado (Sí, Sí, Sí, Sí, Sí)
    if c_x and c_m and c_x_dir and c_vcrn and c_crcn:
        return "🎯 Penetración de Mercado"
    
    # 2. Desarrollo de Producto (No, Sí, No, No, Sí)
    elif (not c_x) and c_m and (not c_x_dir) and (not c_vcrn) and c_crcn:
        return "🔬 Desarrollo de Producto"
    
    # 3. Desarrollo de Mercado - caso 1 (Sí, Sí, No, Sí, Sí)
    elif c_x and c_m and (not c_x_dir) and c_vcrn and c_crcn:
        return "🚀 Desarrollo de Mercado - Caso 1"
    
    # 4. Desarrollo de Mercado - caso 2 (Sí, No, No, Sí, No)
    elif c_x and (not c_m) and (not c_x_dir) and c_vcrn and (not c_crcn):
        return "🌐 Desarrollo de Mercado - Caso 2"
    
    # 5. Sin Estrategia (Cualquier otra combinación)
    else:
        return "⚪ Sin Estrategia"

# ---------------------------------------------------------
# 3. Carga y preparación de datos
# ---------------------------------------------------------
@st.cache_data(ttl=300)
def cargar_datos():
    # Lee el archivo CSV 'partidas_sector.csv' de tu repositorio
    df = pd.read_csv("partidas_sector.csv")
    
    # Limpieza básica de strings
    if 'Partida' in df.columns:
        df['Partida'] = df['Partida'].astype(str).str.replace("'", "").str.strip()
    if 'Sector' in df.columns:
        df['Sector'] = df['Sector'].astype(str).str.strip()
        
    return df

try:
    df_data = cargar_datos()
except Exception as e:
    st.error(f"Error al cargar la base de datos 'partidas_sector.csv': {e}")
    st.stop()

# ---------------------------------------------------------
# 4. Barra Lateral (Navegación Modular)
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
    
    partida_input = st.text_input("Ingrese la partida arancelaria (6 dígitos):", placeholder="Ej: 010121").strip()

    if partida_input:
        resultado = df_data[df_data['Partida'] == partida_input]

        if not resultado.empty:
            fila = resultado.iloc[0]
            sector_asociado = fila.get('Sector', 'No especificado')
            descripcion = fila.get('Descripción', fila.get('Descripción de partida', 'Sin descripción'))

            # Cabecera del Producto
            st.success(f"**Partida seleccionada:** {partida_input} - {descripcion}")
            st.caption(f"📌 **Sector Exportador pertenenciente:** {sector_asociado}")

            # --- SECCIÓN A: TENDENCIAS DEL PRODUCTO (SIN PAÍS SELECCIONADO) ---
            st.markdown("### 📈 Tendencias Globales del Producto")
            
            col_vcrn, col_crcn = st.columns(2)

            # Buscar columnas del VCRn (Oferta Perú)
            cols_vcrn = [c for c in df_data.columns if 'VCRn' in c and any(a in c for a in AÑOS)]
            if cols_vcrn:
                df_vcrn = pd.DataFrame({'Año': AÑOS, 'VCRn': [fila.get(c, 0) for c in cols_vcrn]})
                fig_vcrn = px.line(df_vcrn, x='Año', y='VCRn', title="Tendencia Oferta Global (VCRn Perú)", markers=True)
                fig_vcrn.add_hline(y=0, line_dash="dash", line_color="gray")
                col_vcrn.plotly_chart(fig_vcrn, use_container_width=True)

            # Buscar columnas del CRCn (Demanda Global)
            cols_crcn = [c for c in df_data.columns if 'CRCn' in c and any(a in c for a in AÑOS)]
            if cols_crcn:
                df_crcn = pd.DataFrame({'Año': AÑOS, 'CRCn': [fila.get(c, 0) for c in cols_crcn]})
                fig_crcn = px.line(df_crcn, x='Año', y='CRCn', title="Tendencia Demanda Global (CRCn Mercado)", markers=True)
                fig_crcn.add_hline(y=0, line_dash="dash", line_color="gray")
                col_crcn.plotly_chart(fig_crcn, use_container_width=True)

            # --- DIVISOR VISUAL ---
            st.divider()

            # --- SECCIÓN B: ANÁLISIS MACRO DEL SECTOR Y ESTRATEGIAS ANSOFF ---
            st.markdown(f"### 🏭 Análisis General del Sector: **{sector_asociado}**")

            # Cálculo de variables para la Matriz Ansoff Histórica (Promedio 2015-2024)
            x_peru_hist = fila.get('Promedio X Perú', fila.get('X Perú', 0))
            m_dest_hist = fila.get('Promedio M Dinamarca', fila.get('M Dinamarca', 0))
            x_dir_hist = fila.get('Promedio X Perú a Dinamarca', fila.get('X Perú a Dinamarca', 0))
            vcrn_hist = fila.get('Promedio VCRn', fila.get('VCRn', 0))
            crcn_hist = fila.get('Promedio CRCn', fila.get('CRCn', 0))

            est_historica = calcular_estrategia_ansoff(x_peru_hist, m_dest_hist, x_dir_hist, vcrn_hist, crcn_hist)

            # Cálculo de variables para la Matriz Ansoff Reciente (2024)
            x_peru_2024 = fila.get('X Perú 2024', fila.get('X Perú', 0))
            m_dest_2024 = fila.get('M Dinamarca 2024', fila.get('M Dinamarca', 0))
            x_dir_2024 = fila.get('X Perú a Dinamarca 2024', 0)
            vcrn_2024 = fila.get('VCRn 2024', fila.get('VCRn', 0))
            crcn_2024 = fila.get('CRCn 2024', fila.get('CRCn', 0))

            est_2024 = calcular_estrategia_ansoff(x_peru_2024, m_dest_2024, x_dir_2024, vcrn_2024, crcn_2024)

            # Despliegue de métricas Ansoff lado a lado
            c_ansoff_hist, c_ansoff_2024 = st.columns(2)

            with c_ansoff_hist:
                st.subheader("🏛️ Matriz ANSOFF Histórica (2015 - 2024)")
                st.info(f"**Estrategia:** {est_historica}")

            with c_ansoff_2024:
                st.subheader("⚡ Matriz ANSOFF Reciente (2024)")
                st.success(f"**Estrategia:** {est_2024}")

        else:
            st.warning(f"No se encontró la partida **{partida_input}** en el sistema.")

# ---------------------------------------------------------
# MÓDULOS EN DESARROLLO (SECTOR Y PAÍS)
# ---------------------------------------------------------
elif opcion_busqueda == "🏭 Búsqueda por Sector":
    st.title("🏭 Búsqueda por Sector Exportador")
    st.info("Módulo en preparación. Podrás filtrar y analizar todos los sectores comerciales.")

elif opcion_busqueda == "🌍 Búsqueda por País Destino":
    st.title("🌍 Búsqueda por País Destino")
    st.info("Módulo en preparación. Podrás analizar la demanda y acuerdos según el mercado elegido.")
