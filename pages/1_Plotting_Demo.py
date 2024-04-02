import streamlit as st
import pandas as pd
import altair as alt

# Título de la aplicación
st.title('Análisis Financiero de Certificados de Depósito con Altair')

# Carga de datos
uploaded_file = st.file_uploader("Sube un archivo Excel con datos de CDs", type=['xlsx', 'xls', 'xlsm'])
if uploaded_file is not None:
    df = pd.read_excel(uploaded_file, sheet_name='Hoja1')
    df['Fecha Compra'] = pd.to_datetime(df['Fecha Compra'])
    df['Vencimiento'] = pd.to_datetime(df['Vencimiento'])
    
    # Ajustes para el análisis
    df['Rendimiento (%)'] = df['Tasa'] * 100  # Asume que la tasa está en formato decimal en el Excel
    df['Año Vencimiento'] = df['Vencimiento'].dt.year
    
    # Análisis de Rendimiento con Altair
    chart_rendimiento = alt.Chart(df).mark_bar().encode(
        alt.X('Rendimiento (%):Q', bin=True, title='Rendimiento (%)'),
        alt.Y('count()', title='Número de CDs'),
        tooltip=[alt.Tooltip('count()', title='Número de CDs'), 'Rendimiento (%)']
    ).properties(title='Distribución del Rendimiento de los CDs')
    
    st.altair_chart(chart_rendimiento, use_container_width=True)
    
    # Análisis de Vencimiento con Altair
    chart_vencimiento = alt.Chart(df).mark_bar().encode(
        alt.X('Año Vencimiento:O', title='Año de Vencimiento'),
        alt.Y('count()', title='Número de CDs'),
        tooltip=[alt.Tooltip('count()', title='Número de CDs'), 'Año Vencimiento']
    ).properties(title='Distribución de Vencimientos por Año')
    
    st.altair_chart(chart_vencimiento, use_container_width=True)

    # Asegurándonos de que 'Rating' es de tipo string para el gráfico
    df['Rating'] = df['Rating'].astype(str)
    
    # Clasificación por Rating con Altair
    chart_rating = alt.Chart(df).mark_bar().encode(
        alt.X('Rating:N', sort='-y', title='Rating'),
        alt.Y('count():Q', title='Número de CDs'),
        color='Rating:N',
        tooltip=[alt.Tooltip('count()', title='Número de CDs'), 'Rating:N']
    ).properties(title='Clasificación de CDs por Rating')
    
    st.altair_chart(chart_rating, use_container_width=True)

    # Preparando los datos
    df['A descuento'] = df['A descuento'].map({1: 'Con Descuento', 0: 'Sin Descuento'})
    df['Rendimiento (%)'] = df['Tasa'] * 100  # Asume que la tasa está en formato decimal en el Excel
    
    # Análisis de Impacto del Descuento con Altair
    chart_descuento = alt.Chart(df).mark_bar().encode(
        alt.X('A descuento:N', title='Comprado a Descuento'),
        alt.Y('mean(Rendimiento (%)):Q', title='Rendimiento Medio (%)'),
        color='A descuento:N',
        tooltip=[alt.Tooltip('mean(Rendimiento (%))', title='Rendimiento Medio (%)'), 'A descuento:N']
    ).properties(title='Impacto del Descuento en el Rendimiento Medio de los CDs')
    
    st.altair_chart(chart_descuento, use_container_width=True)

    # Asegurando que 'Sector' y 'Tasa' estén en el formato correcto
    df['Sector'] = df['Sector'].astype(str)
    df['Rendimiento (%)'] = df['Tasa'] * 100  # Asume que la tasa está en formato decimal en el Excel
    
    # Análisis de Rendimiento por Sector con Altair
    chart_sector = alt.Chart(df).mark_bar().encode(
        alt.X('Sector:N', sort='-y', title='Sector'),
        alt.Y('mean(Rendimiento (%)):Q', title='Rendimiento Medio (%)'),
        color=alt.Color('Sector:N', legend=alt.Legend(title="Sector")),
        tooltip=[alt.Tooltip('mean(Rendimiento (%))', title='Rendimiento Medio (%)'), 'Sector:N']
    ).properties(title='Rendimiento Medio de los CDs por Sector')
    
    st.altair_chart(chart_sector, use_container_width=True)

