import streamlit as st
import pandas as pd
import altair as alt

# Título de la aplicación
st.title('Análisis Financiero Mejorado de Certificados de Depósito con Altair')

# Carga de datos
uploaded_file = st.file_uploader("Sube un archivo Excel con datos de CDs", type=['xlsx', 'xls', 'xlsm'])
if uploaded_file is not None:
    df = pd.read_excel(uploaded_file, sheet_name='Hoja1')
    df['Fecha Compra'] = pd.to_datetime(df['Fecha Compra'])
    df['Vencimiento'] = pd.to_datetime(df['Vencimiento'])
    
    # Ajustes para el análisis
    df['Rendimiento (%)'] = df['Tasa'] * 100  # Asume que la tasa está en formato decimal en el Excel
    df['Año Vencimiento'] = df['Vencimiento'].dt.year
    df['A descuento'] = df['A descuento'].map({1: 'Con Descuento', 0: 'Sin Descuento'})
    df['Sector'] = df['Sector'].astype(str)
    df['Rating'] = df['Rating'].astype(str)
    
    # Filtros para análisis
    sector_options = st.multiselect("Selecciona sectores para analizar:", options=df['Sector'].unique(), default=df['Sector'].unique())
    if sector_options:
        df = df[df['Sector'].isin(sector_options)]
    
    year_options = st.multiselect("Selecciona años de vencimiento para analizar:", options=df['Año Vencimiento'].unique(), default=df['Año Vencimiento'].unique())
    if year_options:
        df = df[df['Año Vencimiento'].isin(year_options)]
    
    discount_option = st.radio("Selecciona CDs comprados a descuento o no:", options=['Todos', 'Con Descuento', 'Sin Descuento'], index=0)
    if discount_option == 'Con Descuento':
        df = df[df['A descuento'] == 'Con Descuento']
    elif discount_option == 'Sin Descuento':
        df = df[df['A descuento'] == 'Sin Descuento']
    
    st.write("### Datos Filtrados", df)
    
    # Información sobre los análisis
    st.markdown("""
    **Análisis de Distribución del Rendimiento**: Este gráfico muestra cómo se distribuye el rendimiento de los CDs. 
    Es útil para identificar rangos de rendimiento comunes.
    """)
    
    # Gráfico de Rendimiento
    chart_rendimiento = alt.Chart(df).mark_bar().encode(
        alt.X('Rendimiento (%):Q', bin=True, title='Rendimiento (%)'),
        alt.Y('count()', title='Número de CDs'),
        tooltip=[alt.Tooltip('count()', title='Número de CDs'), 'Rendimiento (%)']
    ).properties(title='Distribución del Rendimiento de los CDs')
    st.altair_chart(chart_rendimiento, use_container_width=True)
    
    st.markdown("""
    **Análisis de Distribución de Vencimientos por Año**: Este gráfico ayuda a visualizar en qué años vencen más CDs, 
    lo cual es importante para la planificación de la liquidez y reinversión.
    """)
    
    # Gráfico de Vencimiento
    chart_vencimiento = alt.Chart(df).mark_bar().encode(
        alt.X('Año Vencimiento:O', title='Año de Vencimiento'),
        alt.Y('count()', title='Número de CDs'),
        tooltip=[alt.Tooltip('count()', title='Número de CDs'), 'Año Vencimiento']
    ).properties(title='Distribución de Vencimientos por Año')
    st.altair_chart(chart_vencimiento, use_container_width=True)
    
    st.markdown("""
    **Clasificación de CDs por Rating**: Este análisis muestra el número de CDs por categoría de rating crediticio, 
    ofreciendo una visión del perfil de riesgo del portafolio.
    """)
    
    # Gráfico de Rating
    chart_rating = alt.Chart(df).mark_bar().encode(
        alt.X('Rating:N', sort='-y', title='Rating'),
        alt.Y('count():Q', title='Número de CDs'),
        color='Rating:N',
        tooltip=[alt.Tooltip('count()', title='Número de CDs'), 'Rating:N']
    ).properties(title='Clasificación de CDs por Rating')
    st.altair_chart(chart_rating, use_container_width=True)

    st.markdown("""
    **Impacto del Descuento en el Rendimiento Medio**: Compara el rendimiento medio de los CDs comprados con descuento 
    versus sin descuento, para evaluar si esta estrategia impacta positivamente el rendimiento.
    """)
    
    # Gráfico de Impacto del Descuento
    chart_descuento = alt.Chart(df).mark_bar().encode(
        alt.X('A descuento:N', title='Comprado a Descuento'),
        alt.Y('mean(Rendimiento (%)):Q', title='Rendimiento Medio (%)'),
        color='A descuento:N',
        tooltip=[alt.Tooltip('mean(Rendimiento (%))', title='Rendimiento Medio (%)'), 'A descuento:N']
    ).properties(title='Impacto del Descuento en el Rendimiento Medio de los CDs')
    st.altair_chart(chart_descuento, use_container_width=True)
    
    st.markdown("""
    **Rendimiento Medio de los CDs por Sector**: Este análisis ofrece insights sobre qué sectores están ofreciendo mejores 
    tasas de rendimiento, lo cual puede informar decisiones de inversión futuras.
    """)
    
    # Gráfico de Rendimiento por Sector
    chart_sector = alt.Chart(df).mark_bar().encode(
        alt.X('Sector:N', sort='-y', title='Sector'),
        alt.Y('mean(Rendimiento (%)):Q', title='Rendimiento Medio (%)'),
        color=alt.Color('Sector:N', legend=alt.Legend(title="Sector")),
        tooltip=[alt.Tooltip('mean(Rendimiento (%))', title='Rendimiento Medio (%)'), 'Sector:N']
    ).properties(title='Rendimiento Medio de los CDs por Sector')
    st.altair_chart(chart_sector, use_container_width=True)
