import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title="Proyecto Clima Chile", layout="wide")
st.title("🌡️ Análisis de Temperaturas - Chile")

url = "https://datos.gob.cl/uploads/recursos/temperaturasDiariasPorEstaciones2012.csv"
ruta_csv = Path("data/temperaturasDiariasPorEstaciones2012.csv")
ruta_csv.parent.mkdir(parents=True, exist_ok=True) 
response = requests.get(url)
if response.status_code == 200:
    with open(ruta_csv, "wb") as f:
        f.write(response.content)
    print(f"Archivo descargado y guardado en {ruta_csv}")
else:
    print(f"No se pudo descargar el archivo. Código de estado: {response.status_code}")

ruta_csv = Path("data/temperaturasDiariasPorEstaciones2012.csv")
df = pd.read_csv(ruta_csv, sep=";")
df = df.rename(columns={"Año": "year", "Mes": "month", "Dia": "day"})
df["Fecha"] = pd.to_datetime(df[["year", "month", "day"]])

# Vista previa de datos
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
df_filtrado = df_estacion[
    (df_estacion["Fecha"] >= pd.to_datetime(rango_fechas[0])) &
    (df_estacion["Fecha"] <= pd.to_datetime(rango_fechas[1]))
]

# Gráfico interactivo de temperaturas
st.subheader("📈 Gráfico de Temperaturas")
fig = px.line(
    df_filtrado,
    x="Fecha",
    y=["TMinima", "TMaxima"],
    labels={"value": "Temperatura (°C)", "Fecha": "Fecha"},
    title=f"Temperaturas en {estacion} del {rango_fechas[0]} al {rango_fechas[1]}"
)
st.plotly_chart(fig, use_container_width=True)

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

# Descargar CSV filtrado
st.subheader("💾 Descargar datos filtrados")
csv = df_filtrado.to_csv(index=False).encode('utf-8')
st.download_button(
    "Descargar CSV filtrado",
    data=csv,
    file_name="datos_filtrados.csv",
    mime="text/csv"
)

# Promedios mensuales
st.subheader("📊 Promedios mensuales")
df_filtrado["month"] = df_filtrado["Fecha"].dt.month
promedios_mes = df_filtrado.groupby("month")[["TMinima", "TMaxima"]].mean().reset_index()
promedios_mes = promedios_mes.rename(columns={"TMinima": "Temperatura Mínima", "TMaxima": "Temperatura Máxima", "month": "Mes"})
st.line_chart(promedios_mes.set_index("Mes"))


# Días con temperaturas extremas
st.subheader("🔥 Días con Mayor temperatura temperaturas (TMax > 25°C)")
extremos = df_filtrado[df_filtrado["TMaxima"] > 25]
if not extremos.empty:
    st.dataframe(extremos[["Fecha", "TMinima", "TMaxima"]])
else:
    st.write("No hay días con temperaturas mayores a 25°C en el rango seleccionado.")
