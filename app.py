import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Análisis de Comercio Exterior", layout="wide")

# 1. Cargar la base de datos completa
@st.cache_data
def cargar_datos_completos():
    # Saltamos la fila 1 (explicativa) y la fila 3 (totales)
    # Ajusta el nombre del archivo según lo guardes en GitHub (ej: 'datos_comercio.xlsx' o '.csv')
    df = pd.read_excel('TablaPrincipal.xlsx', header=1)
    
    # Eliminamos la fila de sumatoria (generalmente es la primera fila de datos)
    # y limpiamos espacios en los códigos de partida
    df = df.iloc[1:].copy() 
    df['Partida'] = df['Partida'].astype(str).str.strip().str.replace("'", "")
    df['Sector'] = df['Sector'].astype(str).str.strip()
    return df

try:
    df_data = cargar_datos_completos()
except Exception as e:
    st.error(f"Asegúrate de subir el archivo de datos al repositorio. Error: {e}")
    st.stop()

# 2. Barra Lateral: Organización de Búsquedas
st.sidebar.title("📌 Menú de Navegación")
tipo_busqueda = st.sidebar.radio(
    "Seleccione el tipo de análisis:",
    ["🔎 Búsqueda por Producto (Partida)", "🏭 Búsqueda por Sector", "🌍 Búsqueda por País Destino"]
)

años = [str(a) for a in range(2015, 2025)]

# ==========================================
# OPCIÓN 1: BÚSQUEDA POR PRODUCTO (PARTIDA)
# ==========================================
if tipo_busqueda == "🔎 Búsqueda por Producto (Partida)":
    st.title("📦 Análisis por Producto / Partida Arancelaria")
    
    partida_input = st.text_input("Ingrese la partida arancelaria (6 dígitos):", placeholder="Ej: 010121").strip()
    
    if partida_input:
        producto_data = df_data[df_data['Partida'] == partida_input]
        
        if not producto_data.empty:
            fila = producto_data.iloc[0]
            sector_actual = fila['Sector']
            descripcion = fila.get('Descripción de partida', 'Sin descripción')
            
            st.subheader(f"Partida: {partida_input} - {descripcion}")
            st.info(f"**Sector Perteneciente:** {sector_actual}")
            
            # --- BLOQUE 1: TENDENCIAS DEL PRODUCTO (2015-2024) ---
            st.markdown("### 📈 Panorama Global del Producto (2015 - 2024)")
            col1, col2 = st.columns(2)
            
            # Gráfico VCRn (Oferta Global de Perú)
            vcrn_cols = [c for c in df_data.columns if 'VCRn' in c and any(str(a) in c for a in años)]
            if vcrn_cols:
                vcrn_vals = fila[vcrn_cols].values
                df_vcrn = pd.DataFrame({'Año': años, 'VCRn': vcrn_vals})
                fig_vcrn = px.line(df_vcrn, x='Año', y='VCRn', title="Tendencia Oferta Global (VCRn Perú)", markers=True)
                fig_vcrn.add_hline(y=0, line_dash="dash", line_color="gray")
                col1.plotly_chart(fig_vcrn, use_container_width=True)
            
            # Gráfico CRCn (Demanda Global / Mercado)
            crcn_cols = [c for c in df_data.columns if 'CRCn' in c and any(str(a) in c for a in años)]
            if crcn_cols:
                crcn_vals = fila[crcn_cols].values
                df_crcn = pd.DataFrame({'Año': años, 'CRCn': crcn_vals})
                fig_crcn = px.line(df_crcn, x='Año', y='CRCn', title="Tendencia Demanda Global (CRCn Mercado)", markers=True)
                fig_crcn.add_hline(y=0, line_dash="dash", line_color="gray")
                col2.plotly_chart(fig_crcn, use_container_width=True)

            st.divider()

            # --- BLOQUE 2: ANÁLISIS MACRO DEL SECTOR ---
            st.markdown(f"### 🏭 Análisis del Sector: {sector_actual}")
            
            # Filtrar todas las partidas de este sector
            sector_df = df_data[df_data['Sector'] == sector_actual]
            num_partidas = len(sector_df)
            
            st.metric(label="Total de Partidas en este Sector", value=num_partidas)
            
            # Aquí se desplegará la Matriz Ansoff Histórica del Sector
            st.markdown("#### 🎯 Matriz Ansoff Histórica (2015-2024)")
            st.success("Estrategia del Sector: **[Definir con regla lógica o columna]**")

        else:
            st.warning(f"No se encontró la partida **{partida_input}**.")
