import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np

st.set_page_config(page_title="Análisis de Pallets", layout="wide")

def initialize_session_state():
    if 'selected_format' not in st.session_state:
        st.session_state.selected_format = "Todos"

# Método para agregar totales
def agregar_totales(df, columna_texto='Formato'):
    # Crear una copia para no modificar el original
    df_totales = df.copy()
    
    # Identificar columnas numéricas
    columnas_numericas = df.select_dtypes(include=[np.number]).columns.tolist()
    
    # Calcular totales solo para columnas numéricas
    totales = df[columnas_numericas].sum()
    
    # Crear un diccionario para la fila de totales
    fila_totales = totales.to_dict()
    
    # Agregar 'Total' a la columna de texto
    fila_totales[columna_texto] = 'Total'
    
    # Convertir a DataFrame
    df_con_totales = pd.concat([df, pd.DataFrame([fila_totales])], ignore_index=True)
    
    return df_con_totales

# Función para cargar y procesar Cargas.csv
def process_cargas(file):
    df = pd.read_csv(file, encoding='utf-8')
    df['total_pallets'] = df['lateral'].astype(float) + df['trasera'].astype(float)
    df['fecha'] = pd.to_datetime(df['fecha'])
    df['lateral'] = df['lateral'].astype(float)
    df['trasera'] = df['trasera'].astype(float)

    vivo_sprim_formats = ['01 - Vivo Caja',
                          '01 -Vivo Caja',
                          '01- Vivo Caja',
                          '01-Vivo Caja',
                          '02 - Vivo Almacén',
                          '02 -Vivo Almacén',
                          '02- Vivo Almacén',
                          '02-Vivo Almacén',
                          '03 - Sprim Caja',
                          '03 -Sprim Caja',
                          '03- Sprim Caja',
                          '03-Sprim Caja',
                          '04 - Sprim Almacén',
                          '04 -Sprim Almacén',
                          '04- Sprim Almacén',
                          '04-Sprim Almacén']

    df['formato'] = df['formato'].replace(vivo_sprim_formats, 'Jugo en Polvo')

    st.write("Formatos únicos (cargas):", df['formato'].unique())

    return df

def process_lineas(file):
    df = pd.read_csv(file, encoding='utf-8')
    df['total_pallets'] = df['pallets'].astype(float)
    df['fecha_de_documento'] = pd.to_datetime(df['fecha_de_documento'])
    
    # Asegurarnos que 'formato' es de tipo string
    df['formato'] = df['formato'].astype(str)
    
    # Reemplazar formatos
    vivo_sprim_formats = ['01 - Vivo Caja',
                          '01 -Vivo Caja',
                          '01- Vivo Caja',
                          '01-Vivo Caja',
                          '02 - Vivo Almacén',
                          '02 -Vivo Almacén',
                          '02- Vivo Almacén',
                          '02-Vivo Almacén',
                          '03 - Sprim Caja',
                          '03 -Sprim Caja',
                          '03- Sprim Caja',
                          '03-Sprim Caja',
                          '04 - Sprim Almacén',
                          '04 -Sprim Almacén',
                          '04- Sprim Almacén',
                          '04-Sprim Almacén']

    df['formato'] = df['formato'].replace(vivo_sprim_formats, 'Jugo en Polvo')

    # Mostrar formatos únicos después del reemplazo
    st.write("Formatos únicos (líneas):", df['formato'].unique())
    
    return df

def process_recepciones(file):
    df = pd.read_csv(file, delimiter=';', encoding='utf-8')
    
    df['Cant Pallet'] = df['Cant Pallet'].apply(lambda x: 
        0 if x == '¿' else 
        str(x).replace(',', '.'))
    
    df['Cant Pallet'] = pd.to_numeric(df['Cant Pallet'], errors='coerce').fillna(0)
    df['total_pallets'] = df['Cant Pallet']
    df['Fecha de documento'] = pd.to_datetime(df['Fecha de documento'], format='%d-%m-%Y')

    if 'Formato' in df.columns:
        # Asegurarnos que 'Formato' es de tipo string
        df['Formato'] = df['Formato'].astype(str)
        
        # Reemplazar formatos
        vivo_sprim_formats = ['01 - Vivo Caja',
                          '01 -Vivo Caja',
                          '01- Vivo Caja',
                          '01-Vivo Caja',
                          '02 - Vivo Almacén',
                          '02 -Vivo Almacén',
                          '02- Vivo Almacén',
                          '02-Vivo Almacén',
                          '03 - Sprim Caja',
                          '03 -Sprim Caja',
                          '03- Sprim Caja',
                          '03-Sprim Caja',
                          '04 - Sprim Almacén',
                          '04 -Sprim Almacén',
                          '04- Sprim Almacén',
                          '04-Sprim Almacén']

        df['Formato'] = df['Formato'].replace(vivo_sprim_formats, 'Jugo en Polvo')

        # Mostrar formatos únicos después del reemplazo
        st.write("Formatos únicos (recepciones):", df['Formato'].unique())
    
    return df

def get_product_details(df, formato, source_type='cargas'):
    """
    Get detailed product analysis for a specific format
    source_type can be: 'cargas', 'lineas', or 'recepciones'
    """
    # Define column mappings for each source
    column_mappings = {
        'cargas': {
            'format_col': 'formato',
            'product_col': 'texto_breve_material',
            'total_col': 'total_pallets'
        },
        'lineas': {
            'format_col': 'formato',
            'product_col': 'texto_breve_material',
            'total_col': 'total_pallets'
        },
        'recepciones': {
            'format_col': 'Formato',
            'product_col': 'Texto breve material',
            'total_col': 'total_pallets'
        }
    }
    
    # Get the correct column names for this source
    cols = column_mappings[source_type]

    df = df.copy()
    vivo_sprim_formats = ['01 - Vivo Caja',
                          '01 -Vivo Caja',
                          '01- Vivo Caja',
                          '01-Vivo Caja',
                          '02 - Vivo Almacén',
                          '02 -Vivo Almacén',
                          '02- Vivo Almacén',
                          '02-Vivo Almacén',
                          '03 - Sprim Caja',
                          '03 -Sprim Caja',
                          '03- Sprim Caja',
                          '03-Sprim Caja',
                          '04 - Sprim Almacén',
                          '04 -Sprim Almacén',
                          '04- Sprim Almacén',
                          '04-Sprim Almacén']
    df.loc[df[cols['format_col']].isin(vivo_sprim_formats), cols['format_col']] = 'Jugo en Polvo'
    
    
    if source_type == 'cargas':
        product_analysis = df[df[cols['format_col']] == formato].groupby(cols['product_col']).agg({
            cols['total_col']: 'sum',
            'lateral': 'sum',
            'trasera': 'sum'
        }).reset_index()
        
        total_pallets = product_analysis[cols['total_col']].sum()
        
        product_analysis['porcentaje_total'] = (product_analysis[cols['total_col']] / total_pallets * 100).round(2)
        product_analysis['porcentaje_lateral'] = (product_analysis['lateral'] / product_analysis[cols['total_col']] * 100).round(2)
        product_analysis['porcentaje_trasera'] = (product_analysis['trasera'] / product_analysis[cols['total_col']] * 100).round(2)
    else:
        product_analysis = df[df[cols['format_col']] == formato].groupby(cols['product_col']).agg({
            cols['total_col']: 'sum'
        }).reset_index()
        
        total_pallets = product_analysis[cols['total_col']].sum()
        product_analysis['porcentaje_total'] = (product_analysis[cols['total_col']] / total_pallets * 100).round(2)
    
    return product_analysis.sort_values(cols['total_col'], ascending=False)

def show_format_details(formato, df_cargas, df_lineas, df_recepciones):
    """
    Display detailed analysis for a specific format
    """
    st.header(f"Análisis Detallado - Formato: {formato}")
    
    # Create tabs for each data source
    tab_cargas, tab_lineas, tab_recepciones = st.tabs(["Cargas", "Líneas", "Recepciones"])
    
    with tab_cargas:
        if df_cargas is not None:
            products_cargas = get_product_details(df_cargas, formato, source_type='cargas')
            st.subheader("Detalle de Productos - Cargas")
            
            # Display metrics
            total_pallets = products_cargas['total_pallets'].sum()
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Pallets", f"{total_pallets:,.2f}")
            
            with col2:
                avg_lateral = (products_cargas['lateral'].sum() / total_pallets * 100).round(2)
                st.metric("Promedio Lateral", f"{avg_lateral:.2f}%")
            
            with col3:
                avg_trasera = (products_cargas['trasera'].sum() / total_pallets * 100).round(2)
                st.metric("Promedio Trasera", f"{avg_trasera:.2f}%")
            
            # Display product table
            st.dataframe(
                products_cargas.style.format({
                    'total_pallets': '{:,.2f}',
                    'lateral': '{:,.2f}',
                    'trasera': '{:,.2f}',
                    'porcentaje_total': '{:.2f}%',
                    'porcentaje_lateral': '{:.2f}%',
                    'porcentaje_trasera': '{:.2f}%'
                })
            )
            
            # Create visualization
            fig = go.Figure(data=[
                go.Bar(name='Lateral', 
                      x=products_cargas['texto_breve_material'], 
                      y=products_cargas['porcentaje_lateral'],
                      text=products_cargas['porcentaje_lateral'].apply(lambda x: f'{x:.1f}%')),
                go.Bar(name='Trasera', 
                      x=products_cargas['texto_breve_material'], 
                      y=products_cargas['porcentaje_trasera'],
                      text=products_cargas['porcentaje_trasera'].apply(lambda x: f'{x:.1f}%'))
            ])
            fig.update_layout(
                barmode='group',
                title=f'Distribución Lateral vs Trasera por Producto - {formato}',
                xaxis_title='Formato',
                yaxis_title='Porcentaje'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with tab_lineas:
        if df_lineas is not None:
            products_lineas = get_product_details(df_lineas, formato, source_type='lineas')
            st.subheader("Detalle de Productos - Líneas")
            
            # Display metrics
            st.metric("Total Pallets", f"{products_lineas['total_pallets'].sum():,.2f}")
            
            # Display product table
            st.dataframe(
                products_lineas.style.format({
                    'total_pallets': '{:,.2f}',
                    'porcentaje_total': '{:.2f}%'
                })
            )
            
            # Create visualization using the correct column name
            fig = px.bar(products_lineas, 
                        x='texto_breve_material',  # This should match the column name from the mapping
                        y='total_pallets',
                        title=f'Distribución de Pallets por Producto - {formato}')
            st.plotly_chart(fig, use_container_width=True)
    
    with tab_recepciones:
        if df_recepciones is not None:
            products_recepciones = get_product_details(df_recepciones, formato, source_type='recepciones')
            st.subheader("Detalle de Productos - Recepciones")
            
            # Display metrics
            st.metric("Total Pallets", f"{products_recepciones['total_pallets'].sum():,.2f}")
            
            # Display product table
            st.dataframe(
                products_recepciones.style.format({
                    'total_pallets': '{:,.2f}',
                    'porcentaje_total': '{:.2f}%'
                })
            )
            
            # Create visualization using the correct column name
            fig = px.bar(products_recepciones, 
                        x='Texto breve material',  # Using the correct column name from mapping
                        y='total_pallets',
                        title=f'Distribución de Pallets por Producto - {formato}')
            st.plotly_chart(fig, use_container_width=True)

def get_product_summary(df, formato, source_type='cargas'):
    """
    Get advanced analytics for products within a specific format
    """
    if source_type == 'cargas':
        df_filtered = df[df['formato'] == formato]
        
        # Análisis por producto
        summary = df_filtered.groupby('texto_breve_material').agg({
            'total_pallets': 'sum',
            'lateral': 'sum',
            'trasera': 'sum',
            'fecha': 'count'  # Cambiado a fecha para contar movimientos
        }).reset_index()
        
        # Calcular métricas avanzadas
        total_pallets = summary['total_pallets'].sum()
        summary['participacion_total'] = (summary['total_pallets'] / total_pallets * 100).round(2)
        summary['promedio_pallets_por_movimiento'] = (summary['total_pallets'] / summary['fecha']).round(2)
        summary['eficiencia_carga'] = ((summary['lateral'] + summary['trasera']) / summary['fecha']).round(2)
        
        # Tendencia de carga (comparar con mes anterior)
        df_filtered['mes'] = df_filtered['fecha'].dt.to_period('M')
        tendencia = df_filtered.groupby(['texto_breve_material', 'mes'])['total_pallets'].sum().reset_index()
        tendencia['mes_anterior'] = tendencia.groupby('texto_breve_material')['total_pallets'].shift(1)
        tendencia['variacion'] = ((tendencia['total_pallets'] - tendencia['mes_anterior']) / tendencia['mes_anterior'] * 100).fillna(0)
        
        # Obtener la última variación para cada producto
        ultima_tendencia = tendencia.groupby('texto_breve_material')['variacion'].last()
        summary['tendencia_mensual'] = summary['texto_breve_material'].map(ultima_tendencia)
        
        # Renombrar columnas
        summary = summary.rename(columns={
            'texto_breve_material': 'Formato',
            'total_pallets': 'Total Pallets',
            'participacion_total': '% Participación',
            'promedio_pallets_por_movimiento': 'Pallets/Movimiento',
            'eficiencia_carga': 'Eficiencia Carga',
            'tendencia_mensual': 'Tendencia (%)',
            'fecha': 'Num Movimientos'  # Renombrar el contador de movimientos
        })
        
    elif source_type == 'lineas':
        df_filtered = df[df['formato'] == formato]
        
        # Análisis por producto para líneas
        summary = df_filtered.groupby('texto_breve_material').agg({
            'total_pallets': ['sum', 'count', 'mean'],
            'fecha_de_documento': 'nunique'
        }).reset_index()
        
        # Aplanar las columnas multiíndice
        summary.columns = ['Formato', 'Total Pallets', 'Num Movimientos', 'Promedio Pallets', 'Num_Dias']
        
        # Calcular métricas adicionales, manejando NaT
        max_date = df_filtered['fecha_de_documento'].max()
        min_date = df_filtered['fecha_de_documento'].min()
        
        if pd.isna(max_date) or pd.isna(min_date):
            total_days = 1
        else:
            date_range = (max_date - min_date).days
            total_days = max(1, date_range + 1)
            
        # Convertir a float antes de hacer las operaciones
        summary['Num_Dias'] = summary['Num_Dias'].astype(float)
        summary['Frecuencia Movimiento'] = (summary['Num_Dias'] / float(total_days) * 100).round(2)
        summary['Pallets por Día Activo'] = (summary['Total Pallets'] / summary['Num_Dias']).round(2)

    else:  # recepciones
        df_filtered = df[df['Formato'] == formato]
        
        # Análisis por producto para recepciones
        summary = df_filtered.groupby('Texto breve material').agg({
            'total_pallets': ['sum', 'count', 'mean'],
            'Fecha de documento': 'nunique'
        }).reset_index()
        
        # Aplanar las columnas multiíndice
        summary.columns = ['Formato', 'Total Pallets', 'Num Recepciones', 'Promedio Pallets', 'Num_Dias']
        
        # Calcular métricas adicionales, manejando NaT
        max_date = df_filtered['Fecha de documento'].max()
        min_date = df_filtered['Fecha de documento'].min()
        
        if pd.isna(max_date) or pd.isna(min_date):
            total_days = 1
        else:
            date_range = (max_date - min_date).days
            total_days = max(1, date_range + 1)
            
        # Convertir a float antes de hacer las operaciones
        summary['Num_Dias'] = summary['Num_Dias'].astype(float)
        summary['Frecuencia Recepción'] = (summary['Num_Dias'] / float(total_days) * 100).round(2)
        summary['Pallets por Recepción'] = (summary['Total Pallets'] / summary['Num Recepciones']).round(2)
    
    return summary

def show_format_summary(formato, df_cargas, df_lineas, df_recepciones):
    """
    Display enhanced format summary for all three data sources
    """
    if formato:
        st.header(f"Análisis Detallado - Formato: {formato}")
        
        tab_cargas, tab_lineas, tab_recepciones = st.tabs(["Cargas", "Líneas", "Recepciones"])
        
        with tab_cargas:
            if df_cargas is not None:
                st.subheader("Análisis de Cargas por Producto")
                summary_cargas = get_product_summary(df_cargas, formato, 'cargas')
                
                # Métricas principales
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Pallets", f"{summary_cargas['Total Pallets'].sum():,.0f}")
                with col2:
                    st.metric("Eficiencia Promedio", 
                             f"{summary_cargas['Eficiencia Carga'].mean():.2f}")
                with col3:
                    st.metric("Productos Activos", f"{len(summary_cargas)}")
                
                # Tabla detallada
                st.dataframe(
                    summary_cargas.style.format({
                        'Total Pallets': '{:,.0f}',
                        '% Participación': '{:.2f}%',
                        'Pallets/Movimiento': '{:.2f}',
                        'Eficiencia Carga': '{:.2f}',
                        'Tendencia (%)': '{:+.2f}%'
                    }).background_gradient(subset=['% Participación'], cmap='YlOrRd')
                )
                
                # Visualización de tendencias
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=summary_cargas['Formato'],
                    y=summary_cargas['Total Pallets'],
                    name='Total Pallets'
                ))
                fig.add_trace(go.Scatter(
                    x=summary_cargas['Formato'],
                    y=summary_cargas['Eficiencia Carga'],
                    name='Eficiencia',
                    yaxis='y2'
                ))
                fig.update_layout(
                    title='Volumen vs Eficiencia por Producto',
                    yaxis2=dict(
                        title='Eficiencia',
                        overlaying='y',
                        side='right'
                    )
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with tab_lineas:
            if df_lineas is not None:
                st.subheader("Análisis de Líneas por Producto")
                summary_lineas = get_product_summary(df_lineas, formato, 'lineas')
                
                # Métricas principales
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Pallets", f"{summary_lineas['Total Pallets'].sum():,.0f}")
                with col2:
                    st.metric("Promedio Diario", 
                             f"{summary_lineas['Pallets por Día Activo'].mean():.2f}")
                with col3:
                    st.metric("Frecuencia Promedio", 
                             f"{summary_lineas['Frecuencia Movimiento'].mean():.2f}%")
                
                st.dataframe(
                    summary_lineas.style.format({
                        'Total Pallets': '{:,.0f}',
                        'Promedio Pallets': '{:.2f}',
                        'Frecuencia Movimiento': '{:.2f}%',
                        'Pallets por Día Activo': '{:.2f}'
                    }).background_gradient(subset=['Frecuencia Movimiento'], cmap='YlOrRd')
                )
        
        with tab_recepciones:
            if df_recepciones is not None:
                st.subheader("Análisis de Recepciones por Producto")
                summary_recepciones = get_product_summary(df_recepciones, formato, 'recepciones')
                
                # Métricas principales
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Pallets", f"{summary_recepciones['Total Pallets'].sum():,.0f}")
                with col2:
                    st.metric("Promedio por Recepción", 
                             f"{summary_recepciones['Pallets por Recepción'].mean():.2f}")
                with col3:
                    st.metric("Frecuencia Promedio", 
                             f"{summary_recepciones['Frecuencia Recepción'].mean():.2f}%")
                
                st.dataframe(
                    summary_recepciones.style.format({
                        'Total Pallets': '{:,.0f}',
                        'Promedio Pallets': '{:.2f}',
                        'Frecuencia Recepción': '{:.2f}%',
                        'Pallets por Recepción': '{:.2f}'
                    }).background_gradient(subset=['Frecuencia Recepción'], cmap='YlOrRd')
                )

def get_time_period_max(df, source_type='cargas'):
    """
    Analiza los máximos valores por diferentes períodos de tiempo
    """
    if source_type == 'cargas':
        # Crear diferentes agrupaciones temporales
        df['fecha'] = pd.to_datetime(df['fecha'])
        df['dia'] = df['fecha'].dt.date
        df['semana'] = df['fecha'].dt.isocalendar().week
        df['mes'] = df['fecha'].dt.to_period('M')
        df['trimestre'] = df['fecha'].dt.to_period('Q')
        df['semestre'] = df['fecha'].dt.to_period('H')
        df['año'] = df['fecha'].dt.year
        
        # Calcular máximos por período
        max_values = {
            'Diario': {
                'lateral': df.groupby('dia')['lateral'].sum().max(),
                'trasera': df.groupby('dia')['trasera'].sum().max(),
                'total': df.groupby('dia')['total_pallets'].sum().max(),
                'fecha_max_lateral': df.groupby('dia')['lateral'].sum().idxmax(),
                'fecha_max_trasera': df.groupby('dia')['trasera'].sum().idxmax(),
                'fecha_max_total': df.groupby('dia')['total_pallets'].sum().idxmax()
            },
            'Semanal': {
                'lateral': df.groupby(['año', 'semana'])['lateral'].sum().max(),
                'trasera': df.groupby(['año', 'semana'])['trasera'].sum().max(),
                'total': df.groupby(['año', 'semana'])['total_pallets'].sum().max(),
                'fecha_max_lateral': df.groupby(['año', 'semana'])['lateral'].sum().idxmax(),
                'fecha_max_trasera': df.groupby(['año', 'semana'])['trasera'].sum().idxmax(),
                'fecha_max_total': df.groupby(['año', 'semana'])['total_pallets'].sum().idxmax()
            },
            'Mensual': {
                'lateral': df.groupby('mes')['lateral'].sum().max(),
                'trasera': df.groupby('mes')['trasera'].sum().max(),
                'total': df.groupby('mes')['total_pallets'].sum().max(),
                'fecha_max_lateral': df.groupby('mes')['lateral'].sum().idxmax(),
                'fecha_max_trasera': df.groupby('mes')['trasera'].sum().idxmax(),
                'fecha_max_total': df.groupby('mes')['total_pallets'].sum().idxmax()
            },
            'Trimestral': {
                'lateral': df.groupby('trimestre')['lateral'].sum().max(),
                'trasera': df.groupby('trimestre')['trasera'].sum().max(),
                'total': df.groupby('trimestre')['total_pallets'].sum().max(),
                'fecha_max_lateral': df.groupby('trimestre')['lateral'].sum().idxmax(),
                'fecha_max_trasera': df.groupby('trimestre')['trasera'].sum().idxmax(),
                'fecha_max_total': df.groupby('trimestre')['total_pallets'].sum().idxmax()
            },
            'Semestral': {
                'lateral': df.groupby('semestre')['lateral'].sum().max(),
                'trasera': df.groupby('semestre')['trasera'].sum().max(),
                'total': df.groupby('semestre')['total_pallets'].sum().max(),
                'fecha_max_lateral': df.groupby('semestre')['lateral'].sum().idxmax(),
                'fecha_max_trasera': df.groupby('semestre')['trasera'].sum().idxmax(),
                'fecha_max_total': df.groupby('semestre')['total_pallets'].sum().idxmax()
            },
            'Anual': {
                'lateral': df.groupby('año')['lateral'].sum().max(),
                'trasera': df.groupby('año')['trasera'].sum().max(),
                'total': df.groupby('año')['total_pallets'].sum().max(),
                'fecha_max_lateral': df.groupby('año')['lateral'].sum().idxmax(),
                'fecha_max_trasera': df.groupby('año')['trasera'].sum().idxmax(),
                'fecha_max_total': df.groupby('año')['total_pallets'].sum().idxmax()
            }
        }
        
    elif source_type == 'lineas':
        # Para líneas (producción)
        df['fecha_de_documento'] = pd.to_datetime(df['fecha_de_documento'])
        df['dia'] = df['fecha_de_documento'].dt.date
        df['semana'] = df['fecha_de_documento'].dt.isocalendar().week
        df['mes'] = df['fecha_de_documento'].dt.to_period('M')
        df['trimestre'] = df['fecha_de_documento'].dt.to_period('Q')
        df['semestre'] = df['fecha_de_documento'].dt.to_period('H')
        df['año'] = df['fecha_de_documento'].dt.year
        
        max_values = {
            'Diario': {
                'total': df.groupby('dia')['total_pallets'].sum().max(),
                'fecha_max_total': df.groupby('dia')['total_pallets'].sum().idxmax()
            },
            'Semanal': {
                'total': df.groupby(['año', 'semana'])['total_pallets'].sum().max(),
                'fecha_max_total': df.groupby(['año', 'semana'])['total_pallets'].sum().idxmax()
            },
            'Mensual': {
                'total': df.groupby('mes')['total_pallets'].sum().max(),
                'fecha_max_total': df.groupby('mes')['total_pallets'].sum().idxmax()
            },
            'Trimestral': {
                'total': df.groupby('trimestre')['total_pallets'].sum().max(),
                'fecha_max_total': df.groupby('trimestre')['total_pallets'].sum().idxmax()
            },
            'Semestral': {
                'total': df.groupby('semestre')['total_pallets'].sum().max(),
                'fecha_max_total': df.groupby('semestre')['total_pallets'].sum().idxmax()
            },
            'Anual': {
                'total': df.groupby('año')['total_pallets'].sum().max(),
                'fecha_max_total': df.groupby('año')['total_pallets'].sum().idxmax()
            }
        }
    
    elif source_type == 'recepciones':
        # Para recepciones
        df['Fecha de documento'] = pd.to_datetime(df['Fecha de documento'])
        df['dia'] = df['Fecha de documento'].dt.date
        df['semana'] = df['Fecha de documento'].dt.isocalendar().week
        df['mes'] = df['Fecha de documento'].dt.to_period('M')
        df['trimestre'] = df['Fecha de documento'].dt.to_period('Q')
        df['semestre'] = df['Fecha de documento'].dt.to_period('H')
        df['año'] = df['Fecha de documento'].dt.year
        
        max_values = {
            'Diario': {
                'total': df.groupby('dia')['total_pallets'].sum().max(),
                'fecha_max_total': df.groupby('dia')['total_pallets'].sum().idxmax(),
                'num_recepciones': df.groupby('dia').size().max(),
                'fecha_max_recepciones': df.groupby('dia').size().idxmax()
            },
            'Semanal': {
                'total': df.groupby(['año', 'semana'])['total_pallets'].sum().max(),
                'fecha_max_total': df.groupby(['año', 'semana'])['total_pallets'].sum().idxmax(),
                'num_recepciones': df.groupby(['año', 'semana']).size().max(),
                'fecha_max_recepciones': df.groupby(['año', 'semana']).size().idxmax()
            },
            'Mensual': {
                'total': df.groupby('mes')['total_pallets'].sum().max(),
                'fecha_max_total': df.groupby('mes')['total_pallets'].sum().idxmax(),
                'num_recepciones': df.groupby('mes').size().max(),
                'fecha_max_recepciones': df.groupby('mes').size().idxmax()
            },
            'Trimestral': {
                'total': df.groupby('trimestre')['total_pallets'].sum().max(),
                'fecha_max_total': df.groupby('trimestre')['total_pallets'].sum().idxmax(),
                'num_recepciones': df.groupby('trimestre').size().max(),
                'fecha_max_recepciones': df.groupby('trimestre').size().idxmax()
            },
            'Semestral': {
                'total': df.groupby('semestre')['total_pallets'].sum().max(),
                'fecha_max_total': df.groupby('semestre')['total_pallets'].sum().idxmax(),
                'num_recepciones': df.groupby('semestre').size().max(),
                'fecha_max_recepciones': df.groupby('semestre').size().idxmax()
            },
            'Anual': {
                'total': df.groupby('año')['total_pallets'].sum().max(),
                'fecha_max_total': df.groupby('año')['total_pallets'].sum().idxmax(),
                'num_recepciones': df.groupby('año').size().max(),
                'fecha_max_recepciones': df.groupby('año').size().idxmax()
            }
        }
    
    return max_values

# Función para mostrar el análisis en la interfaz
def show_time_period_analysis(df_cargas, df_lineas, df_recepciones):
    st.header("Análisis de Máximos por Período")
    
    tab1, tab2, tab3 = st.tabs(["Cargas", "Producción", "Recepciones"])
    
    with tab1:
        if df_cargas is not None:
            max_cargas = get_time_period_max(df_cargas, 'cargas')
            
            st.subheader("Máximos Despachos")
            for periodo, valores in max_cargas.items():
                st.write(f"### {periodo}")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(
                        "Máx. Lateral",
                        f"{valores['lateral']:,.2f}",
                        help=f"Fecha: {valores['fecha_max_lateral']}"
                    )
                
                with col2:
                    st.metric(
                        "Máx. Trasera",
                        f"{valores['trasera']:,.2f}",
                        help=f"Fecha: {valores['fecha_max_trasera']}"
                    )
                
                with col3:
                    st.metric(
                        "Máx. Total",
                        f"{valores['total']:,.2f}",
                        help=f"Fecha: {valores['fecha_max_total']}"
                    )
    
    with tab2:
        if df_lineas is not None:
            max_lineas = get_time_period_max(df_lineas, 'lineas')
            
            st.subheader("Máximos Producción")
            for periodo, valores in max_lineas.items():
                st.write(f"### {periodo}")
                st.metric(
                    "Máx. Total Producido",
                    f"{valores['total']:,.2f}",
                    help=f"Fecha: {valores['fecha_max_total']}"
                )
    
    with tab3:
        if df_recepciones is not None:
            max_recepciones = get_time_period_max(df_recepciones, 'recepciones')
            
            st.subheader("Máximos Recepciones")
            for periodo, valores in max_recepciones.items():
                st.write(f"### {periodo}")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric(
                        "Máx. Pallets Recibidos",
                        f"{valores['total']:,.2f}",
                        help=f"Fecha: {valores['fecha_max_total']}"
                    )
                
                with col2:
                    st.metric(
                        "Máx. Número de Recepciones",
                        f"{valores['num_recepciones']:,.0f}",
                        help=f"Fecha: {valores['fecha_max_recepciones']}"
                    )

def add_period_column(df, fecha_col, periodo):
    """
    Agrega columna de período según el filtro seleccionado
    """
    df = df.copy()
    fecha = pd.to_datetime(df[fecha_col])
    
    if periodo == "Diario":
        df['periodo'] = fecha.dt.date
    elif periodo == "Semanal":
        df['periodo'] = fecha.dt.strftime('%Y-W%W')
    elif periodo == "Mensual":
        df['periodo'] = fecha.dt.strftime('%Y-%m')
    elif periodo == "Trimestral":
        df['periodo'] = fecha.dt.to_period('Q').astype(str)
    elif periodo == "Semestral":
        df['periodo'] = fecha.dt.to_period('H').astype(str)
    else:  # Anual
        df['periodo'] = fecha.dt.year
    
    return df

def get_product_summary_by_period(df, formato, periodo, source_type='cargas'):
    """
    Obtiene el análisis por producto agrupado por período
    """
    if source_type == 'cargas':
        df = add_period_column(df, 'fecha', periodo)
        df_filtered = df[df['formato'] == formato]
        
        # Análisis por producto y período
        summary = df_filtered.groupby(['texto_breve_material', 'periodo']).agg({
            'total_pallets': 'sum',
            'lateral': 'sum',
            'trasera': 'sum'
        }).reset_index()
        
        # Encontrar los máximos por producto
        max_values = summary.groupby('texto_breve_material').agg({
            'total_pallets': ['sum', 'max', 'mean'],
            'lateral': ['sum', 'max'],
            'trasera': ['sum', 'max'],
            'periodo': lambda x: x[summary.groupby('texto_breve_material')['total_pallets'].transform('max') == summary['total_pallets']].iloc[0]
        }).reset_index()
        
        # Aplanar columnas multinivel
        max_values.columns = ['Formato', 'Total', 'Max_Periodo', 'Promedio', 'Lateral_Total', 'Lateral_Max', 
                            'Trasera_Total', 'Trasera_Max', 'Periodo_Max']
        
        # Calcular porcentajes
        total_pallets = max_values['Total'].sum()
        max_values['Participacion'] = (max_values['Total'] / total_pallets * 100).round(2)
        max_values['Pct_Lateral'] = (max_values['Lateral_Total'] / max_values['Total'] * 100).round(2)
        max_values['Pct_Trasera'] = (max_values['Trasera_Total'] / max_values['Total'] * 100).round(2)
        
    elif source_type == 'lineas':
        df = add_period_column(df, 'fecha_de_documento', periodo)
        df_filtered = df[df['formato'] == formato]
        
        summary = df_filtered.groupby(['texto_breve_material', 'periodo']).agg({
            'total_pallets': 'sum'
        }).reset_index()
        
        max_values = summary.groupby('texto_breve_material').agg({
            'total_pallets': ['sum', 'max'],
            'periodo': lambda x: x[summary.groupby('texto_breve_material')['total_pallets'].transform('max') == summary['total_pallets']].iloc[0]
        }).reset_index()
        
        max_values.columns = ['Formato', 'Total', 'Max_Periodo', 'Periodo_Max']
        max_values['Participacion'] = (max_values['Total'] / max_values['Total'].sum() * 100).round(2)
        
    else:  # recepciones
        df = add_period_column(df, 'Fecha de documento', periodo)
        df_filtered = df[df['Formato'] == formato]
        
        summary = df_filtered.groupby(['Texto breve material', 'periodo']).agg({
            'total_pallets': 'sum'
        }).reset_index()
        
        max_values = summary.groupby('Texto breve material').agg({
            'total_pallets': ['sum', 'max'],
            'periodo': lambda x: x[summary.groupby('Texto breve material')['total_pallets'].transform('max') == summary['total_pallets']].iloc[0]
        }).reset_index()
        
        max_values.columns = ['Formato', 'Total', 'Max_Periodo', 'Periodo_Max']
        max_values['Participacion'] = (max_values['Total'] / max_values['Total'].sum() * 100).round(2)
    
    return max_values.sort_values('Total', ascending=False)

def get_weekly_analysis(df, formato, num_semanas=52):  # 52 semanas para un año
    """
    Calcula el análisis semanal de pallets por formato y material con un número fijo de semanas
    """
    fecha_column = next((col for col in df.columns if col in ['fecha', 'fecha_de_documento', 'Fecha de documento']), None)
    if not fecha_column:
        st.error("No se encontró la columna de fecha en el DataFrame")
        return None

    # Agregamos columna de semana usando la columna de fecha correcta
    df['fecha'] = pd.to_datetime(df[fecha_column])
    df['semana'] = df['fecha'].dt.isocalendar().week
    df['año'] = df['fecha'].dt.isocalendar().year
    
    # Crear un DataFrame con todas las semanas posibles
    # Crear un DataFrame con todas las semanas de 2024
    todas_semanas = pd.DataFrame(
        [(2024, week) for week in range(1, num_semanas + 1)],
        columns=['año', 'semana']
    )
    # Resto del código para identificar columnas...
    formato_column = next((col for col in df.columns if col in ['formato', 'Formato']), None)
    material_column = next((col for col in df.columns if col in ['texto_breve_material', 'Texto breve material', 'texto_breve_material']), None)
    cantidad_column = next((col for col in df.columns if col in ['total_pallets', 'pallets', 'Cant Pallet']), None)
    
    if formato and formato_column:
        df = df[df[formato_column] == formato]
    
    # Agrupamos por año, semana, formato y material
    weekly_avg = df.groupby(['año', 'semana', formato_column, material_column])[cantidad_column].sum().reset_index()
    
    # Crear una cuadrícula completa con todas las combinaciones
    grid = pd.merge(
        todas_semanas,
        weekly_avg[[formato_column, material_column]].drop_duplicates(),
        how='cross'
    )
    
    # Hacer merge con los datos reales
    weekly_complete = pd.merge(
        grid,
        weekly_avg,
        on=['año', 'semana', formato_column, material_column],
        how='left'
    )
    
    # Rellenar los valores faltantes con 0
    weekly_complete[cantidad_column] = weekly_complete[cantidad_column].fillna(0)
    
    # Calcular promedio diario
    weekly_complete['promedio_diario'] = weekly_complete[cantidad_column] / 7
    
    # Calculamos estadísticas
    stats = weekly_complete.groupby([formato_column, material_column]).agg({
        cantidad_column: ['mean', 'std', 'min', 'max', 'count'],
        'promedio_diario': ['mean', 'std', 'min', 'max']
    }).round(2)
    
    # Limpiamos los nombres de las columnas
    stats.columns = ['promedio_semanal', 'desviacion_std', 'min_semanal', 'max_semanal', 'num_semanas',
                    'promedio_diario', 'desviacion_std_diaria', 'min_diario', 'max_diario']
    stats = stats.reset_index()
    
    return stats

def analisis_semanal_detallado(df, formato):
    """
    Genera un análisis detallado de pallets por semana para un formato específico
    """
    # Identificar la columna de fecha correcta
    fecha_column = next((col for col in df.columns if col in ['fecha', 'fecha_de_documento', 'Fecha de documento']), None)
    
    if not fecha_column:
        st.error("No se encontró la columna de fecha en el DataFrame")
        return None

    # Convertir fecha a datetime
    df['fecha'] = pd.to_datetime(df[fecha_column])
    
    # Agregar columnas de año y semana
    df['año'] = df['fecha'].dt.isocalendar().year
    df['semana'] = df['fecha'].dt.isocalendar().week
    
    # Filtrar por formato si se proporciona
    if formato:
        formato_column = next((col for col in df.columns if col in ['formato', 'Formato']), None)
        if formato_column:
            df = df[df[formato_column] == formato]
    
    # Obtener la columna de pallets
    pallets_column = next((col for col in df.columns if col in ['total_pallets', 'pallets', 'Cant Pallet']), None)
    
    # Agrupar por año y semana
    pallets_por_semana = df.groupby(['año', 'semana'])[pallets_column].sum().reset_index()
    
    # Calcular promedio global
    promedio_global = pallets_por_semana[pallets_column].mean()
    
    # Agregar columna de comparación con el promedio
    pallets_por_semana['desviacion_promedio'] = pallets_por_semana[pallets_column] - promedio_global
    pallets_por_semana['porcentaje_desviacion'] = (pallets_por_semana['desviacion_promedio'] / promedio_global * 100).round(2)
    
    # Categorizar desviación
    def categorizar_desviacion(desviacion_porcentual):
        if desviacion_porcentual > 50:
            return 'Muy por encima (+50%)'
        elif desviacion_porcentual > 20:
            return 'Por encima (+20%)'
        elif desviacion_porcentual > 0:
            return 'Ligeramente por encima (+)'
        elif desviacion_porcentual == 0:
            return 'Igual al promedio'
        elif desviacion_porcentual > -20:
            return 'Ligeramente por debajo (-)'
        elif desviacion_porcentual > -50:
            return 'Por debajo (-20%)'
        else:
            return 'Muy por debajo (-50%)'
    
    pallets_por_semana['categoria_desviacion'] = pallets_por_semana['porcentaje_desviacion'].apply(categorizar_desviacion)
    
    # Renombrar columnas
    pallets_por_semana.columns = [
        'Año', 
        'Semana', 
        'Pallets', 
        'Desviación del Promedio', 
        'Porcentaje Desviación',
        'Categoría Desviación'
    ]
    
    return pallets_por_semana

def show_product_analysis_by_period(formato, df_cargas, df_lineas, df_recepciones, periodo):
    """
    Muestra el análisis por producto según el período seleccionado
    """
    if formato:
        st.header(f"Análisis de {formato} por {periodo}")
            
        # Análisis semanal para cada tipo de movimiento
        if df_cargas is not None:
            st.subheader("Cargas - Promedio Semanal")
            weekly_cargas = get_weekly_analysis(df_cargas, formato)
            
            if weekly_cargas is not None:
                # Métricas resumen de cargas semanales
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Promedio Semanal Global", f"{weekly_cargas['promedio_semanal'].mean():,.0f}")
                with col2:
                    st.metric("Máx. Semanal", f"{weekly_cargas['max_semanal'].max():,.0f}")
                with col3:
                    st.metric("Mín. Semanal", f"{weekly_cargas['min_semanal'].min():,.0f}")
                
                weekly_cargas_con_total = agregar_totales(weekly_cargas)

                
                # Tabla detallada de cargas semanales
                st.dataframe(
                    weekly_cargas_con_total.style.format({
                        'promedio_semanal': '{:,.0f}',
                        'desviacion_std': '{:,.2f}',
                        'min_semanal': '{:,.0f}',
                        'max_semanal': '{:,.0f}',
                        'num_semanas': '{:,.0f}',
                        'lateral': '{:,.0f}',
                        'trasera': '{:,.0f}',
                        'pct_lateral': '{:.1f}%',
                        'pct_trasera': '{:.1f}%'
                    })
                )
                
        
        if df_lineas is not None:
            st.subheader("Líneas - Promedio Semanal")
            weekly_lineas = get_weekly_analysis(df_lineas, formato)
            if weekly_lineas is not None:
                weekly_lineas_con_total = agregar_totales(weekly_lineas)
                st.dataframe(
                    weekly_lineas_con_total.style.format({
                        'promedio_semanal': '{:,.0f}',
                        'desviacion_std': '{:,.2f}',
                        'min_semanal': '{:,.0f}',
                        'max_semanal': '{:,.0f}',
                        'num_semanas': '{:,.0f}'
                    })
                )
        
        if df_recepciones is not None:
            st.subheader("Recepciones - Promedio Semanal")
            weekly_recepciones = get_weekly_analysis(df_recepciones, formato)
            if weekly_recepciones is not None:
                weekly_recepciones_con_total = agregar_totales(weekly_recepciones)
                st.dataframe(
                    weekly_recepciones_con_total.style.format({
                        'promedio_semanal': '{:,.0f}',
                        'desviacion_std': '{:,.2f}',
                        'min_semanal': '{:,.0f}',
                        'max_semanal': '{:,.0f}',
                        'num_semanas': '{:,.0f}'
                    })
                )

    st.subheader("Análisis Semanal Detallado")
    
    if df_cargas is not None:
        st.subheader("Cargas - Análisis Semanal")
        semanal_cargas = analisis_semanal_detallado(df_cargas, formato)
        
        if semanal_cargas is not None:
            # Métricas generales
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Promedio Semanal", f"{semanal_cargas['Pallets'].mean():,.0f}")
            with col2:
                st.metric("Máximo Semanal", f"{semanal_cargas['Pallets'].max():,.0f}")
            with col3:
                st.metric("Mínimo Semanal", f"{semanal_cargas['Pallets'].min():,.0f}")
            
            # Tabla de análisis semanal
            st.dataframe(
                semanal_cargas.style.format({
                    'Pallets': '{:,.0f}',
                    'Desviación del Promedio': '{:,.0f}',
                    'Porcentaje Desviación': '{:.2f}%'
                }).background_gradient(
                    subset=['Porcentaje Desviación'], 
                    cmap='RdYlGn_r'  # Gradiente de rojo a verde invertido
                )
            )
            
            # Gráfico de desviación semanal
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=semanal_cargas['Semana'],
                y=semanal_cargas['Pallets'],
                name='Pallets',
                text=semanal_cargas['Pallets'].apply(lambda x: f'{x:,.0f}'),
                textposition='auto'
            ))
            fig.add_trace(go.Scatter(
                x=semanal_cargas['Semana'],
                y=semanal_cargas['Porcentaje Desviación'],
                name='% Desviación',
                yaxis='y2'
            ))
            
            fig.update_layout(
                title='Pallets y Desviación por Semana',
                yaxis=dict(title='Pallets'),
                yaxis2=dict(
                    title='% Desviación',
                    overlaying='y',
                    side='right'
                )
            )
            
            st.plotly_chart(fig, use_container_width=True)

            # Identificar la columna de fecha correcta
            fecha_column = next((col for col in df_cargas.columns if col in ['fecha', 'fecha_de_documento', 'Fecha de documento']), None)

            # Convertir fecha a datetime
            df_cargas['fecha'] = pd.to_datetime(df_cargas[fecha_column])

            # Agregar columnas de año y semana
            df_cargas['año'] = df_cargas['fecha'].dt.isocalendar().year
            df_cargas['semana'] = df_cargas['fecha'].dt.isocalendar().week

            # Filtrar por formato si se proporciona
            if formato:
                formato_column = next((col for col in df_cargas.columns if col in ['formato', 'Formato']), None)
                if formato_column:
                    df_cargas = df_cargas[df_cargas[formato_column] == formato]

            # Obtener la columna de pallets
            pallets_column = next((col for col in df_cargas.columns if col in ['total_pallets', 'pallets', 'Cant Pallet']), None)

            # Agrupar por año y semana
            pallets_por_semana = df_cargas.groupby(['año', 'semana'])[pallets_column].sum().reset_index()

            # Calcular promedio global
            promedio_global = pallets_por_semana[pallets_column].mean()

            # Crear etiqueta de semana combinando año y número de semana
            pallets_por_semana['semana_label'] = pallets_por_semana['año'].astype(str) + '-W' + pallets_por_semana['semana'].astype(str)

            # Crear figura con Plotly
            fig = go.Figure()

            # Agregar barras de pallets por semana
            fig.add_trace(go.Bar(
                x=pallets_por_semana['semana_label'], 
                y=pallets_por_semana[pallets_column],
                name='Pallets por Semana',
                text=pallets_por_semana[pallets_column].apply(lambda x: f'{x:,.0f}'),
                textposition='outside'
            ))

            # Agregar línea de promedio
            fig.add_trace(go.Scatter(
                x=pallets_por_semana['semana_label'],
                y=[promedio_global] * len(pallets_por_semana),
                mode='lines',
                name='Promedio',
                line=dict(color='red', width=2, dash='dash')
            ))

            # Configurar diseño del gráfico
            fig.update_layout(
                title=f'Pallets por Semana - {formato}',
                xaxis_title='Semana',
                yaxis_title='Pallets',
                hovermode='closest'
            )

            # Mostrar gráfico
            st.plotly_chart(fig, use_container_width=True)

def get_abc_classification(df, source_type='cargas'):
    """
    Realiza análisis ABC basado en frecuencia de movimientos
    """
    if source_type == 'cargas':
        # Contar movimientos por producto
        movements = df.groupby('formato').agg({
            'fecha': 'count',
            'total_pallets': 'sum',
            'lateral': 'sum',
            'trasera': 'sum'
        }).reset_index()
        
        movements.columns = ['Formato', 'Frecuencia', 'Total_Pallets', 'Lateral', 'Trasera']
        
    elif source_type == 'lineas':
        movements = df.groupby('formato').agg({
            'fecha_de_documento': 'count',
            'total_pallets': 'sum'
        }).reset_index()
        
        movements.columns = ['Formato', 'Frecuencia', 'Total_Pallets']
        
    else:  # recepciones
        movements = df.groupby('Formato').agg({
            'Fecha de documento': 'count',
            'total_pallets': 'sum'
        }).reset_index()
        
        movements.columns = ['Formato', 'Frecuencia', 'Total_Pallets']
    
    # Calcular porcentajes y acumulados
    total_pallets = movements['Total_Pallets'].sum()
    movements['Porcentaje'] = (movements['Total_Pallets'] / total_pallets * 100).round(2)
    movements = movements.sort_values('Total_Pallets', ascending=False)
    movements['Porcentaje_Acumulado'] = movements['Porcentaje'].cumsum()
    
    # Asignar clasificación ABC
    movements['Clasificacion'] = movements['Porcentaje_Acumulado'].apply(
        lambda x: 'A' if x <= 80 else ('B' if x <= 95 else 'C')
    )
    
    return movements

def show_abc_analysis(df_cargas, df_lineas, df_recepciones):
    """
    Muestra el análisis ABC en la interfaz
    """
    st.header("Análisis ABC por Frecuencia de Movimientos")
    
    tab_cargas, tab_lineas, tab_recepciones = st.tabs(["Cargas", "Líneas", "Recepciones"])
    
    with tab_cargas:
        if df_cargas is not None:
            st.subheader("Análisis ABC de Cargas")
            abc_cargas = get_abc_classification(df_cargas, 'cargas')
            
            # Resumen por clasificación
            summary = abc_cargas.groupby('Clasificacion').agg({
                'Formato': 'count',
                'Frecuencia': 'sum',
                'Total_Pallets': 'sum'
            }).reset_index()
            
            summary['Porcentaje_Productos'] = (summary['Formato'] / summary['Formato'].sum() * 100).round(2)
            summary['Porcentaje_Movimientos'] = (summary['Frecuencia'] / summary['Frecuencia'].sum() * 100).round(2)
            
            # Mostrar métricas por clasificación
            st.write("### Resumen por Clasificación")
            col1, col2, col3 = st.columns(3)
            
            for idx, row in summary.iterrows():
                with st.container():
                    st.write(f"#### Clasificación {row['Clasificacion']}")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Formatos", f"{row['Formato']:.0f} ({row['Porcentaje_Productos']:.1f}%)")
                    with col2:
                        st.metric("Movimientos", f"{row['Frecuencia']:.0f} ({row['Porcentaje_Movimientos']:.1f}%)")
                    with col3:
                        st.metric("Total Pallets", f"{row['Total_Pallets']:,.0f}")
            
            # Gráfico de Pareto
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=abc_cargas['Formato'],
                y=abc_cargas['Porcentaje'],
                name='Porcentaje'
            ))
            fig.add_trace(go.Scatter(
                x=abc_cargas['Formato'],
                y=abc_cargas['Porcentaje_Acumulado'],
                name='% Acumulado',
                yaxis='y2'
            ))
            
            fig.update_layout(
                title='Diagrama de Pareto - Total de Pallets',
                yaxis=dict(title='Porcentaje'),
                yaxis2=dict(
                    title='Porcentaje Acumulado',
                    overlaying='y',
                    side='right',
                    range=[0, 100]
                ),
                showlegend=True
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Tabla detallada
            st.write("### Detalle por Producto")
            st.dataframe(
                abc_cargas.style.format({
                    'Frecuencia': '{:,.0f}',
                    'Total_Pallets': '{:,.0f}',
                    'Lateral': '{:,.0f}',
                    'Trasera': '{:,.0f}',
                    'Porcentaje': '{:.2f}%',
                    'Porcentaje_Acumulado': '{:.2f}%'
                }).background_gradient(
                    subset=['Porcentaje'],
                    cmap='YlOrRd'
                )
            )
    
    with tab_lineas:
        if df_lineas is not None:
            st.subheader("Análisis ABC de Líneas")
            abc_lineas = get_abc_classification(df_lineas, 'lineas')
            
            # Similar análisis para líneas...
            summary = abc_lineas.groupby('Clasificacion').agg({
                'Formato': 'count',
                'Frecuencia': 'sum',
                'Total_Pallets': 'sum'
            }).reset_index()
            
            summary['Porcentaje_Productos'] = (summary['Formato'] / summary['Formato'].sum() * 100).round(2)
            summary['Porcentaje_Movimientos'] = (summary['Frecuencia'] / summary['Frecuencia'].sum() * 100).round(2)
            
            # Mostrar métricas...
            st.write("### Resumen por Clasificación")
            for idx, row in summary.iterrows():
                with st.container():
                    st.write(f"#### Clasificación {row['Clasificacion']}")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Formato", f"{row['Formato']:.0f} ({row['Porcentaje_Productos']:.1f}%)")
                    with col2:
                        st.metric("Movimientos", f"{row['Frecuencia']:.0f} ({row['Porcentaje_Movimientos']:.1f}%)")
                    with col3:
                        st.metric("Total Pallets", f"{row['Total_Pallets']:,.0f}")
            
            # Tabla detallada
            st.write("### Detalle por Producto")
            st.dataframe(
                abc_lineas.style.format({
                    'Frecuencia': '{:,.0f}',
                    'Total_Pallets': '{:,.0f}',
                    'Porcentaje': '{:.2f}%',
                    'Porcentaje_Acumulado': '{:.2f}%'
                }).background_gradient(
                    subset=['Porcentaje'],
                    cmap='YlOrRd'
                )
            )
    
    with tab_recepciones:
        if df_recepciones is not None:
            st.subheader("Análisis ABC de Recepciones")
            abc_recepciones = get_abc_classification(df_recepciones, 'recepciones')
            
            # Similar análisis para recepciones...
            summary = abc_recepciones.groupby('Clasificacion').agg({
                'Formato': 'count',
                'Frecuencia': 'sum',
                'Total_Pallets': 'sum'
            }).reset_index()
            
            summary['Porcentaje_Productos'] = (summary['Formato'] / summary['Formato'].sum() * 100).round(2)
            summary['Porcentaje_Movimientos'] = (summary['Frecuencia'] / summary['Frecuencia'].sum() * 100).round(2)
            
            # Mostrar métricas...
            st.write("### Resumen por Clasificación")
            for idx, row in summary.iterrows():
                with st.container():
                    st.write(f"#### Clasificación {row['Clasificacion']}")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Formato", f"{row['Formato']:.0f} ({row['Porcentaje_Productos']:.1f}%)")
                    with col2:
                        st.metric("Movimientos", f"{row['Frecuencia']:.0f} ({row['Porcentaje_Movimientos']:.1f}%)")
                    with col3:
                        st.metric("Total Pallets", f"{row['Total_Pallets']:,.0f}")
            
            # Tabla detallada
            st.write("### Detalle por Producto")
            st.dataframe(
                abc_recepciones.style.format({
                    'Frecuencia': '{:,.0f}',
                    'Total_Pallets': '{:,.0f}',
                    'Porcentaje': '{:.2f}%',
                    'Porcentaje_Acumulado': '{:.2f}%'
                }).background_gradient(
                    subset=['Porcentaje'],
                    cmap='YlOrRd'
                )
            )

def analyze_product_location_strategy(df_cargas, df_lineas, df_recepciones):
    """
    Análisis integral para estrategia de ubicación de productos
    
    Parámetros:
    - df_cargas: DataFrame de Cargas
    - df_lineas: DataFrame de Líneas
    - df_recepciones: DataFrame de Recepciones
    
    Retorna: DataFrame con estrategia de ubicación
    """
    # 1. Análisis ABC de Frecuencia (ya implementado en get_abc_classification)
    abc_cargas = get_abc_classification(df_cargas, 'cargas')
    abc_lineas = get_abc_classification(df_lineas, 'lineas')
    abc_recepciones = get_abc_classification(df_recepciones, 'recepciones')
    
    # 2. Análisis de Volumen Total
    def calcular_volumen(df, source_type='cargas'):
        if source_type == 'cargas':
            volumenes = df.groupby('texto_breve_material')['total_pallets'].sum()
        elif source_type == 'lineas':
            volumenes = df.groupby('texto_breve_material')['total_pallets'].sum()
        else:  # recepciones
            volumenes = df.groupby('Texto breve material')['total_pallets'].sum()
        
        # Categorizar volumen usando percentiles
        volumenes_cat = pd.qcut(volumenes, q=3, labels=['Bajo', 'Medio', 'Alto'])
        return volumenes_cat
    
    volumen_cargas = calcular_volumen(df_cargas, 'cargas')
    volumen_lineas = calcular_volumen(df_lineas, 'lineas')
    volumen_recepciones = calcular_volumen(df_recepciones, 'recepciones')
    
    # 3. Análisis de Distribución de Cargas (solo para Cargas)
    def analizar_distribucion_cargas(df):
        df_grupo = df.groupby('texto_breve_material').agg({
            'lateral': 'sum',
            'trasera': 'sum',
            'total_pallets': 'sum'
        })
        
        df_grupo['pct_lateral'] = df_grupo['lateral'] / df_grupo['total_pallets'] * 100
        df_grupo['pct_trasera'] = df_grupo['trasera'] / df_grupo['total_pallets'] * 100
        
        # Categorizar distribución
        def categorizar_distribucion(row):
            if row['pct_lateral'] > 70:
                return 'Predominio Lateral'
            elif row['pct_trasera'] > 70:
                return 'Predominio Trasera'
            else:
                return 'Balanceado'
        
        df_grupo['distribucion_cargas'] = df_grupo.apply(categorizar_distribucion, axis=1)
        
        return df_grupo['distribucion_cargas']
    
    distribucion_cargas = analizar_distribucion_cargas(df_cargas)
    
    # Consolidar estrategia
    estrategia = pd.DataFrame({
        'Frecuencia_Cargas': abc_cargas.set_index('Formato')['Clasificacion'],
        'Frecuencia_Lineas': abc_lineas.set_index('Formato')['Clasificacion'],
        'Frecuencia_Recepciones': abc_recepciones.set_index('Formato')['Clasificacion'],
        'Volumen_Cargas': volumen_cargas,
        'Volumen_Lineas': volumen_lineas,
        'Volumen_Recepciones': volumen_recepciones,
        'Distribucion_Cargas': distribucion_cargas
    })
    
    # Definir estrategia de ubicación
    def definir_estrategia_ubicacion(row):
        # Priorizar productos Clase A, Alto Volumen
        if (row['Frecuencia_Cargas'] == 'A' and row['Volumen_Cargas'] == 'Alto'):
            return 'Zona Prime - Acceso Rápido'
        
        # Productos Clase B o Volumen Medio
        elif (row['Frecuencia_Cargas'] == 'B' or row['Volumen_Cargas'] == 'Medio'):
            return 'Zona Secundaria'
        
        # Productos Clase C o Bajo Volumen
        else:
            return 'Zona de Reserva'
    
    estrategia['Estrategia_Ubicacion'] = estrategia.apply(definir_estrategia_ubicacion, axis=1)
    
    # Considerar distribución de cargas para ajustar ubicación
    def ajustar_ubicacion_por_distribucion(row):
        if row['Distribucion_Cargas'] == 'Predominio Lateral':
            return f"{row['Estrategia_Ubicacion']} - Preferencia Lateral"
        elif row['Distribucion_Cargas'] == 'Predominio Trasera':
            return f"{row['Estrategia_Ubicacion']} - Preferencia Trasera"
        else:
            return row['Estrategia_Ubicacion']
    
    estrategia['Estrategia_Ubicacion_Final'] = estrategia.apply(ajustar_ubicacion_por_distribucion, axis=1)
    
    return estrategia

def visualizar_estrategia_ubicacion(estrategia):
    """
    Crear una visualización de la estrategia de ubicación
    """
    import plotly.express as px
    import plotly.graph_objects as go
    
    # Contar estrategias
    conteo_estrategias = estrategia['Estrategia_Ubicacion_Final'].value_counts()
    
    # Gráfico de distribución de estrategias
    fig1 = px.pie(
        values=conteo_estrategias.values, 
        names=conteo_estrategias.index, 
        title='Distribución de Estrategias de Ubicación'
    )
    
    # Gráfico de distribución por frecuencia
    fig2 = go.Figure()
    for estrategia_ubicacion in estrategia['Estrategia_Ubicacion_Final'].unique():
        subset = estrategia[estrategia['Estrategia_Ubicacion_Final'] == estrategia_ubicacion]
        
        fig2.add_trace(go.Bar(
            name=estrategia_ubicacion,
            x=['Cargas', 'Líneas', 'Recepciones'],
            y=[
                (subset['Frecuencia_Cargas'] == 'A').mean() * 100,
                (subset['Frecuencia_Lineas'] == 'A').mean() * 100,
                (subset['Frecuencia_Recepciones'] == 'A').mean() * 100
            ]
        ))
    
    fig2.update_layout(
        title='Porcentaje de Productos Clase A por Estrategia de Ubicación',
        yaxis_title='Porcentaje de Productos Clase A'
    )
    
    return fig1, fig2

def agrupar_productos_por_categoria(df_cargas, df_lineas, df_recepciones):
    """
    Agrupar productos con nombres específicos en categorías personalizadas
    """
    def encontrar_productos_por_nombre(df, columna_producto, palabras_clave):
        """
        Encontrar productos que contengan cualquiera de las palabras clave
        """
        return df[df[columna_producto].str.contains('|'.join(palabras_clave), case=False, na=False)]

    # Definir grupos de productos
    grupos_productos = {
        'Jugo en Polvo': ['01 - Vivo Caja', '02 - Vivo Almacén', '03 - Sprim Caja', '04 - Sprim Almacén']
    }

    # Función para marcar productos en grupos
    def marcar_grupo_producto(producto, grupos):
        for grupo, palabras_clave in grupos.items():
            if any(palabra.lower() in producto.lower() for palabra in palabras_clave):
                return grupo
        return producto

    # Aplicar marcación de grupos a cada DataFrame
    for df, col_producto in [
        (df_cargas, 'texto_breve_material'), 
        (df_lineas, 'texto_breve_material'), 
        (df_recepciones, 'Texto breve material')
    ]:
        df['Grupo_Producto'] = df[col_producto].apply(lambda x: marcar_grupo_producto(str(x), grupos_productos))

    return df_cargas, df_lineas, df_recepciones

# Esta función se puede llamar desde Streamlit para mostrar los resultados
def main_location_strategy(df_cargas, df_lineas, df_recepciones):
    """
    Función principal para ejecutar el análisis de estrategia de ubicación
    """
    estrategia = analyze_product_location_strategy(df_cargas, df_lineas, df_recepciones)
    
    # Opcionalmente, puedes guardar la estrategia en un archivo CSV
    estrategia.to_csv('estrategia_ubicacion_productos.csv')
    
    # Visualizar resultados
    fig1, fig2 = visualizar_estrategia_ubicacion(estrategia)
    
    return estrategia, fig1, fig2


def identificar_productos_duplicados(df_cargas, df_lineas, df_recepciones):
    """
    Identificar productos duplicados en diferentes fuentes de datos
    """
    # Función para obtener categorías por producto en una fuente
    def get_categorias_por_producto(df, columna_producto='Formato', columna_categoria='Clasificacion'):
        return df.set_index(columna_producto)[columna_categoria].to_dict()

    # Obtener diccionarios de categorías
    cats_cargas = get_categorias_por_producto(
        get_abc_classification(df_cargas, 'cargas'), 
        columna_producto='Formato', 
        columna_categoria='Clasificacion'
    )
    cats_lineas = get_categorias_por_producto(
        get_abc_classification(df_lineas, 'lineas'), 
        columna_producto='Formato', 
        columna_categoria='Clasificacion'
    )
    cats_recepciones = get_categorias_por_producto(
        get_abc_classification(df_recepciones, 'recepciones'), 
        columna_producto='Formato', 
        columna_categoria='Clasificacion'
    )

    # Combinar todos los productos
    todos_productos = set(list(cats_cargas.keys()) + 
                          list(cats_lineas.keys()) + 
                          list(cats_recepciones.keys()))

    # Identificar productos con categorías diferentes
    productos_duplicados = {}
    for producto in todos_productos:
        categorias = []
        if producto in cats_cargas:
            categorias.append(('Cargas', cats_cargas[producto]))
        if producto in cats_lineas:
            categorias.append(('Líneas', cats_lineas[producto]))
        if producto in cats_recepciones:
            categorias.append(('Recepciones', cats_recepciones[producto]))
        
        # Si tiene más de una categoría, es un duplicado
        if len(set(cat for _, cat in categorias)) > 1:
            productos_duplicados[producto] = categorias

    return productos_duplicados

def seleccionar_categorias_duplicados(productos_duplicados):
    """
    Crear una interfaz de Streamlit para seleccionar categorías de productos duplicados
    """
    st.header("Resolución de Productos Duplicados")
    categorias_seleccionadas = {}

    for producto, categorias in productos_duplicados.items():
        st.subheader(f"Producto: {producto}")
        
        # Mostrar las categorías encontradas
        for fuente, categoria in categorias:
            st.write(f"- {fuente}: {categoria}")
        
        # Selector de categoría
        categoria_elegida = st.selectbox(
            f"Selecciona categoría final para {producto}", 
            ['A', 'B', 'C'], 
            index=0,  # Por defecto selecciona 'A'
            key=f"cat_selector_{producto}"
        )
        
        categorias_seleccionadas[producto] = categoria_elegida

    return categorias_seleccionadas

def apply_custom_categorization(df, categorias_seleccionadas, source_type='cargas'):
    """
    Aplicar categorización personalizada a un DataFrame
    """
    # Clonar el DataFrame para no modificar el original
    df_modificado = df.copy()
    
    # Columnas según el tipo de fuente
    if source_type == 'cargas':
        producto_col = 'texto_breve_material'
    elif source_type == 'lineas':
        producto_col = 'texto_breve_material'
    else:  # recepciones
        producto_col = 'Texto breve material'
    
    # Aplicar categorías personalizadas
    for producto, categoria in categorias_seleccionadas.items():
        df_modificado.loc[df_modificado[producto_col] == producto, 'Clasificacion'] = categoria
    
    return df_modificado

def analyze_product_location_strategy(df_cargas, df_lineas, df_recepciones):
    """
    Análisis integral para estrategia de ubicación de productos con categorización personalizada
    """
    df_cargas, df_lineas, df_recepciones = agrupar_productos_por_categoria(df_cargas, df_lineas, df_recepciones)

    # Identificar productos duplicados
    productos_duplicados = identificar_productos_duplicados(df_cargas, df_lineas, df_recepciones)
    
    # Si hay productos duplicados, mostrar interfaz de selección
    categorias_seleccionadas = {}
    if productos_duplicados:
        categorias_seleccionadas = seleccionar_categorias_duplicados(productos_duplicados)
    
    # Aplicar categorizaciones personalizadas
    abc_cargas = get_abc_classification(df_cargas, 'cargas')
    abc_lineas = get_abc_classification(df_lineas, 'lineas')
    abc_recepciones = get_abc_classification(df_recepciones, 'recepciones')
    
    # Si hay categorías personalizadas, aplicarlas
    if categorias_seleccionadas:
        abc_cargas = apply_custom_categorization(abc_cargas, categorias_seleccionadas, 'cargas')
        abc_lineas = apply_custom_categorization(abc_lineas, categorias_seleccionadas, 'lineas')
        abc_recepciones = apply_custom_categorization(abc_recepciones, categorias_seleccionadas, 'recepciones')
    
    # 2. Análisis de Volumen Total
    def calcular_volumen(df, source_type='cargas'):
        if source_type == 'cargas':
            volumenes = df.groupby('texto_breve_material')['total_pallets'].sum()
        elif source_type == 'lineas':
            volumenes = df.groupby('texto_breve_material')['total_pallets'].sum()
        else:  # recepciones
            volumenes = df.groupby('Texto breve material')['total_pallets'].sum()
        
        # Eliminar duplicados del índice
        volumenes = volumenes[~volumenes.index.duplicated(keep='first')]
        
        # Categorizar volumen usando percentiles
        volumenes_cat = pd.qcut(volumenes, q=3, labels=['Bajo', 'Medio', 'Alto'])
        return volumenes_cat
    
    volumen_cargas = calcular_volumen(df_cargas, 'cargas')
    volumen_lineas = calcular_volumen(df_lineas, 'lineas')
    volumen_recepciones = calcular_volumen(df_recepciones, 'recepciones')
    
    # 3. Análisis de Distribución de Cargas (solo para Cargas)
    def analizar_distribucion_cargas(df):
        df_grupo = df.groupby('texto_breve_material').agg({
            'lateral': 'sum',
            'trasera': 'sum',
            'total_pallets': 'sum'
        })
        
        # Eliminar duplicados del índice
        df_grupo = df_grupo[~df_grupo.index.duplicated(keep='first')]
        
        df_grupo['pct_lateral'] = df_grupo['lateral'] / df_grupo['total_pallets'] * 100
        df_grupo['pct_trasera'] = df_grupo['trasera'] / df_grupo['total_pallets'] * 100
        
        # Categorizar distribución
        def categorizar_distribucion(row):
            if row['pct_lateral'] > 70:
                return 'Predominio Lateral'
            elif row['pct_trasera'] > 70:
                return 'Predominio Trasera'
            else:
                return 'Balanceado'
        
        df_grupo['distribucion_cargas'] = df_grupo.apply(categorizar_distribucion, axis=1)
        
        return df_grupo['distribucion_cargas']
    
    distribucion_cargas = analizar_distribucion_cargas(df_cargas)
    
    # Consolidar estrategia
    estrategia = pd.DataFrame({
        'Frecuencia_Cargas': abc_cargas.set_index('Formato')['Clasificacion'],
        'Frecuencia_Lineas': abc_lineas.set_index('Formato')['Clasificacion'],
        'Frecuencia_Recepciones': abc_recepciones.set_index('Formato')['Clasificacion'],
        'Volumen_Cargas': volumen_cargas,
        'Volumen_Lineas': volumen_lineas,
        'Volumen_Recepciones': volumen_recepciones,
        'Distribucion_Cargas': distribucion_cargas
    }).reset_index()
    
    # Renombrar la columna de índice
    estrategia.rename(columns={'index': 'Formato'}, inplace=True)
    
    # Definir estrategia de ubicación
    def definir_estrategia_ubicacion(row):
        # Priorizar productos Clase A, Alto Volumen
        if (row['Frecuencia_Cargas'] == 'A' and row['Volumen_Cargas'] == 'Alto'):
            return 'Zona Prime - Acceso Rápido'
        
        # Productos Clase B o Volumen Medio
        elif (row['Frecuencia_Cargas'] == 'B' or row['Volumen_Cargas'] == 'Medio'):
            return 'Zona Secundaria'
        
        # Productos Clase C o Bajo Volumen
        else:
            return 'Zona de Reserva'
    
    estrategia['Estrategia_Ubicacion'] = estrategia.apply(definir_estrategia_ubicacion, axis=1)
    
    # Considerar distribución de cargas para ajustar ubicación
    def ajustar_ubicacion_por_distribucion(row):
        if row['Distribucion_Cargas'] == 'Predominio Lateral':
            return f"{row['Estrategia_Ubicacion']} - Preferencia Lateral"
        elif row['Distribucion_Cargas'] == 'Predominio Trasera':
            return f"{row['Estrategia_Ubicacion']} - Preferencia Trasera"
        else:
            return row['Estrategia_Ubicacion']
    
    estrategia['Estrategia_Ubicacion_Final'] = estrategia.apply(ajustar_ubicacion_por_distribucion, axis=1)
    
    # Establecer el Producto como índice al final
    estrategia.set_index('Formato', inplace=True)
    
    return estrategia

def analyze_product_location_strategy(df_cargas, df_lineas, df_recepciones):
    """
    Análisis integral para estrategia de ubicación de productos
    
    Parámetros:
    - df_cargas: DataFrame de Cargas
    - df_lineas: DataFrame de Líneas
    - df_recepciones: DataFrame de Recepciones
    
    Retorna: DataFrame con estrategia de ubicación
    """
    # 1. Análisis ABC de Frecuencia (ya implementado en get_abc_classification)
    abc_cargas = get_abc_classification(df_cargas, 'cargas')
    abc_lineas = get_abc_classification(df_lineas, 'lineas')
    abc_recepciones = get_abc_classification(df_recepciones, 'recepciones')
    
    # Eliminar duplicados conservando el primer registro
    abc_cargas = abc_cargas.drop_duplicates(subset=['Formato'], keep='first')
    abc_lineas = abc_lineas.drop_duplicates(subset=['Formato'], keep='first')
    abc_recepciones = abc_recepciones.drop_duplicates(subset=['Formato'], keep='first')
    
    # 2. Análisis de Volumen Total
    def calcular_volumen(df, source_type='cargas'):
        if source_type == 'cargas':
            volumenes = df.groupby('texto_breve_material')['total_pallets'].sum()
        elif source_type == 'lineas':
            volumenes = df.groupby('texto_breve_material')['total_pallets'].sum()
        else:  # recepciones
            volumenes = df.groupby('Texto breve material')['total_pallets'].sum()
        
        # Eliminar duplicados del índice
        volumenes = volumenes[~volumenes.index.duplicated(keep='first')]
        
        # Categorizar volumen usando percentiles
        volumenes_cat = pd.qcut(volumenes, q=3, labels=['Bajo', 'Medio', 'Alto'])
        return volumenes_cat
    
    volumen_cargas = calcular_volumen(df_cargas, 'cargas')
    volumen_lineas = calcular_volumen(df_lineas, 'lineas')
    volumen_recepciones = calcular_volumen(df_recepciones, 'recepciones')
    
    # 3. Análisis de Distribución de Cargas (solo para Cargas)
    def analizar_distribucion_cargas(df):
        df_grupo = df.groupby('texto_breve_material').agg({
            'lateral': 'sum',
            'trasera': 'sum',
            'total_pallets': 'sum'
        })
        
        # Eliminar duplicados del índice
        df_grupo = df_grupo[~df_grupo.index.duplicated(keep='first')]
        
        df_grupo['pct_lateral'] = df_grupo['lateral'] / df_grupo['total_pallets'] * 100
        df_grupo['pct_trasera'] = df_grupo['trasera'] / df_grupo['total_pallets'] * 100
        
        # Categorizar distribución
        def categorizar_distribucion(row):
            if row['pct_lateral'] > 70:
                return 'Predominio Lateral'
            elif row['pct_trasera'] > 70:
                return 'Predominio Trasera'
            else:
                return 'Balanceado'
        
        df_grupo['distribucion_cargas'] = df_grupo.apply(categorizar_distribucion, axis=1)
        
        return df_grupo['distribucion_cargas']
    
    distribucion_cargas = analizar_distribucion_cargas(df_cargas)
    
    # Consolidar estrategia
    estrategia = pd.DataFrame({
        'Frecuencia_Cargas': abc_cargas.set_index('Formato')['Clasificacion'],
        'Frecuencia_Lineas': abc_lineas.set_index('Formato')['Clasificacion'],
        'Frecuencia_Recepciones': abc_recepciones.set_index('Formato')['Clasificacion'],
        'Volumen_Cargas': volumen_cargas,
        'Volumen_Lineas': volumen_lineas,
        'Volumen_Recepciones': volumen_recepciones,
        'Distribucion_Cargas': distribucion_cargas
    }).reset_index()
    
    # Renombrar la columna de índice
    estrategia.rename(columns={'index': 'Formato'}, inplace=True)
    
    # Definir estrategia de ubicación
    def definir_estrategia_ubicacion(row):
        # Priorizar productos Clase A, Alto Volumen
        if (row['Frecuencia_Cargas'] == 'A' and row['Volumen_Cargas'] == 'Alto'):
            return 'Zona Prime - Acceso Rápido'
        
        # Productos Clase B o Volumen Medio
        elif (row['Frecuencia_Cargas'] == 'B' or row['Volumen_Cargas'] == 'Medio'):
            return 'Zona Secundaria'
        
        # Productos Clase C o Bajo Volumen
        else:
            return 'Zona de Reserva'
    
    estrategia['Estrategia_Ubicacion'] = estrategia.apply(definir_estrategia_ubicacion, axis=1)
    
    # Considerar distribución de cargas para ajustar ubicación
    def ajustar_ubicacion_por_distribucion(row):
        if row['Distribucion_Cargas'] == 'Predominio Lateral':
            return f"{row['Estrategia_Ubicacion']} - Preferencia Lateral"
        elif row['Distribucion_Cargas'] == 'Predominio Trasera':
            return f"{row['Estrategia_Ubicacion']} - Preferencia Trasera"
        else:
            return row['Estrategia_Ubicacion']
    
    estrategia['Estrategia_Ubicacion_Final'] = estrategia.apply(ajustar_ubicacion_por_distribucion, axis=1)
    
    # Establecer el Producto como índice al final
    estrategia.set_index('Formato', inplace=True)
    
    return estrategia

def visualizar_estrategia_ubicacion(estrategia):
    """
    Crear una visualización de la estrategia de ubicación
    """
    import plotly.express as px
    import plotly.graph_objects as go
    
    # Contar estrategias
    conteo_estrategias = estrategia['Estrategia_Ubicacion_Final'].value_counts()
    
    # Gráfico de distribución de estrategias
    fig1 = px.pie(
        values=conteo_estrategias.values, 
        names=conteo_estrategias.index, 
        title='Distribución de Estrategias de Ubicación'
    )
    
    # Gráfico de distribución por frecuencia
    fig2 = go.Figure()
    for estrategia_ubicacion in estrategia['Estrategia_Ubicacion_Final'].unique():
        subset = estrategia[estrategia['Estrategia_Ubicacion_Final'] == estrategia_ubicacion]
        
        fig2.add_trace(go.Bar(
            name=estrategia_ubicacion,
            x=['Cargas', 'Líneas', 'Recepciones'],
            y=[
                (subset['Frecuencia_Cargas'] == 'A').mean() * 100,
                (subset['Frecuencia_Lineas'] == 'A').mean() * 100,
                (subset['Frecuencia_Recepciones'] == 'A').mean() * 100
            ]
        ))
    
    fig2.update_layout(
        title='Porcentaje de Productos Clase A por Estrategia de Ubicación',
        yaxis_title='Porcentaje de Productos Clase A'
    )
    
    return fig1, fig2

# Esta función se puede llamar desde Streamlit para mostrar los resultados
def main_location_strategy(df_cargas, df_lineas, df_recepciones):
    """
    Función principal para ejecutar el análisis de estrategia de ubicación
    """
    estrategia = analyze_product_location_strategy(df_cargas, df_lineas, df_recepciones)
    
    # Opcionalmente, puedes guardar la estrategia en un archivo CSV
    estrategia.to_csv('estrategia_ubicacion_productos.csv')
    
    # Visualizar resultados
    fig1, fig2 = visualizar_estrategia_ubicacion(estrategia)
    
    return estrategia, fig1, fig2

# Título de la aplicación
st.title("📦 Análisis de Movimiento de Pallets")

# Sidebar para cargar archivos
st.sidebar.header("Carga de Archivos")

cargas_file = st.sidebar.file_uploader("Cargar Cargas.csv", type=['csv'])
lineas_file = st.sidebar.file_uploader("Cargar Lineas.csv", type=['csv'])
recepciones_file = st.sidebar.file_uploader("Cargar Recepciones.csv", type=['csv'])

# Después de los file_uploaders en el sidebar
st.sidebar.markdown("---")
top_n = st.sidebar.slider(
    "Mostrar Top N Productos",
    min_value=1,
    max_value=50,
    value=10,
    help="Selecciona la cantidad de productos a mostrar en los gráficos y tablas"
)

# En la sección del sidebar, después del slider de top_n
st.sidebar.markdown("---")
periodo_analisis = st.sidebar.selectbox(
    "Período de Análisis",
    ["Diario", "Semanal", "Mensual", "Trimestral", "Semestral", "Anual"],
    help="Selecciona el período para agrupar los datos en el análisis"
)


# Contenedor principal
if cargas_file or lineas_file or recepciones_file:
    initialize_session_state()
    
    # Tabs para diferentes análisis
    tab1, tab2, tab3, tab4, tab0 = st.tabs(["Análisis General", "Análisis por Formato", "Análisis por Período", "Análisis ABC", "Data"])
    
    with tab1:
        # Crear tres columnas para mostrar los totales
        col1, col2, col3 = st.columns(3)
        
        # Variable para almacenar los datos de la gráfica
        plot_data = []
        
        # Procesar Cargas.csv
        if cargas_file:
            with col1:
                st.subheader("Cargas")
                df_cargas = process_cargas(cargas_file)
                total_cargas = df_cargas['total_pallets'].sum()
                st.metric("Total Pallets", f"{total_cargas:,.2f}")
                st.metric("Total Registros", len(df_cargas))
                
                plot_data.append({
                    'Fuente': 'Cargas',
                    'Total Pallets': total_cargas
                })
                
                st.subheader("Desglose por Mes")
                monthly_cargas = df_cargas.groupby(df_cargas['fecha'].dt.strftime('%Y-%m'))[['total_pallets']].sum()
                st.dataframe(monthly_cargas)

                st.write("Columnas disponibles:", df_cargas.columns.tolist())  # Para Cargas
        
        # Procesar Lineas.csv
        if lineas_file:
            with col2:
                st.subheader("Líneas")
                df_lineas = process_lineas(lineas_file)
                total_lineas = df_lineas['total_pallets'].sum()
                st.metric("Total Pallets", f"{total_lineas:,.2f}")
                st.metric("Total Registros", len(df_lineas))
                
                plot_data.append({
                    'Fuente': 'Líneas',
                    'Total Pallets': total_lineas
                })
                
                st.subheader("Desglose por Mes")
                monthly_lineas = df_lineas.groupby(df_lineas['fecha_de_documento'].dt.strftime('%Y-%m'))[['total_pallets']].sum()
                st.dataframe(monthly_lineas)

                st.write("Columnas disponibles:", df_lineas.columns.tolist())  # Para Líneas 
        
        # Procesar Recepciones.csv
        if recepciones_file:
            with col3:
                st.subheader("Recepciones")
                df_recepciones = process_recepciones(recepciones_file)
                total_recepciones = df_recepciones['total_pallets'].sum()
                st.metric("Total Pallets", f"{total_recepciones:,.2f}")
                st.metric("Total Registros", len(df_recepciones))
                
                plot_data.append({
                    'Fuente': 'Recepciones',
                    'Total Pallets': total_recepciones
                })
                
                st.subheader("Desglose por Mes")
                monthly_recepciones = df_recepciones.groupby(df_recepciones['Fecha de documento'].dt.strftime('%Y-%m'))[['total_pallets']].sum()
                st.dataframe(monthly_recepciones)

                st.write("Columnas disponibles:", df_recepciones.columns.tolist())  # Para Recepciones

        
        # Mostrar gráfica comparativa
        if plot_data:
            st.subheader("Comparativa de Pallets por Fuente")
            df_plot = pd.DataFrame(plot_data)
            fig = px.bar(df_plot, 
                        x='Fuente', 
                        y='Total Pallets',
                        title='Comparación de Pallets por Fuente',
                        color='Fuente')
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        resumen_tab, detalle_tab = st.tabs(["Resumen por Formato", "Detalle de Formato"])

        with resumen_tab:
            # Agregar selector de formato al inicio
            all_formats = set()
            if 'df_cargas' in locals():
                all_formats.update(df_cargas['formato'].unique())
            if 'df_lineas' in locals():
                all_formats.update(df_lineas['formato'].unique())
            if 'df_recepciones' in locals():
                all_formats.update(df_recepciones['Formato'].unique())

            formato_options = ["Todos"] + sorted(list(all_formats))
            
            # Selector de formato en la pestaña Resumen
            selected_format_resumen  = st.selectbox(
                "Filtrar por Formato",
                formato_options,
                index=formato_options.index(st.session_state.selected_format)
            )

            # Actualizar el estado cuando cambia la selección en Resumen
            if selected_format_resumen != st.session_state.selected_format:
                st.session_state.selected_format = selected_format_resumen
            
            if st.session_state.selected_format != "Todos":
                # Mostrar análisis detallado del formato seleccionado
                tab_cargas, tab_lineas, tab_recepciones = st.tabs(["Cargas", "Líneas", "Recepciones"])
                
                with tab_cargas:
                    if df_cargas is not None:
                        st.subheader("Análisis de Cargas por Producto")
                        summary_cargas = get_product_summary(df_cargas, selected_format_resumen, 'cargas')
                        
                        # Métricas principales
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Total Pallets", f"{summary_cargas['Total Pallets'].sum():,.0f}")
                        with col2:
                            st.metric("Eficiencia Promedio", 
                                     f"{summary_cargas['Eficiencia Carga'].mean():.2f}")
                        with col3:
                            st.metric("Productos Activos", f"{len(summary_cargas)}")
                        
                        # Tabla detallada
                        st.dataframe(
                            summary_cargas.style.format({
                                'Total Pallets': '{:,.0f}',
                                '% Participación': '{:.2f}%',
                                'Pallets/Movimiento': '{:.2f}',
                                'Eficiencia Carga': '{:.2f}',
                                'Tendencia (%)': '{:+.2f}%'
                            }).background_gradient(subset=['% Participación'], cmap='YlOrRd')
                        )
                        
                        # Gráfico de análisis
                        fig = go.Figure()
                        fig.add_trace(go.Bar(
                            x=summary_cargas['Formato'],
                            y=summary_cargas['Total Pallets'],
                            name='Total Pallets'
                        ))
                        fig.add_trace(go.Scatter(
                            x=summary_cargas['Formato'],
                            y=summary_cargas['Eficiencia Carga'],
                            name='Eficiencia',
                            yaxis='y2'
                        ))
                        fig.update_layout(
                            title='Volumen vs Eficiencia por Formato',
                            yaxis2=dict(
                                title='Eficiencia',
                                overlaying='y',
                                side='right'
                            )
                        )
                        st.plotly_chart(fig, use_container_width=True)
                
                with tab_lineas:
                    if df_lineas is not None:
                        st.subheader("Análisis de Líneas por Producto")
                        summary_lineas = get_product_summary(df_lineas, selected_format_resumen, 'lineas')
                        
                        # Métricas principales
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Total Pallets", f"{summary_lineas['Total Pallets'].sum():,.0f}")
                        with col2:
                            st.metric("Promedio Diario", 
                                     f"{summary_lineas['Pallets por Día Activo'].mean():.2f}")
                        with col3:
                            st.metric("Frecuencia Promedio", 
                                     f"{summary_lineas['Frecuencia Movimiento'].mean():.2f}%")
                        
                        st.dataframe(
                            summary_lineas.style.format({
                                'Total Pallets': '{:,.0f}',
                                'Promedio Pallets': '{:.2f}',
                                'Frecuencia Movimiento': '{:.2f}%',
                                'Pallets por Día Activo': '{:.2f}'
                            }).background_gradient(subset=['Frecuencia Movimiento'], cmap='YlOrRd')
                        )
                
                with tab_recepciones:
                    if df_recepciones is not None:
                        st.subheader("Análisis de Recepciones por Producto")
                        summary_recepciones = get_product_summary(df_recepciones, selected_format_resumen, 'recepciones')
                        
                        # Métricas principales
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Total Pallets", f"{summary_recepciones['Total Pallets'].sum():,.0f}")
                        with col2:
                            st.metric("Promedio por Recepción", 
                                     f"{summary_recepciones['Pallets por Recepción'].mean():.2f}")
                        with col3:
                            st.metric("Frecuencia Promedio", 
                                     f"{summary_recepciones['Frecuencia Recepción'].mean():.2f}%")
                        
                        st.dataframe(
                            summary_recepciones.style.format({
                                'Total Pallets': '{:,.0f}',
                                'Promedio Pallets': '{:.2f}',
                                'Frecuencia Recepción': '{:.2f}%',
                                'Pallets por Recepción': '{:.2f}'
                            }).background_gradient(subset=['Frecuencia Recepción'], cmap='YlOrRd')
                        )
            else:
                # Mostrar el análisis general por formato (tu código existente)
                st.header("Análisis por Formato")
                
                # Análisis por formato para cada archivo
                if cargas_file:
                    st.subheader("Cargas - Análisis por Formato")
                    format_cargas = df_cargas.groupby('formato').agg({
                        'total_pallets': 'sum',
                        'lateral': 'sum',
                        'trasera': 'sum',
                        'texto_breve_material': 'count'
                    }).reset_index()

                    total_pallets = format_cargas['total_pallets'].sum()

                    format_cargas['pct_lateral'] = (format_cargas['lateral'] / format_cargas['total_pallets'] * 100).round(2)
                    format_cargas['pct_trasera'] = (format_cargas['trasera'] / format_cargas['total_pallets'] * 100).round(2)
                    format_cargas['pct_total'] = (format_cargas['total_pallets'] / total_pallets * 100).round(2)
                    

                    format_cargas.columns = [
                        'Formato', 
                        'Total Pallets',
                        'Pallets Lateral', 
                        'Pallets Trasera',
                        'Cantidad de Registros',
                        'Porcentaje Lateral',
                        'Porcentaje Trasera',
                        'Porcentaje del Total'
                    ]

                    # Ordenar por Total Pallets de mayor a menor
                    format_cargas = format_cargas.sort_values('Total Pallets', ascending=False).head(top_n)
                    format_cargas = agregar_totales(format_cargas)

                    st.dataframe(
                        format_cargas.style.format({
                            'Total Pallets': '{:,.2f}',
                            'Pallets Lateral': '{:,.2f}',
                            'Pallets Trasera': '{:,.2f}',
                            'Cantidad de Registros': '{:,.0f}',
                            'Porcentaje Lateral': '{:.2f}%',
                            'Porcentaje Trasera': '{:.2f}%',
                            'Porcentaje del Total': '{:.2f}%'
                        }),
                        use_container_width=True
                    )

                    fig_lateral_trasera = go.Figure(data=[
                        go.Bar(name='Lateral', 
                            x=format_cargas['Formato'], 
                            y=format_cargas['Porcentaje Lateral'],
                            text=format_cargas['Porcentaje Lateral'].apply(lambda x: f'{x:.1f}%'),
                            textposition='auto'),
                        go.Bar(name='Trasera', 
                            x=format_cargas['Formato'], 
                            y=format_cargas['Porcentaje Trasera'],
                            text=format_cargas['Porcentaje Trasera'].apply(lambda x: f'{x:.1f}%'),
                            textposition='auto')
                    ])
                    
                    fig_lateral_trasera.update_layout(
                        barmode='stack',
                        title=f'Distribución Porcentual Lateral vs Trasera por Formato (Top {top_n})',
                        xaxis_title='Formato',
                        yaxis_title='Porcentaje',
                        yaxis=dict(tickformat='.0f')
                    )
                    
                    st.plotly_chart(fig_lateral_trasera, use_container_width=True)
                    
                if lineas_file:
                    st.subheader("Líneas - Análisis por Formato")
                    format_lineas = df_lineas.groupby('formato').agg({
                        'total_pallets': 'sum',
                        'texto_breve_material': 'count'
                    }).reset_index()
                    format_lineas.columns = ['Formato', 'Total Pallets', 'Cantidad de Registros']

                    format_lineas['Porcentaje del Total'] = (format_lineas['Total Pallets'] / format_lineas['Total Pallets'].sum() * 100).round(2)
                    
                    format_lineas = format_lineas.sort_values('Total Pallets', ascending=False).head(top_n)
                    format_lineas = agregar_totales(format_lineas)

                    st.dataframe(
                        format_lineas.style.format({
                            'Total Pallets': '{:,.2f}',
                            'Cantidad de Registros': '{:,.0f}',
                            'Porcentaje del Total': '{:,.2f}%'
                        }),
                        use_container_width=True
                    )

                    # Gráfico de barras para Líneas
                    fig_lineas = px.bar(format_lineas, 
                                    x='Formato', 
                                    y='Total Pallets',
                                    title=f'Distribución de Pallets por Formato - Líneas (Top {top_n})',
                                    color='Formato')
                    st.plotly_chart(fig_lineas, use_container_width=True)

                    
                if recepciones_file:
                    st.subheader("Recepciones - Análisis por Formato")
                    format_recepciones = df_recepciones.groupby('Formato').agg({
                        'total_pallets': 'sum',
                        'Texto breve material': 'count'
                    }).reset_index()
                    format_recepciones.columns = ['Formato', 'Total Pallets', 'Cantidad de Registros']

                    format_recepciones['Porcentaje del Total'] = (format_recepciones['Total Pallets'] / format_recepciones['Total Pallets'].sum() * 100).round(2)
                    
                    format_recepciones = format_recepciones.sort_values('Total Pallets', ascending=False).head(top_n)
                    format_recepciones = agregar_totales(format_recepciones)

                    st.dataframe(
                        format_recepciones.style.format({
                            'Total Pallets': '{:,.2f}',
                            'Cantidad de Registros': '{:,.0f}',
                            'Porcentaje del Total': '{:,.2f}%'
                        }),
                        use_container_width=True
                    )

                    # Gráfico de barras para Recepciones
                    fig_recepciones = px.bar(format_recepciones, 
                                        x='Formato', 
                                        y='Total Pallets',
                                        title=f'Distribución de Pallets por Formato - Recepciones (Top {top_n})',
                                        color='Formato')
                    st.plotly_chart(fig_recepciones, use_container_width=True)


                # Comparativa de formatos entre archivos
                if cargas_file and lineas_file and recepciones_file:
                    st.subheader("Comparativa de Formatos entre Archivos")
                    
                    # Preparar datos para la comparativa
                    # Obtener los valores de cada fuente
                    cargas_totales = format_cargas.groupby('Formato')['Total Pallets'].sum().reset_index()
                    cargas_totales.rename(columns={'Total Pallets': 'Cargas'}, inplace=True)

                    lineas_totales = format_lineas.groupby('Formato')['Total Pallets'].sum().reset_index()
                    lineas_totales.rename(columns={'Total Pallets': 'Líneas'}, inplace=True)

                    recepciones_totales = format_recepciones.groupby('Formato')['Total Pallets'].sum().reset_index()
                    recepciones_totales.rename(columns={'Total Pallets': 'Recepciones'}, inplace=True)

                    format_comparison = pd.DataFrame({'Formato': pd.concat([
                        cargas_totales['Formato'], lineas_totales['Formato'], recepciones_totales['Formato']
                    ]).drop_duplicates()})

                    # Unir los datos calculados
                    format_comparison = format_comparison.merge(cargas_totales, on='Formato', how='left')
                    format_comparison = format_comparison.merge(lineas_totales, on='Formato', how='left')
                    format_comparison = format_comparison.merge(recepciones_totales, on='Formato', how='left')

                    # Rellenar NaN con 0 para evitar valores faltantes
                    format_comparison.fillna(0, inplace=True)

                    # Agregar columna con el total de pallets sumando Cargas, Líneas y Recepciones
                    format_comparison['Total Pallets'] = format_comparison['Cargas'] + format_comparison['Líneas'] + format_comparison['Recepciones']
                    
                    # Gráfico de barras agrupadas
                    fig_comparison = go.Figure(data=[
                        go.Bar(name='Cargas', x=format_comparison['Formato'], y=format_comparison['Cargas']),
                        go.Bar(name='Líneas', x=format_comparison['Formato'], y=format_comparison['Líneas']),
                        go.Bar(name='Recepciones', x=format_comparison['Formato'], y=format_comparison['Recepciones'])
                    ])

                    fig_comparison.update_layout(
                        barmode='group',
                        title='Comparativa de Pallets por Formato entre Archivos',
                        xaxis_title='Formato',
                        yaxis_title='Total Pallets'
                    )

                    st.plotly_chart(fig_comparison, use_container_width=True)
                    st.dataframe(format_comparison)


        with detalle_tab:
            st.header("Detalle por Formato")
            
            # Selector de formato en la pestaña Detalle
            selected_format_detalle = st.selectbox(
                "Filtrar por Formato",
                formato_options,
                index=formato_options.index(st.session_state.selected_format),
                key="format_selector_detalle"  # Clave única para este selectbox
            )

            if selected_format_detalle != st.session_state.selected_format:
                st.session_state.selected_format = selected_format_detalle
            
            if st.session_state.selected_format != "Todos":
                show_format_details(
                    st.session_state.selected_format,
                    df_cargas if cargas_file else None,
                    df_lineas if lineas_file else None,
                    df_recepciones if recepciones_file else None
                )
                show_product_analysis_by_period(
                    st.session_state.selected_format,
                    df_cargas if cargas_file else None,
                    df_lineas if lineas_file else None,
                    df_recepciones if recepciones_file else None,
                    periodo_analisis
                )
            else:
                st.info("Selecciona un formato específico para ver sus detalles")
    with tab3:
        show_time_period_analysis(
            df_cargas if cargas_file else None,
            df_lineas if lineas_file else None,
            df_recepciones if recepciones_file else None
        )
    
    with tab4:
        show_abc_analysis(
            df_cargas if cargas_file else None,
            df_lineas if lineas_file else None,
            df_recepciones if recepciones_file else None
        )
    
    with tab0:
        st.header("Estrategia de Ubicación de Productos")

        estrategia, fig_distribucion, fig_clase_a = main_location_strategy(
            df_cargas, df_lineas, df_recepciones
        )

        # Gráfico de distribución de estrategias
        st.plotly_chart(fig_distribucion, use_container_width=True)
        
        # Gráfico de porcentaje de productos Clase A
        st.plotly_chart(fig_clase_a, use_container_width=True)
        
        # Tabla detallada de estrategias
        st.dataframe(estrategia)
else:
    st.info("👈 Por favor, carga los archivos CSV en el panel lateral para comenzar el análisis.")
    
# Agregar información adicional
st.sidebar.markdown("---")
st.sidebar.markdown("""
### Información
- Cargas: suma de lateral + trasera
- Líneas: columna pallets
- Recepciones: columna Cant Pallet
""")