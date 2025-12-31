# 🇲🇽 CDMX Airbnb Comparador (Streamlit)

Dashboard interactivo para **comparar opciones de Airbnb en CDMX** con filtros por alcaldía, tipo de alojamiento, presupuesto y reseñas; además de **mapas** (unificado o por zona) y análisis visual (seguridad vs precio, boxplot de precios y top populares).

> Hecho con **Streamlit + Plotly + Pandas**.

---

## ✨ Qué hace (features)

- **Planeador de viaje**:
  - Noches (para estimar costo total del viaje)
  - Filtro por **Alcaldía**
  - Filtro por **tipo de alojamiento** (room_type)
  - **Rango de precios** por noche
  - Mínimo de **reseñas**
- **KPIs**:
  - Número de opciones filtradas
  - Precio promedio por noche
  - **Costo estimado** por N noches
  - *Seguridad promedio* (si existe `security_index` en el dataset)
- **Mapa interactivo**:
  - ✅ **Mapa unificado** con “heat” por precio
  - ✅ **Mapas separados por alcaldía** (toggle) con escala consistente
- **Análisis** (tabs):
  - Seguridad vs Precio (scatter) *(si existe `security_index`)*
  - Rango de precios por alcaldía (boxplot)
  - Top 10 más populares (por `number_of_reviews`)

---

## 🧱 Estructura del repo (recomendada)

```txt
.
├─ app.py
├─ check.py
├─ CDMX_Airbnb.csv
├─ requirements.txt
└─ README.md
