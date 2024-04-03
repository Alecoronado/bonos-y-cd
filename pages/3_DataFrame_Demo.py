import streamlit as st
import pandas as pd
from pandas import Timestamp, to_datetime

# Subir y leer el Excel
def cargar_excel():
    uploaded_file = st.sidebar.file_uploader("Seleccione el archivo Excel con los datos de CD", type=["xlsx"])
    if uploaded_file is not None:
        dataframe = pd.read_excel(uploaded_file)
        return dataframe
    else:
        return None

dataframe_cd = cargar_excel()

if dataframe_cd is not None:
    # Función para buscar por nombre de instrumento
    def buscar_instrumento(nombre_instrumento):
        resultado_busqueda_cd = dataframe_cd[dataframe_cd['Nombre'].str.upper() == nombre_instrumento.upper()]
        return resultado_busqueda_cd

    # Función para buscar datos de correlativo
    def buscar_correlativo(obtener_correlativo):
        resultado_busqueda_correlativo = dataframe_cd[dataframe_cd['Correlativo'] == obtener_correlativo]
        return resultado_busqueda_correlativo

    # Función para obtener la vigencia del instrumento
    def obtener_vigencia_instrumento(obtener_correlativo):
        resultado_correlativo = buscar_correlativo(obtener_correlativo)
        if not resultado_correlativo.empty:
            capturar_fecha_compra = pd.to_datetime(resultado_correlativo['Fecha Compra'])
            capturar_fecha_vencimiento = pd.to_datetime(resultado_correlativo['Vencimiento'])
            vigencia_instrumento = (capturar_fecha_vencimiento - capturar_fecha_compra).dt.days
            return vigencia_instrumento.iloc[0]

    # Función para obtener la liquidez del instrumento
    def obtener_liquidez_instrumento(obtener_correlativo):
        resultado_correlativo = buscar_correlativo(obtener_correlativo)
        if not resultado_correlativo.empty:
            capturar_fecha_compra = pd.to_datetime(resultado_correlativo['Fecha Compra'])
            capturar_fecha_liquidez = pd.to_datetime(resultado_correlativo['Fecha Liquidación'])
            liquidez_instrumento = (capturar_fecha_liquidez - capturar_fecha_compra).dt.days
            return liquidez_instrumento.iloc[0]

    # Función para calcular el valor estimado de venta del bono
    def obtener_ingresos_vencidos(obtener_correlativo):
        resultado_correlativo = buscar_correlativo(obtener_correlativo)
        dias_vigencia = obtener_vigencia_instrumento(obtener_correlativo) - obtener_liquidez_instrumento(obtener_correlativo)
        if not resultado_correlativo.empty:
            obtener_valor_nominal = resultado_correlativo['Valor nominal'].iloc[0]
            obtener_tasa = resultado_correlativo['Tasa'].iloc[0]
            valor_vendido = (obtener_valor_nominal * obtener_tasa * dias_vigencia) / 360
            return valor_vendido

    # Función para calcular el valor de devengamiento diario
    def obtener_devengamiento_diario(obtener_correlativo):
        capturar_ingresos_vendidos = obtener_ingresos_vencidos(obtener_correlativo)
        dias_vigencia = obtener_vigencia_instrumento(obtener_correlativo) - obtener_liquidez_instrumento(obtener_correlativo)
        resultado_devengamiento = capturar_ingresos_vendidos / dias_vigencia
        return resultado_devengamiento

    # Función para generar DataFrame con fechas y devengamiento diario
    def generar_dias_devengamiento(obtener_correlativo):
        resultado_correlativo = buscar_correlativo(obtener_correlativo)
        if not resultado_correlativo.empty:
            lista_devengamiento = []
            contar_dias = 0
            vigencia_instrumento = obtener_vigencia_instrumento(obtener_correlativo)
            liquidez_instrumento = obtener_liquidez_instrumento(obtener_correlativo)
            fecha_compra = resultado_correlativo['Fecha Compra'].iloc[0]
            valor_nominal = resultado_correlativo['Valor nominal'].iloc[0]
            devengamiento = obtener_devengamiento_diario(obtener_correlativo)
            incrementar_devengamiento = valor_nominal

            while contar_dias < vigencia_instrumento:
                fecha_actual = fecha_compra + pd.DateOffset(days=contar_dias)

                if contar_dias < liquidez_instrumento:
                    lista_devengamiento.append({'Fecha': fecha_actual, 'Devengamiento x dia': round(valor_nominal, 2)})
                else:
                    incrementar_devengamiento += devengamiento
                    lista_devengamiento.append({'Fecha': fecha_actual, 'Devengamiento x dia': round(incrementar_devengamiento, 2)})
                contar_dias += 1

            dataframe_devengamiento = pd.DataFrame(lista_devengamiento)
            pd.options.display.float_format = '{:,.2f}'.format
            return dataframe_devengamiento

    # Interfaz de usuario para buscar instrumento
    st.subheader("Buscar Instrumento")
    nombre_instrumento = st.text_input("Ingrese el nombre del instrumento CD que desea buscar:")
    if st.button("Buscar Instrumento"):
        resultado = buscar_instrumento(nombre_instrumento)
        if not resultado.empty:
            st.write("El instrumento ingresado es:", nombre_instrumento)
            st.dataframe(resultado)
        else:
            st.write("Instrumento no encontrado.")

    # Interfaz de usuario para ingresar número correlativo y mostrar resultados
    st.subheader("Datos del Correlativo")
    numero_correlativo = st.number_input("Ingrese el número de correlativo", min_value=1, format='%d')
    if st.button("Mostrar Datos"):
        correlativo_info = buscar_correlativo(numero_correlativo)
        if not correlativo_info.empty:
            st.dataframe(correlativo_info)
            st.write("La duración del bono es de:", obtener_vigencia_instrumento(numero_correlativo), "días, desde su momento de compra.")
            st.write("Tiene:", obtener_liquidez_instrumento(numero_correlativo), "días de liquidez.")
            ingresos_vendidos = obtener_ingresos_vencidos(numero_correlativo)
            st.write(f"Los ingresos vencidos fueron: {ingresos_vendidos:,.2f}")
            devengamiento_diario = obtener_devengamiento_diario(numero_correlativo)
            st.write(f"Los devengamientos diarios serían de: {devengamiento_diario:,.2f}")
            st.dataframe(generar_dias_devengamiento(numero_correlativo))

    # Función para filtrar CDs por rango de fecha
    def filtrar_cd_rango_fecha_indicada(fecha):
        convertir_fecha = to_datetime(fecha, dayfirst=True)
        cd_encontrados = []

        for index, fila in dataframe_cd.iterrows():
            fecha_compra = Timestamp(fila['Fecha Compra'])
            fecha_vencimiento = Timestamp(fila['Vencimiento'])

            if convertir_fecha <= fecha_vencimiento:
                if fecha_compra < convertir_fecha:
                    cd_encontrados.append(fila)
                else:
                    break

        cd_encontrados = pd.DataFrame(cd_encontrados)
        return cd_encontrados

    # Función para calcular el monto devengado hasta una fecha indicada
    def monto_devengado_fecha_indicada(fecha_compra, fecha_liquidacion, fecha_vencimiento, valor_nominal, tasa, fecha_ingresada):
        dias_liquidez = abs(fecha_compra - fecha_liquidacion).days
        duracion_instrumento = abs(fecha_compra - fecha_vencimiento).days
        
        dias_vencidos = abs(dias_liquidez - duracion_instrumento)
        ingresos_vencidos = (valor_nominal * tasa * dias_vencidos) / 360
        devengamiento_diario = ingresos_vencidos / dias_vencidos

        fecha_actual = fecha_compra
        monto_devengado = valor_nominal
        while fecha_actual < fecha_ingresada:
            if fecha_actual >= fecha_liquidacion:
                monto_devengado += devengamiento_diario
            fecha_actual += pd.DateOffset(days=1)

        return round(monto_devengado, 2)

    # Función para calcular el total de la cartera de CDs a una fecha seleccionada
    def total_cartera_cd_a_fecha_seleccionada(fecha):
        convertir_fecha = to_datetime(fecha, dayfirst=True)
        lista_montos = []
        df_filtrado = filtrar_cd_rango_fecha_indicada(fecha)

        for index, fila in df_filtrado.iterrows():
            fecha_compra = Timestamp(fila['Fecha Compra'])
            fecha_liquidacion = Timestamp(fila['Fecha Liquidación'])
            fecha_vencimiento = Timestamp(fila['Vencimiento'])
            valor_nominal = fila['Valor nominal']
            tasa = fila['Tasa']

            monto_fecha_ingresada = monto_devengado_fecha_indicada(
                fecha_compra, fecha_liquidacion, fecha_vencimiento, valor_nominal, tasa, fecha_ingresada=convertir_fecha)
            
            lista_montos.append(monto_fecha_ingresada)
        resultado_suma = sum(lista_montos)
        return resultado_suma

    # Widgets para entrada de fecha
    fecha_busqueda = st.date_input("Ingrese la fecha de búsqueda (DD-MM-YYYY):")
    
    # Botones para ejecutar funciones y mostrar resultados
    if st.button("Filtrar CDs"):
        cds_filtrados = filtrar_cd_rango_fecha_indicada(fecha_busqueda)
        st.subheader("CDs filtrados por fecha:")
        st.dataframe(cds_filtrados.style.format({'Fecha Compra': '{:%d-%m-%Y}', 'Vencimiento': '{:%d-%m-%Y}'}))

    if st.button("Calcular Total Cartera a Fecha Seleccionada"):
        total_cartera = total_cartera_cd_a_fecha_seleccionada(fecha_busqueda)
        st.subheader("Total de la Cartera de CDs a la Fecha Seleccionada:")
        st.write(total_cartera)
else:
    st.write("Por favor, suba un archivo Excel para comenzar.")

