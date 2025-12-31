import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="CDMX Airbnb Master", page_icon="🇲🇽", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0e1117; }
    h1 { color: #00f5d4; font-family: 'Helvetica Neue', sans-serif; }
    h2, h3 { color: #f15bb5; }
    div.stMetric { 
        background-color: #1e1e1e; 
        padding: 15px; 
        border-radius: 10px; 
        border: 1px solid #333; 
        box-shadow: 2px 2px 5px rgba(0,0,0,0.5);
    }
    div[data-testid="metric-container"]:nth-child(3) {
        border: 1px solid #f15bb5;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. DATA ENGINE ---
@st.cache_data
def load_data():
    df = pd.read_csv("CDMX_Airbnb.csv")
    
    # Limpieza
    if df['price'].dtype == 'O':
        df['price'] = df['price'].astype(str).str.replace(r'[$,]', '', regex=True)
        df['price'] = pd.to_numeric(df['price'], errors='coerce')
    
    if 'number_of_reviews' in df.columns:
        df['number_of_reviews'] = df['number_of_reviews'].fillna(0)
    
    df = df[df['price'] > 0]
    df = df[df['price'] < df['price'].quantile(0.99)]
    
    center_lat, center_lon = 19.4270, -99.1677
    R = 6371
    phi1, phi2 = np.radians(df['latitude']), np.radians(center_lat)
    dphi = np.radians(center_lat - df['latitude'])
    dlambda = np.radians(center_lon - df['longitude'])
    a = np.sin(dphi/2)**2 + np.cos(phi1) * np.cos(phi2) * np.sin(dlambda/2)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
    df['distancia_angel_km'] = R * c
    
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"🚨 Error: {e}")
    st.stop()

# --- 3. BARRA LATERAL ---
st.sidebar.title("🧮 Planeador de Viaje")
st.sidebar.markdown("---")

# Cotizador
st.sidebar.subheader("📅 Duración")
noches = st.sidebar.number_input("Noches:", min_value=1, value=3, step=1)

# Filtro Alcaldía
st.sidebar.markdown("---")
st.sidebar.subheader("📍 Ubicación")
alcaldias_list = sorted(list(df['neighbourhood'].unique()))

selected_alcaldias = st.sidebar.multiselect(
    "Selecciona Alcaldías:", 
    alcaldias_list,
    default=alcaldias_list[:2] 
)

# EL CONTROL CORREGIDO
separar_mapas = st.sidebar.checkbox("🪟 Ver mapas individuales", value=False)

# Otros filtros
st.sidebar.markdown("---")
room_types_list = list(df['room_type'].unique())
selected_rooms = st.sidebar.multiselect("🏠 Tipo de Alojamiento:", room_types_list, default=room_types_list)

min_p, max_p = int(df['price'].min()), int(df['price'].max())
price_range = st.sidebar.slider("💰 Presupuesto Noche ($):", min_p, max_p, (500, 5000))

min_reviews = st.sidebar.slider("⭐ Mínimo Reseñas:", 0, 200, 0)

# --- 4. LÓGICA DE FILTRADO ---
if not selected_alcaldias:
    alcaldias_filter = df['neighbourhood'].isin(alcaldias_list)
else:
    alcaldias_filter = df['neighbourhood'].isin(selected_alcaldias)

filtered_df = df[
    alcaldias_filter &
    (df['price'] >= price_range[0]) & 
    (df['price'] <= price_range[1]) &
    (df['number_of_reviews'] >= min_reviews) &
    (df['room_type'].isin(selected_rooms))
]

# --- 5. DASHBOARD ---
st.title("🇲🇽 CDMX Airbnb Comparador")

# KPIs
promedio_noche = filtered_df['price'].mean() if not filtered_df.empty else 0
total_viaje = promedio_noche * noches

col1, col2, col3, col4 = st.columns(4)
col1.metric("Opciones", f"{len(filtered_df):,}")
col2.metric("Precio Promedio", f"${promedio_noche:,.0f} MXN")
col3.metric(f"💰 Costo x {noches} Noches", f"${total_viaje:,.0f} MXN", delta="Estimado", delta_color="off")
col4.metric("Seguridad Promedio", f"{filtered_df['security_index'].mean():.2f}" if 'security_index' in df.columns and not filtered_df.empty else "N/A")

# --- SECCIÓN DE MAPAS (SOLUCIÓN ROBUSTA) ---
if not filtered_df.empty:
    hover_data = {"price": True, "neighbourhood": True, "room_type": True, "security_index": True}
    
    # OPCIÓN A: MAPA UNIFICADO (Lo clásico)
    if not separar_mapas:
        # Calcular centro dinámico
        center_coords = {"lat": filtered_df['latitude'].mean(), "lon": filtered_df['longitude'].mean()}
        zoom_level = 11 if len(selected_alcaldias) > 1 else 13
        
        fig_map = px.scatter_mapbox(filtered_df, 
                                lat="latitude", lon="longitude", 
                                color="price", 
                                color_continuous_scale="Plasma", # Mapa de calor PRECIOS
                                size=filtered_df["number_of_reviews"] + 5, 
                                size_max=25,
                                zoom=zoom_level,
                                center=center_coords,
                                mapbox_style="carto-darkmatter",
                                hover_name="name",
                                hover_data=hover_data,
                                height=600)
        fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        st.plotly_chart(fig_map, use_container_width=True)
    
    # OPCIÓN B: MAPAS SEPARADOS (Iteración manual)
    else:
        # Si no seleccionó nada específico, usamos todas las alcaldías presentes en el filtro
        zonas_a_mostrar = selected_alcaldias if selected_alcaldias else filtered_df['neighbourhood'].unique()
        
        # Columnas para organizar los mapas en rejilla (2 por fila)
        cols = st.columns(2)
        
        for i, zona in enumerate(zonas_a_mostrar):
            # Filtramos datos SOLO para esta zona
            df_zona = filtered_df[filtered_df['neighbourhood'] == zona]
            
            if not df_zona.empty:
                # Usamos la columna correspondiente (0 o 1)
                with cols[i % 2]:
                    st.markdown(f"### 📍 {zona}")
                    center_coords = {"lat": df_zona['latitude'].mean(), "lon": df_zona['longitude'].mean()}
                    
                    fig_zona = px.scatter_mapbox(df_zona, 
                                            lat="latitude", lon="longitude", 
                                            color="price", 
                                            color_continuous_scale="Plasma", # Mantiene escala de precio
                                            size=df_zona["number_of_reviews"] + 5, 
                                            size_max=25,
                                            zoom=12.5, # Zoom cercano fijo
                                            center=center_coords,
                                            mapbox_style="carto-darkmatter",
                                            hover_name="name",
                                            hover_data=hover_data,
                                            height=400) # Mapas un poco más chicos
                    fig_zona.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
                    # Truco para que la escala de colores sea consistente entre mapas
                    fig_zona.update_layout(coloraxis=dict(cmin=min_p, cmax=max_p))
                    
                    st.plotly_chart(fig_zona, use_container_width=True)

else:
    st.warning("🔎 Selecciona al menos una alcaldía.")

# --- 6. ANÁLISIS ---
st.markdown("---")
st.subheader("📊 Comparativa de Zonas")

if not filtered_df.empty:
    tab1, tab2, tab3 = st.tabs(["🛡️ Seguridad vs Precio", "📦 Rango de Precios", "💎 Top Populares"])

    with tab1:
        if 'security_index' in df.columns:
            fig_scatter = px.scatter(filtered_df, x="security_index", y="price", color="neighbourhood", 
                                     size="number_of_reviews", title="Seguridad vs Costo")
            fig_scatter.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="white")
            st.plotly_chart(fig_scatter, use_container_width=True)

    with tab2:
        fig_box = px.box(filtered_df, x="neighbourhood", y="price", color="neighbourhood", points="outliers")
        fig_box.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="white", showlegend=False)
        st.plotly_chart(fig_box, use_container_width=True)

    with tab3:
        top_reviews = filtered_df.sort_values(by="number_of_reviews", ascending=False).head(10)
        fig_bar = px.bar(top_reviews, x="number_of_reviews", y="name", orientation='h', color="neighbourhood")
        fig_bar.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="white")
        st.plotly_chart(fig_bar, use_container_width=True)