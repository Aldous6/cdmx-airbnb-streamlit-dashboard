import pandas as pd
import numpy as np

# --- CONFIGURACIÓN ---
FILE_NAME = "CDMX_Airbnb.csv" # Asegúrate de que tu archivo se llame así

print(f"📂 Cargando {FILE_NAME}...")

try:
    df = pd.read_csv(FILE_NAME)
    print("✅ ¡Archivo cargado con éxito!")
except FileNotFoundError:
    print("❌ ERROR: No encuentro el archivo. Revisa el nombre o la carpeta.")
    exit()

# --- 1. RADIOGRAFÍA DE COLUMNAS ---
print("\n--- 📋 Columnas Disponibles ---")
print(df.columns.tolist())

# Verificamos si tenemos las variables de 'Reviews' (Popularidad)
has_reviews = 'number_of_reviews' in df.columns
print(f"\n¿Tenemos datos de reseñas (Popularidad)? -> {'✅ SÍ' if has_reviews else '⚠️ NO (Adaptaremos el mapa)'}")

# --- 2. LIMPIEZA INICIAL (CLEANING) ---
print("\n--- 🧹 Iniciando Limpieza ---")
original_count = len(df)

# A. Limpieza de Precio
# A veces el precio viene como texto "$1,200". Esto lo arregla por si acaso.
if df['price'].dtype == 'O': 
    df['price'] = df['price'].astype(str).str.replace(r'[$,]', '', regex=True)
    df['price'] = pd.to_numeric(df['price'], errors='coerce')

# Eliminamos precios $0 y nulos
df = df[df['price'] > 0]

# B. Outliers (Top 1% más caro)
# En CDMX hay penthouses en Polanco de 50,000 pesos que rompen el promedio. Los quitamos.
price_cap = df['price'].quantile(0.99)
df = df[df['price'] < price_cap]

print(f"💰 Se eliminaron propiedades con precio mayor a ${price_cap:,.0f} (Top 1% outliers)")

# --- 3. INGENIERÍA DE FEATURES (CDMX EDITION) ---
print("\n--- 📐 Calculando Distancias ---")

# Referencia: El Ángel de la Independencia (El corazón turístico)
center_lat, center_lon = 19.4270, -99.1677

# Fórmula de Haversine (Matemáticas para calcular distancia en esfera)
R = 6371
phi1, phi2 = np.radians(df['latitude']), np.radians(center_lat)
dphi = np.radians(center_lat - df['latitude'])
dlambda = np.radians(center_lon - df['longitude'])
a = np.sin(dphi/2)**2 + np.cos(phi1) * np.cos(phi2) * np.sin(dlambda/2)**2
c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))

df['distance_to_angel'] = R * c

# --- 4. REPORTE FINAL ---
print("\n--- 🏁 REPORTE FINAL ---")
print(f"Filas originales: {original_count}")
print(f"Filas limpias:    {len(df)}")
print(f"Datos retenidos:  {len(df)/original_count*100:.2f}%")
print("\nEjemplo de datos procesados:")
print(df[['neighbourhood', 'price', 'distance_to_angel']].head())