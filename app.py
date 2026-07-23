import streamlit as st
import pandas as pd

# Configuración de la página
st.set_page_config(page_title="Buscador de Sectores", page_icon="🔎", layout="centered")

st.title("🔎 Consultar Sector por Partida Arancelaria")
st.write("Ingresa el código de 6 dígitos para identificar el sector exportador.")

# 1. Cargar el CSV directamente desde GitHub
@st.cache_data(ttl=300)
def cargar_base_datos():
    # Leemos el archivo CSV que subiste
    df = pd.read_csv("partidas_sector.csv")
    
    # Limpiamos la comilla simple (') si viene incluida en el texto y eliminamos espacios extra
    df['Partida'] = df['Partida'].astype(str).str.replace("'", "").str.strip()
    df['Sector'] = df['Sector'].astype(str).str.strip()
    
    return df

try:
    df_partidas = cargar_base_datos()

    # 2. Entrada directa del usuario
    busqueda = st.text_input("Ingrese la partida arancelaria (6 dígitos):", placeholder="Ej: 010121")

    if busqueda:
        # Quitamos espacios accidentales del buscador
        busqueda_limpia = busqueda.strip()
        
        # Búsqueda exacta en la columna 'Partida'
        resultado = df_partidas[df_partidas['Partida'] == busqueda_limpia]

        if not resultado.empty:
            sector_encontrado = resultado.iloc[0]['Sector']
            st.success(f"**Partida ingresada:** {busqueda_limpia}")
            st.metric(label="Sector Comercial", value=sector_encontrado)
        else:
            st.warning(f"No se encontró información para la partida **{busqueda_limpia}**.")

except Exception as e:
    st.error(f"Error al cargar el archivo de datos: {e}")
