import streamlit as st
import pandas as pd
from datetime import datetime
import numpy as np

# Configura la página
st.set_page_config(page_title="Análisis Financiero", layout="wide")

# Título de la aplicación
st.title('Análisis Financiero: CDs y Bonos')

# Subida de archivo y selección de hoja
uploaded_file = st.file_uploader("Elige un archivo Excel con datos de CDs y Bonos", type=['xlsx', 'xls', 'xlsm'])
if uploaded_file:
    sheet = st.selectbox("Selecciona la hoja del Excel", pd.ExcelFile(uploaded_file).sheet_names)

    # Cargar y mostrar el DataFrame
    df = pd.read_excel(uploaded_file, sheet_name=sheet)
    st.write(df)

    # Espacio para más lógica y visualizaciones...

if uploaded_file is not None:
    correlativo = st.number_input("Ingrese el número de correlativo para buscar", min_value=0, value=0, step=1)
    if correlativo > 0:
        filtered_data = df[df['Correlativo'] == correlativo]
        if not filtered_data.empty:
            st.write("Resultado de la Búsqueda:", filtered_data)
        else:
            st.write("No se encontraron registros con ese correlativo.")
if uploaded_file is not None and 'Fecha Compra' in df.columns and 'Vencimiento' in df.columns:
    if st.button('Calcular Duración de CDs'):
        df['Fecha Compra'] = pd.to_datetime(df['Fecha Compra'])
        df['Vencimiento'] = pd.to_datetime(df['Vencimiento'])
        df['Duración (días)'] = (df['Vencimiento'] - df['Fecha Compra']).dt.days
        st.write(df[['Correlativo', 'Fecha Compra', 'Vencimiento', 'Duración (días)']])
    
# Funciones de análisis financiero
    def buscar_correlativo(dataframe, obtener_correlativo):
        return dataframe[dataframe['Correlativo'] == obtener_correlativo]

    def calcular_valor_venta(dataframe, obtener_correlativo):
        resultado_correlativo = buscar_correlativo(dataframe, obtener_correlativo)
        if not resultado_correlativo.empty:
            valor_nominal = float(resultado_correlativo['Valor nominal'].iloc[0].replace(',', ''))
            tasa = float(resultado_correlativo['Tasa'].iloc[0].replace(',', ''))
            fecha_compra = pd.to_datetime(resultado_correlativo['Fecha Compra'].iloc[0])
            fecha_liquidacion = pd.to_datetime(resultado_correlativo['Fecha Liquidación'].iloc[0])
            dias_vigencia = (fecha_liquidacion - fecha_compra).days
            valor_vendido = (valor_nominal * tasa * dias_vigencia) / 360
            return valor_vendido
        return 0

    if 'Fecha Compra' in df.columns and 'Vencimiento' in df.columns:
        correlativo = st.number_input("Ingrese el número de correlativo para estimaciones", min_value=0, value=0, step=1)
        if correlativo > 0:
            valor_venta = calcular_valor_venta(df, correlativo)
            st.write(f"Estimación del valor de venta para el correlativo {correlativo}: {valor_venta:.2f}")