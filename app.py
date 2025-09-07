import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

st.set_page_config(page_title="Proyecto Clima Chile", layout="wide")
st.title("🌡️ Análisis de Temperaturas - Chile")

# Cargar CSV
ruta_csv = Path("data/temperaturasDiariasPorEstaciones2012.csv")
df = pd.read_csv(ruta_csv, sep=";")
df = df.rename(columns={"Año": "year", "Mes": "month", "Dia": "day"})
df["Fecha"] = pd.to_datetime(df[["year", "month", "day"]])

st.subheader("Vista previa de los datos")
st.dataframe(df.head())

# Selección de estación
estacion = st.selectbox("Selecciona una estación", df["Nombre Estacion"].unique(), key="estacion")
df_estacion = df[df["Nombre Estacion"] == estacion]

# Selección de rango de fechas
fecha_min = df_estacion["Fecha"].min()
fecha_max = df_estacion["Fecha"].max()
rango_fechas = st.date_input(
    "Selecciona un rango de fechas",
    value=(fecha_min, fecha_max),
    min_value=fecha_min,
    max_value=fecha_max
)

# Filtrar según rango
df_filtrado = df_estacion[(df_estacion["Fecha"] >= pd.to_datetime(rango_fechas[0])) &
                          (df_estacion["Fecha"] <= pd.to_datetime(rango_fechas[1]))]

# Gráfico
fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(df_filtrado["Fecha"], df_filtrado["TMinima"], label="TMin", marker="o", color="blue")
ax.plot(df_filtrado["Fecha"], df_filtrado["TMaxima"], label="TMax", marker="o", color="red")
ax.set_title(f"Temperaturas en {estacion} del {rango_fechas[0]} al {rango_fechas[1]}")
ax.set_xlabel("Fecha")
ax.set_ylabel("Temperatura (°C)")
ax.legend()
ax.grid(True)
plt.xticks(rotation=45)
fig.tight_layout()
st.pyplot(fig)

# Estadísticas
st.subheader("📊 Estadísticas de la estación seleccionada")

estadisticas = df_filtrado[["TMinima", "TMaxima"]].describe()

# Traducir columnas y filas
estadisticas = estadisticas.rename(
    index={
        "count": "Cantidad",
        "mean": "Promedio",
        "std": "Desviación Estándar",
        "min": "Mínimo",
        "25%": "Percentil 25",
        "50%": "Percentil 50",
        "75%": "Percentil 75",
        "max": "Máximo"
    },
    columns={
        "TMinima": "Temperatura Mínima",
        "TMaxima": "Temperatura Máxima"
    }
)

st.write(estadisticas)
