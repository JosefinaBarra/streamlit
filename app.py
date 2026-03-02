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

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def agregar_totales(df, columna_texto='Formato'):
    """Agrega fila de totales numéricos al DataFrame."""
    df_totales = df.copy()
    columnas_numericas = df.select_dtypes(include=[np.number]).columns.tolist()
    totales = df[columnas_numericas].sum()
    fila_totales = totales.to_dict()
    fila_totales[columna_texto] = 'Total'
    df_con_totales = pd.concat([df, pd.DataFrame([fila_totales])], ignore_index=True)
    return df_con_totales

VIVO_SPRIM_FORMATS = [
    '01 - Vivo Caja',  '01 -Vivo Caja',  '01- Vivo Caja',  '01-Vivo Caja',
    '02 - Vivo Almacén','02 -Vivo Almacén','02- Vivo Almacén','02-Vivo Almacén',
    '03 - Sprim Caja',  '03 -Sprim Caja',  '03- Sprim Caja',  '03-Sprim Caja',
    '04 - Sprim Almacén','04 -Sprim Almacén','04- Sprim Almacén','04-Sprim Almacén',
]

# ─────────────────────────────────────────────
# DATA LOADING
# ─────────────────────────────────────────────

def process_cargas(file):
    df = pd.read_csv(file, encoding='utf-8')
    df['lateral'] = df['lateral'].astype(float)
    df['trasera'] = df['trasera'].astype(float)
    df['total_pallets'] = df['lateral'] + df['trasera']
    df['fecha'] = pd.to_datetime(df['fecha'])
    df['formato'] = df['formato'].replace(VIVO_SPRIM_FORMATS, 'Jugo en Polvo')
    with st.expander("Formatos únicos (cargas)", expanded=False):
        st.write(df['formato'].unique())
    return df

def process_lineas(file):
    df = pd.read_csv(file, encoding='utf-8')
    df['total_pallets'] = df['pallets'].astype(float)
    df['fecha_de_documento'] = pd.to_datetime(df['fecha_de_documento'])
    df['formato'] = df['formato'].astype(str).replace(VIVO_SPRIM_FORMATS, 'Jugo en Polvo')
    with st.expander("Formatos únicos (líneas)", expanded=False):
        st.write(df['formato'].unique())
    return df

def process_recepciones(file):
    df = pd.read_csv(file, delimiter=';', encoding='utf-8')
    df['Cant Pallet'] = df['Cant Pallet'].apply(
        lambda x: 0 if str(x).strip() == '¿' else str(x).replace(',', '.')
    )
    df['Cant Pallet'] = pd.to_numeric(df['Cant Pallet'], errors='coerce').fillna(0)
    df['total_pallets'] = df['Cant Pallet']
    df['Fecha de documento'] = pd.to_datetime(df['Fecha de documento'], format='%d-%m-%Y')
    if 'Formato' in df.columns:
        df['Formato'] = df['Formato'].astype(str).replace(VIVO_SPRIM_FORMATS, 'Jugo en Polvo')
        with st.expander("Formatos únicos (recepciones)", expanded=False):
            st.write(df['Formato'].unique())
    return df

# ─────────────────────────────────────────────
# PRODUCT DETAILS
# ─────────────────────────────────────────────

def get_product_details(df, formato, source_type='cargas'):
    column_mappings = {
        'cargas':      {'format_col': 'formato',   'product_col': 'texto_breve_material', 'total_col': 'total_pallets'},
        'lineas':      {'format_col': 'formato',   'product_col': 'texto_breve_material', 'total_col': 'total_pallets'},
        'recepciones': {'format_col': 'Formato',   'product_col': 'Texto breve material', 'total_col': 'total_pallets'},
    }
    cols = column_mappings[source_type]
    df = df.copy()
    df[cols['format_col']] = df[cols['format_col']].replace(VIVO_SPRIM_FORMATS, 'Jugo en Polvo')

    if source_type == 'cargas':
        product_analysis = df[df[cols['format_col']] == formato].groupby(cols['product_col']).agg(
            {cols['total_col']: 'sum', 'lateral': 'sum', 'trasera': 'sum'}
        ).reset_index()
        total = product_analysis[cols['total_col']].sum()
        product_analysis['porcentaje_total']   = (product_analysis[cols['total_col']] / total * 100).round(2)
        product_analysis['porcentaje_lateral'] = (product_analysis['lateral'] / product_analysis[cols['total_col']] * 100).round(2)
        product_analysis['porcentaje_trasera'] = (product_analysis['trasera'] / product_analysis[cols['total_col']] * 100).round(2)
    else:
        product_analysis = df[df[cols['format_col']] == formato].groupby(cols['product_col']).agg(
            {cols['total_col']: 'sum'}
        ).reset_index()
        total = product_analysis[cols['total_col']].sum()
        product_analysis['porcentaje_total'] = (product_analysis[cols['total_col']] / total * 100).round(2)

    return product_analysis.sort_values(cols['total_col'], ascending=False)

def show_format_details(formato, df_cargas, df_lineas, df_recepciones):
    st.header(f"Análisis Detallado - Formato: {formato}")
    tab_c, tab_l, tab_r = st.tabs(["Cargas", "Líneas", "Recepciones"])

    with tab_c:
        if df_cargas is not None:
            products = get_product_details(df_cargas, formato, 'cargas')
            st.subheader("Detalle de Productos - Cargas")
            total = products['total_pallets'].sum()
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Pallets", f"{total:,.2f}")
            c2.metric("Promedio Lateral", f"{(products['lateral'].sum()/total*100):.2f}%")
            c3.metric("Promedio Trasera", f"{(products['trasera'].sum()/total*100):.2f}%")
            st.dataframe(products.style.format({
                'total_pallets': '{:,.2f}', 'lateral': '{:,.2f}', 'trasera': '{:,.2f}',
                'porcentaje_total': '{:.2f}%', 'porcentaje_lateral': '{:.2f}%', 'porcentaje_trasera': '{:.2f}%'
            }))
            fig = go.Figure(data=[
                go.Bar(name='Lateral', x=products['texto_breve_material'], y=products['porcentaje_lateral'],
                       text=products['porcentaje_lateral'].apply(lambda x: f'{x:.1f}%')),
                go.Bar(name='Trasera', x=products['texto_breve_material'], y=products['porcentaje_trasera'],
                       text=products['porcentaje_trasera'].apply(lambda x: f'{x:.1f}%'))
            ])
            fig.update_layout(barmode='group', title=f'Lateral vs Trasera por Producto - {formato}',
                              xaxis_title='Producto', yaxis_title='Porcentaje')
            st.plotly_chart(fig, use_container_width=True)

    with tab_l:
        if df_lineas is not None:
            products = get_product_details(df_lineas, formato, 'lineas')
            st.subheader("Detalle de Productos - Líneas")
            st.metric("Total Pallets", f"{products['total_pallets'].sum():,.2f}")
            st.dataframe(products.style.format({'total_pallets': '{:,.2f}', 'porcentaje_total': '{:.2f}%'}))
            fig = px.bar(products, x='texto_breve_material', y='total_pallets',
                         title=f'Distribución de Pallets por Producto - {formato}')
            st.plotly_chart(fig, use_container_width=True)

    with tab_r:
        if df_recepciones is not None:
            products = get_product_details(df_recepciones, formato, 'recepciones')
            st.subheader("Detalle de Productos - Recepciones")
            st.metric("Total Pallets", f"{products['total_pallets'].sum():,.2f}")
            st.dataframe(products.style.format({'total_pallets': '{:,.2f}', 'porcentaje_total': '{:.2f}%'}))
            fig = px.bar(products, x='Texto breve material', y='total_pallets',
                         title=f'Distribución de Pallets por Producto - {formato}')
            st.plotly_chart(fig, use_container_width=True)

# ─────────────────────────────────────────────
# PRODUCT SUMMARY
# ─────────────────────────────────────────────

def get_product_summary(df, formato, source_type='cargas'):
    if source_type == 'cargas':
        df_filtered = df[df['formato'] == formato].copy()
        summary = df_filtered.groupby('texto_breve_material').agg(
            total_pallets=('total_pallets', 'sum'),
            lateral=('lateral', 'sum'),
            trasera=('trasera', 'sum'),
            num_movimientos=('fecha', 'count')
        ).reset_index()
        total = summary['total_pallets'].sum()
        summary['participacion_total'] = (summary['total_pallets'] / total * 100).round(2)
        summary['promedio_pallets_por_movimiento'] = (summary['total_pallets'] / summary['num_movimientos']).round(2)
        summary['eficiencia_carga'] = ((summary['lateral'] + summary['trasera']) / summary['num_movimientos']).round(2)

        df_filtered['mes'] = df_filtered['fecha'].dt.to_period('M')
        tendencia = df_filtered.groupby(['texto_breve_material', 'mes'])['total_pallets'].sum().reset_index()
        tendencia['mes_anterior'] = tendencia.groupby('texto_breve_material')['total_pallets'].shift(1)
        tendencia['variacion'] = ((tendencia['total_pallets'] - tendencia['mes_anterior']) / tendencia['mes_anterior'] * 100).fillna(0)
        ultima_tendencia = tendencia.groupby('texto_breve_material')['variacion'].last()
        summary['tendencia_mensual'] = summary['texto_breve_material'].map(ultima_tendencia)

        summary = summary.rename(columns={
            'texto_breve_material': 'Formato',
            'total_pallets': 'Total Pallets',
            'participacion_total': '% Participación',
            'promedio_pallets_por_movimiento': 'Pallets/Movimiento',
            'eficiencia_carga': 'Eficiencia Carga',
            'tendencia_mensual': 'Tendencia (%)',
            'num_movimientos': 'Num Movimientos'
        })

    elif source_type == 'lineas':
        df_filtered = df[df['formato'] == formato].copy()
        summary = df_filtered.groupby('texto_breve_material').agg(
            total_pallets=('total_pallets', 'sum'),
            num_movimientos=('total_pallets', 'count'),
            promedio_pallets=('total_pallets', 'mean'),
            num_dias=('fecha_de_documento', 'nunique')
        ).reset_index()

        max_date = df_filtered['fecha_de_documento'].max()
        min_date = df_filtered['fecha_de_documento'].min()
        total_days = max(1, (max_date - min_date).days + 1) if pd.notna(max_date) and pd.notna(min_date) else 1

        summary['Frecuencia Movimiento'] = (summary['num_dias'] / total_days * 100).round(2)
        summary['Pallets por Día Activo'] = (summary['total_pallets'] / summary['num_dias']).round(2)
        summary = summary.rename(columns={
            'texto_breve_material': 'Formato',
            'total_pallets': 'Total Pallets',
            'num_movimientos': 'Num Movimientos',
            'promedio_pallets': 'Promedio Pallets',
            'num_dias': 'Num_Dias'
        })

    else:  # recepciones
        df_filtered = df[df['Formato'] == formato].copy()
        summary = df_filtered.groupby('Texto breve material').agg(
            total_pallets=('total_pallets', 'sum'),
            num_recepciones=('total_pallets', 'count'),
            promedio_pallets=('total_pallets', 'mean'),
            num_dias=('Fecha de documento', 'nunique')
        ).reset_index()

        max_date = df_filtered['Fecha de documento'].max()
        min_date = df_filtered['Fecha de documento'].min()
        total_days = max(1, (max_date - min_date).days + 1) if pd.notna(max_date) and pd.notna(min_date) else 1

        summary['Frecuencia Recepción'] = (summary['num_dias'] / total_days * 100).round(2)
        summary['Pallets por Recepción'] = (summary['total_pallets'] / summary['num_recepciones']).round(2)
        summary = summary.rename(columns={
            'Texto breve material': 'Formato',
            'total_pallets': 'Total Pallets',
            'num_recepciones': 'Num Recepciones',
            'promedio_pallets': 'Promedio Pallets',
            'num_dias': 'Num_Dias'
        })

    return summary

def show_format_summary(formato, df_cargas, df_lineas, df_recepciones):
    if not formato:
        return
    st.header(f"Análisis Detallado - Formato: {formato}")
    tab_c, tab_l, tab_r = st.tabs(["Cargas", "Líneas", "Recepciones"])

    with tab_c:
        if df_cargas is not None:
            st.subheader("Análisis de Cargas por Producto")
            summary = get_product_summary(df_cargas, formato, 'cargas')
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Pallets",    f"{summary['Total Pallets'].sum():,.0f}")
            c2.metric("Eficiencia Prom.", f"{summary['Eficiencia Carga'].mean():.2f}")
            c3.metric("Productos Activos",f"{len(summary)}")
            st.dataframe(summary.style.format({
                'Total Pallets': '{:,.0f}', '% Participación': '{:.2f}%',
                'Pallets/Movimiento': '{:.2f}', 'Eficiencia Carga': '{:.2f}', 'Tendencia (%)': '{:+.2f}%'
            }).background_gradient(subset=['% Participación'], cmap='YlOrRd'))
            fig = go.Figure()
            fig.add_trace(go.Bar(x=summary['Formato'], y=summary['Total Pallets'], name='Total Pallets'))
            fig.add_trace(go.Scatter(x=summary['Formato'], y=summary['Eficiencia Carga'],
                                     name='Eficiencia', yaxis='y2'))
            fig.update_layout(title='Volumen vs Eficiencia',
                              yaxis2=dict(title='Eficiencia', overlaying='y', side='right'))
            st.plotly_chart(fig, use_container_width=True)

    with tab_l:
        if df_lineas is not None:
            st.subheader("Análisis de Líneas por Producto")
            summary = get_product_summary(df_lineas, formato, 'lineas')
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Pallets",      f"{summary['Total Pallets'].sum():,.0f}")
            c2.metric("Promedio Diario",    f"{summary['Pallets por Día Activo'].mean():.2f}")
            c3.metric("Frecuencia Prom.",   f"{summary['Frecuencia Movimiento'].mean():.2f}%")
            st.dataframe(summary.style.format({
                'Total Pallets': '{:,.0f}', 'Promedio Pallets': '{:.2f}',
                'Frecuencia Movimiento': '{:.2f}%', 'Pallets por Día Activo': '{:.2f}'
            }).background_gradient(subset=['Frecuencia Movimiento'], cmap='YlOrRd'))

    with tab_r:
        if df_recepciones is not None:
            st.subheader("Análisis de Recepciones por Producto")
            summary = get_product_summary(df_recepciones, formato, 'recepciones')
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Pallets",         f"{summary['Total Pallets'].sum():,.0f}")
            c2.metric("Promedio por Recepción",f"{summary['Pallets por Recepción'].mean():.2f}")
            c3.metric("Frecuencia Prom.",       f"{summary['Frecuencia Recepción'].mean():.2f}%")
            st.dataframe(summary.style.format({
                'Total Pallets': '{:,.0f}', 'Promedio Pallets': '{:.2f}',
                'Frecuencia Recepción': '{:.2f}%', 'Pallets por Recepción': '{:.2f}'
            }).background_gradient(subset=['Frecuencia Recepción'], cmap='YlOrRd'))

# ─────────────────────────────────────────────
# TIME PERIOD MAX ANALYSIS
# ─────────────────────────────────────────────

def get_time_period_max(df, source_type='cargas'):
    if source_type == 'cargas':
        df = df.copy()
        df['fecha'] = pd.to_datetime(df['fecha'])
        df['dia']        = df['fecha'].dt.date
        df['semana']     = df['fecha'].dt.isocalendar().week
        df['mes']        = df['fecha'].dt.to_period('M')
        df['trimestre']  = df['fecha'].dt.to_period('Q')
        df['semestre']   = df['fecha'].dt.to_period('H')
        df['año']        = df['fecha'].dt.year

        def _max_info(grouped, col):
            s = grouped[col].sum()
            return {'val': s.max(), 'fecha': s.idxmax()}

        max_values = {}
        for periodo, grp_key in [
            ('Diario', 'dia'), ('Semanal', ['año','semana']),
            ('Mensual','mes'), ('Trimestral','trimestre'),
            ('Semestral','semestre'), ('Anual','año')
        ]:
            g = df.groupby(grp_key)
            max_values[periodo] = {
                'lateral':         g['lateral'].sum().max(),
                'trasera':         g['trasera'].sum().max(),
                'total':           g['total_pallets'].sum().max(),
                'fecha_max_lateral': str(g['lateral'].sum().idxmax()),
                'fecha_max_trasera': str(g['trasera'].sum().idxmax()),
                'fecha_max_total':   str(g['total_pallets'].sum().idxmax()),
            }

    elif source_type == 'lineas':
        df = df.copy()
        df['fecha_de_documento'] = pd.to_datetime(df['fecha_de_documento'])
        df['dia']       = df['fecha_de_documento'].dt.date
        df['semana']    = df['fecha_de_documento'].dt.isocalendar().week
        df['mes']       = df['fecha_de_documento'].dt.to_period('M')
        df['trimestre'] = df['fecha_de_documento'].dt.to_period('Q')
        df['semestre']  = df['fecha_de_documento'].dt.to_period('H')
        df['año']       = df['fecha_de_documento'].dt.year

        max_values = {}
        for periodo, grp_key in [
            ('Diario','dia'), ('Semanal',['año','semana']),
            ('Mensual','mes'), ('Trimestral','trimestre'),
            ('Semestral','semestre'), ('Anual','año')
        ]:
            g = df.groupby(grp_key)
            max_values[periodo] = {
                'total':         g['total_pallets'].sum().max(),
                'fecha_max_total': str(g['total_pallets'].sum().idxmax()),
            }

    else:  # recepciones
        df = df.copy()
        df['Fecha de documento'] = pd.to_datetime(df['Fecha de documento'])
        df['dia']       = df['Fecha de documento'].dt.date
        df['semana']    = df['Fecha de documento'].dt.isocalendar().week
        df['mes']       = df['Fecha de documento'].dt.to_period('M')
        df['trimestre'] = df['Fecha de documento'].dt.to_period('Q')
        df['semestre']  = df['Fecha de documento'].dt.to_period('H')
        df['año']       = df['Fecha de documento'].dt.year

        max_values = {}
        for periodo, grp_key in [
            ('Diario','dia'), ('Semanal',['año','semana']),
            ('Mensual','mes'), ('Trimestral','trimestre'),
            ('Semestral','semestre'), ('Anual','año')
        ]:
            g = df.groupby(grp_key)
            max_values[periodo] = {
                'total':                g['total_pallets'].sum().max(),
                'fecha_max_total':      str(g['total_pallets'].sum().idxmax()),
                'num_recepciones':      g.size().max(),
                'fecha_max_recepciones':str(g.size().idxmax()),
            }

    return max_values

def show_time_period_analysis(df_cargas, df_lineas, df_recepciones):
    st.header("Análisis de Máximos por Período")
    tab1, tab2, tab3 = st.tabs(["Cargas", "Producción", "Recepciones"])

    with tab1:
        if df_cargas is not None:
            max_c = get_time_period_max(df_cargas, 'cargas')
            st.subheader("Máximos Despachos")
            for periodo, v in max_c.items():
                st.write(f"### {periodo}")
                c1, c2, c3 = st.columns(3)
                c1.metric("Máx. Lateral", f"{v['lateral']:,.2f}", help=f"Fecha: {v['fecha_max_lateral']}")
                c2.metric("Máx. Trasera", f"{v['trasera']:,.2f}", help=f"Fecha: {v['fecha_max_trasera']}")
                c3.metric("Máx. Total",   f"{v['total']:,.2f}",   help=f"Fecha: {v['fecha_max_total']}")

    with tab2:
        if df_lineas is not None:
            max_l = get_time_period_max(df_lineas, 'lineas')
            st.subheader("Máximos Producción")
            for periodo, v in max_l.items():
                st.write(f"### {periodo}")
                st.metric("Máx. Total Producido", f"{v['total']:,.2f}", help=f"Fecha: {v['fecha_max_total']}")

    with tab3:
        if df_recepciones is not None:
            max_r = get_time_period_max(df_recepciones, 'recepciones')
            st.subheader("Máximos Recepciones")
            for periodo, v in max_r.items():
                st.write(f"### {periodo}")
                c1, c2 = st.columns(2)
                c1.metric("Máx. Pallets Recibidos",     f"{v['total']:,.2f}",           help=f"Fecha: {v['fecha_max_total']}")
                c2.metric("Máx. Número de Recepciones", f"{v['num_recepciones']:,.0f}", help=f"Fecha: {v['fecha_max_recepciones']}")

# ─────────────────────────────────────────────
# WEEKLY ANALYSIS
# ─────────────────────────────────────────────

def add_period_column(df, fecha_col, periodo):
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
    else:
        df['periodo'] = fecha.dt.year
    return df

def get_weekly_analysis(df, formato, num_semanas=52):
    df = df.copy()
    fecha_column = next((c for c in df.columns if c in ['fecha', 'fecha_de_documento', 'Fecha de documento']), None)
    if not fecha_column:
        st.error("No se encontró la columna de fecha en el DataFrame")
        return None

    df['_fecha_tmp'] = pd.to_datetime(df[fecha_column])
    df['semana'] = df['_fecha_tmp'].dt.isocalendar().week
    df['año']    = df['_fecha_tmp'].dt.isocalendar().year

    años_disponibles = sorted(df['año'].unique())
    año_analisis = años_disponibles[-1]  # usa el año más reciente en los datos

    todas_semanas = pd.DataFrame(
        [(año_analisis, w) for w in range(1, num_semanas + 1)],
        columns=['año', 'semana']
    )

    formato_column   = next((c for c in df.columns if c in ['formato', 'Formato']), None)
    material_column  = next((c for c in df.columns if c in ['texto_breve_material', 'Texto breve material']), None)
    cantidad_column  = next((c for c in df.columns if c in ['total_pallets', 'pallets', 'Cant Pallet']), None)

    if formato and formato_column:
        df = df[df[formato_column] == formato]

    weekly_avg = df.groupby(['año', 'semana', formato_column, material_column])[cantidad_column].sum().reset_index()

    grid = pd.merge(todas_semanas,
                    weekly_avg[[formato_column, material_column]].drop_duplicates(),
                    how='cross')

    weekly_complete = pd.merge(grid, weekly_avg,
                                on=['año', 'semana', formato_column, material_column],
                                how='left')
    weekly_complete[cantidad_column] = weekly_complete[cantidad_column].fillna(0)
    weekly_complete['promedio_diario'] = weekly_complete[cantidad_column] / 7

    stats = weekly_complete.groupby([formato_column, material_column]).agg(
        promedio_semanal=(cantidad_column, 'mean'),
        desviacion_std=(cantidad_column, 'std'),
        min_semanal=(cantidad_column, 'min'),
        max_semanal=(cantidad_column, 'max'),
        num_semanas=(cantidad_column, 'count'),
        promedio_diario=('promedio_diario', 'mean'),
        desviacion_std_diaria=('promedio_diario', 'std'),
        min_diario=('promedio_diario', 'min'),
        max_diario=('promedio_diario', 'max'),
    ).round(2).reset_index()

    return stats

def analisis_semanal_detallado(df, formato):
    df = df.copy()
    fecha_column = next((c for c in df.columns if c in ['fecha', 'fecha_de_documento', 'Fecha de documento']), None)
    if not fecha_column:
        st.error("No se encontró la columna de fecha")
        return None

    df['_fecha_tmp'] = pd.to_datetime(df[fecha_column])
    df['año']    = df['_fecha_tmp'].dt.isocalendar().year
    df['semana'] = df['_fecha_tmp'].dt.isocalendar().week

    if formato:
        formato_column = next((c for c in df.columns if c in ['formato', 'Formato']), None)
        if formato_column:
            df = df[df[formato_column] == formato]

    pallets_column = next((c for c in df.columns if c in ['total_pallets', 'pallets', 'Cant Pallet']), None)
    pps = df.groupby(['año', 'semana'])[pallets_column].sum().reset_index()
    promedio_global = pps[pallets_column].mean()
    pps['desviacion_promedio'] = pps[pallets_column] - promedio_global
    pps['porcentaje_desviacion'] = (pps['desviacion_promedio'] / promedio_global * 100).round(2)

    def categorizar(d):
        if d > 50:   return 'Muy por encima (+50%)'
        if d > 20:   return 'Por encima (+20%)'
        if d > 0:    return 'Ligeramente por encima (+)'
        if d == 0:   return 'Igual al promedio'
        if d > -20:  return 'Ligeramente por debajo (-)'
        if d > -50:  return 'Por debajo (-20%)'
        return 'Muy por debajo (-50%)'

    pps['categoria_desviacion'] = pps['porcentaje_desviacion'].apply(categorizar)
    pps.columns = ['Año', 'Semana', 'Pallets', 'Desviación del Promedio', 'Porcentaje Desviación', 'Categoría Desviación']
    return pps

def show_product_analysis_by_period(formato, df_cargas, df_lineas, df_recepciones, periodo):
    if not formato:
        return
    st.header(f"Análisis de {formato} por {periodo}")

    for label, df, source in [
        ("Cargas", df_cargas, 'cargas'),
        ("Líneas", df_lineas, 'lineas'),
        ("Recepciones", df_recepciones, 'recepciones')
    ]:
        if df is not None:
            st.subheader(f"{label} - Promedio Semanal")
            weekly = get_weekly_analysis(df, formato)
            if weekly is not None:
                if source == 'cargas':
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Promedio Semanal Global", f"{weekly['promedio_semanal'].mean():,.0f}")
                    c2.metric("Máx. Semanal",            f"{weekly['max_semanal'].max():,.0f}")
                    c3.metric("Mín. Semanal",             f"{weekly['min_semanal'].min():,.0f}")
                weekly_con_total = agregar_totales(weekly)
                st.dataframe(weekly_con_total.style.format({
                    'promedio_semanal': '{:,.0f}', 'desviacion_std': '{:,.2f}',
                    'min_semanal': '{:,.0f}', 'max_semanal': '{:,.0f}', 'num_semanas': '{:,.0f}'
                }))

    st.subheader("Análisis Semanal Detallado")

    if df_cargas is not None:
        st.subheader("Cargas - Análisis Semanal")
        semanal = analisis_semanal_detallado(df_cargas, formato)
        if semanal is not None:
            c1, c2, c3 = st.columns(3)
            c1.metric("Promedio Semanal", f"{semanal['Pallets'].mean():,.0f}")
            c2.metric("Máximo Semanal",   f"{semanal['Pallets'].max():,.0f}")
            c3.metric("Mínimo Semanal",   f"{semanal['Pallets'].min():,.0f}")
            st.dataframe(semanal.style.format({
                'Pallets': '{:,.0f}', 'Desviación del Promedio': '{:,.0f}', 'Porcentaje Desviación': '{:.2f}%'
            }).background_gradient(subset=['Porcentaje Desviación'], cmap='RdYlGn_r'))

            fig = go.Figure()
            fig.add_trace(go.Bar(x=semanal['Semana'], y=semanal['Pallets'], name='Pallets',
                                 text=semanal['Pallets'].apply(lambda x: f'{x:,.0f}'), textposition='auto'))
            fig.add_trace(go.Scatter(x=semanal['Semana'], y=semanal['Porcentaje Desviación'],
                                     name='% Desviación', yaxis='y2'))
            fig.update_layout(title='Pallets y Desviación por Semana',
                              yaxis=dict(title='Pallets'),
                              yaxis2=dict(title='% Desviación', overlaying='y', side='right'))
            st.plotly_chart(fig, use_container_width=True)

            # Weekly bar chart with average line
            df_c = df_cargas.copy()
            fecha_col = next((c for c in df_c.columns if c in ['fecha','fecha_de_documento','Fecha de documento']), None)
            df_c['_fecha'] = pd.to_datetime(df_c[fecha_col])
            df_c['año']    = df_c['_fecha'].dt.isocalendar().year
            df_c['semana'] = df_c['_fecha'].dt.isocalendar().week
            fmt_col = next((c for c in df_c.columns if c in ['formato','Formato']), None)
            if fmt_col:
                df_c = df_c[df_c[fmt_col] == formato]
            pallets_col = next((c for c in df_c.columns if c in ['total_pallets','pallets','Cant Pallet']), None)
            pps = df_c.groupby(['año','semana'])[pallets_col].sum().reset_index()
            pps['semana_label'] = pps['año'].astype(str) + '-W' + pps['semana'].astype(str)
            promedio_global = pps[pallets_col].mean()

            fig2 = go.Figure()
            fig2.add_trace(go.Bar(x=pps['semana_label'], y=pps[pallets_col], name='Pallets por Semana',
                                  text=pps[pallets_col].apply(lambda x: f'{x:,.0f}'), textposition='outside'))
            fig2.add_trace(go.Scatter(x=pps['semana_label'], y=[promedio_global]*len(pps),
                                      mode='lines', name='Promedio',
                                      line=dict(color='red', width=2, dash='dash')))
            fig2.update_layout(title=f'Pallets por Semana - {formato}',
                               xaxis_title='Semana', yaxis_title='Pallets')
            st.plotly_chart(fig2, use_container_width=True)

# ─────────────────────────────────────────────
# ABC ANALYSIS
# ─────────────────────────────────────────────

def get_abc_classification(df, source_type='cargas'):
    if source_type == 'cargas':
        movements = df.groupby('formato').agg(
            Frecuencia=('fecha', 'count'),
            Total_Pallets=('total_pallets', 'sum'),
            Lateral=('lateral', 'sum'),
            Trasera=('trasera', 'sum')
        ).reset_index().rename(columns={'formato': 'Formato'})
    elif source_type == 'lineas':
        movements = df.groupby('formato').agg(
            Frecuencia=('fecha_de_documento', 'count'),
            Total_Pallets=('total_pallets', 'sum')
        ).reset_index().rename(columns={'formato': 'Formato'})
    else:
        movements = df.groupby('Formato').agg(
            Frecuencia=('Fecha de documento', 'count'),
            Total_Pallets=('total_pallets', 'sum')
        ).reset_index()

    total = movements['Total_Pallets'].sum()
    movements['Porcentaje'] = (movements['Total_Pallets'] / total * 100).round(2)
    movements = movements.sort_values('Total_Pallets', ascending=False)
    movements['Porcentaje_Acumulado'] = movements['Porcentaje'].cumsum()
    movements['Clasificacion'] = movements['Porcentaje_Acumulado'].apply(
        lambda x: 'A' if x <= 80 else ('B' if x <= 95 else 'C')
    )
    return movements

def show_abc_analysis(df_cargas, df_lineas, df_recepciones):
    st.header("Análisis ABC por Frecuencia de Movimientos")
    tab_c, tab_l, tab_r = st.tabs(["Cargas", "Líneas", "Recepciones"])

    def _render_abc(abc, source_type):
        has_lat = 'Lateral' in abc.columns
        summary = abc.groupby('Clasificacion').agg(
            Formatos=('Formato', 'count'),
            Frecuencia=('Frecuencia', 'sum'),
            Total_Pallets=('Total_Pallets', 'sum')
        ).reset_index()
        summary['Pct_Productos']   = (summary['Formatos']   / summary['Formatos'].sum()   * 100).round(2)
        summary['Pct_Movimientos'] = (summary['Frecuencia'] / summary['Frecuencia'].sum() * 100).round(2)

        st.write("### Resumen por Clasificación")
        for _, row in summary.iterrows():
            st.write(f"#### Clasificación {row['Clasificacion']}")
            c1, c2, c3 = st.columns(3)
            c1.metric("Formatos",      f"{row['Formatos']:.0f} ({row['Pct_Productos']:.1f}%)")
            c2.metric("Movimientos",   f"{row['Frecuencia']:.0f} ({row['Pct_Movimientos']:.1f}%)")
            c3.metric("Total Pallets", f"{row['Total_Pallets']:,.0f}")

        fig = go.Figure()
        fig.add_trace(go.Bar(x=abc['Formato'], y=abc['Porcentaje'], name='Porcentaje'))
        fig.add_trace(go.Scatter(x=abc['Formato'], y=abc['Porcentaje_Acumulado'],
                                 name='% Acumulado', yaxis='y2'))
        fig.update_layout(title='Diagrama de Pareto - Total de Pallets',
                          yaxis=dict(title='Porcentaje'),
                          yaxis2=dict(title='% Acumulado', overlaying='y', side='right', range=[0,100]))
        st.plotly_chart(fig, use_container_width=True)

        fmt = {'Frecuencia': '{:,.0f}', 'Total_Pallets': '{:,.0f}',
               'Porcentaje': '{:.2f}%', 'Porcentaje_Acumulado': '{:.2f}%'}
        if has_lat:
            fmt.update({'Lateral': '{:,.0f}', 'Trasera': '{:,.0f}'})
        st.write("### Detalle por Producto")
        st.dataframe(abc.style.format(fmt).background_gradient(subset=['Porcentaje'], cmap='YlOrRd'))

    with tab_c:
        if df_cargas is not None:
            st.subheader("Análisis ABC de Cargas")
            _render_abc(get_abc_classification(df_cargas, 'cargas'), 'cargas')
    with tab_l:
        if df_lineas is not None:
            st.subheader("Análisis ABC de Líneas")
            _render_abc(get_abc_classification(df_lineas, 'lineas'), 'lineas')
    with tab_r:
        if df_recepciones is not None:
            st.subheader("Análisis ABC de Recepciones")
            _render_abc(get_abc_classification(df_recepciones, 'recepciones'), 'recepciones')

# ─────────────────────────────────────────────
# LOCATION STRATEGY  (single, clean definition)
# ─────────────────────────────────────────────

# ═══════════════════════════════════════════════════════
# MAIN APP
# ═══════════════════════════════════════════════════════

st.title("📦 Análisis de Movimiento de Pallets")

st.sidebar.header("Carga de Archivos")
cargas_file      = st.sidebar.file_uploader("Cargar Cargas.csv",      type=['csv'])
lineas_file      = st.sidebar.file_uploader("Cargar Lineas.csv",       type=['csv'])
recepciones_file = st.sidebar.file_uploader("Cargar Recepciones.csv",  type=['csv'])

st.sidebar.markdown("---")
top_n = st.sidebar.slider("Mostrar Top N Productos", min_value=1, max_value=50, value=10,
                           help="Cantidad de productos a mostrar en gráficos y tablas")

st.sidebar.markdown("---")
periodo_analisis = st.sidebar.selectbox(
    "Período de Análisis",
    ["Diario","Semanal","Mensual","Trimestral","Semestral","Anual"],
    help="Período para agrupar los datos"
)

if cargas_file or lineas_file or recepciones_file:
    initialize_session_state()

    # ── Load data (once, at top level) ──────────────────
    df_cargas      = process_cargas(cargas_file)       if cargas_file      else None
    df_lineas      = process_lineas(lineas_file)        if lineas_file      else None
    df_recepciones = process_recepciones(recepciones_file) if recepciones_file else None

    tab1, tab2, tab3, tab4 = st.tabs([
        "Análisis General", "Análisis por Formato",
        "Análisis por Período", "Análisis ABC"
    ])

    # ── TAB 1: General ───────────────────────────────────
    with tab1:
        col1, col2, col3 = st.columns(3)
        plot_data = []

        if df_cargas is not None:
            with col1:
                st.subheader("Cargas")
                total = df_cargas['total_pallets'].sum()
                st.metric("Total Pallets",  f"{total:,.2f}")
                st.metric("Total Registros", len(df_cargas))
                plot_data.append({'Fuente': 'Cargas', 'Total Pallets': total})
                st.subheader("Desglose por Mes")
                st.dataframe(df_cargas.groupby(df_cargas['fecha'].dt.strftime('%Y-%m'))[['total_pallets']].sum())
                st.write("Columnas disponibles:", df_cargas.columns.tolist())

        if df_lineas is not None:
            with col2:
                st.subheader("Líneas")
                total = df_lineas['total_pallets'].sum()
                st.metric("Total Pallets",  f"{total:,.2f}")
                st.metric("Total Registros", len(df_lineas))
                plot_data.append({'Fuente': 'Líneas', 'Total Pallets': total})
                st.subheader("Desglose por Mes")
                st.dataframe(df_lineas.groupby(df_lineas['fecha_de_documento'].dt.strftime('%Y-%m'))[['total_pallets']].sum())
                st.write("Columnas disponibles:", df_lineas.columns.tolist())

        if df_recepciones is not None:
            with col3:
                st.subheader("Recepciones")
                total = df_recepciones['total_pallets'].sum()
                st.metric("Total Pallets",  f"{total:,.2f}")
                st.metric("Total Registros", len(df_recepciones))
                plot_data.append({'Fuente': 'Recepciones', 'Total Pallets': total})
                st.subheader("Desglose por Mes")
                st.dataframe(df_recepciones.groupby(df_recepciones['Fecha de documento'].dt.strftime('%Y-%m'))[['total_pallets']].sum())
                st.write("Columnas disponibles:", df_recepciones.columns.tolist())

        if plot_data:
            st.subheader("Comparativa de Pallets por Fuente")
            fig = px.bar(pd.DataFrame(plot_data), x='Fuente', y='Total Pallets',
                         title='Comparación de Pallets por Fuente', color='Fuente')
            st.plotly_chart(fig, use_container_width=True)

    # ── TAB 2: Por Formato ───────────────────────────────
    with tab2:
        resumen_tab, detalle_tab = st.tabs(["Resumen por Formato", "Detalle de Formato"])

        # Collect all available formats
        all_formats = set()
        if df_cargas      is not None: all_formats.update(df_cargas['formato'].unique())
        if df_lineas       is not None: all_formats.update(df_lineas['formato'].unique())
        if df_recepciones  is not None: all_formats.update(df_recepciones['Formato'].unique())
        formato_options = ["Todos"] + sorted(list(all_formats))

        with resumen_tab:
            sel_resumen = st.selectbox("Filtrar por Formato", formato_options,
                                       index=formato_options.index(st.session_state.selected_format),
                                       key="format_selector_resumen")
            if sel_resumen != st.session_state.selected_format:
                st.session_state.selected_format = sel_resumen

            if st.session_state.selected_format != "Todos":
                show_format_summary(st.session_state.selected_format, df_cargas, df_lineas, df_recepciones)
            else:
                st.header("Análisis por Formato")

                if df_cargas is not None:
                    st.subheader("Cargas - Análisis por Formato")
                    fc = df_cargas.groupby('formato').agg(
                        total_pallets=('total_pallets','sum'),
                        lateral=('lateral','sum'),
                        trasera=('trasera','sum'),
                        registros=('texto_breve_material','count')
                    ).reset_index()
                    total = fc['total_pallets'].sum()
                    fc['pct_lateral'] = (fc['lateral'] / fc['total_pallets'] * 100).round(2)
                    fc['pct_trasera'] = (fc['trasera'] / fc['total_pallets'] * 100).round(2)
                    fc['pct_total']   = (fc['total_pallets'] / total * 100).round(2)
                    fc.columns = ['Formato','Total Pallets','Pallets Lateral','Pallets Trasera',
                                  'Cantidad de Registros','Porcentaje Lateral','Porcentaje Trasera','Porcentaje del Total']
                    fc = fc.sort_values('Total Pallets', ascending=False).head(top_n)
                    # Note: agregar_totales AFTER head(top_n) — totals are for shown rows only
                    fc_con_total = agregar_totales(fc)
                    st.dataframe(fc_con_total.style.format({
                        'Total Pallets': '{:,.2f}', 'Pallets Lateral': '{:,.2f}', 'Pallets Trasera': '{:,.2f}',
                        'Cantidad de Registros': '{:,.0f}', 'Porcentaje Lateral': '{:.2f}%',
                        'Porcentaje Trasera': '{:.2f}%', 'Porcentaje del Total': '{:.2f}%'
                    }), use_container_width=True)

                    fig = go.Figure(data=[
                        go.Bar(name='Lateral', x=fc['Formato'], y=fc['Porcentaje Lateral'],
                               text=fc['Porcentaje Lateral'].apply(lambda x: f'{x:.1f}%'), textposition='auto'),
                        go.Bar(name='Trasera', x=fc['Formato'], y=fc['Porcentaje Trasera'],
                               text=fc['Porcentaje Trasera'].apply(lambda x: f'{x:.1f}%'), textposition='auto'),
                    ])
                    fig.update_layout(barmode='stack', title=f'Lateral vs Trasera (Top {top_n})',
                                      xaxis_title='Formato', yaxis_title='Porcentaje')
                    st.plotly_chart(fig, use_container_width=True)

                if df_lineas is not None:
                    st.subheader("Líneas - Análisis por Formato")
                    fl = df_lineas.groupby('formato').agg(
                        total_pallets=('total_pallets','sum'), registros=('texto_breve_material','count')
                    ).reset_index()
                    fl.columns = ['Formato','Total Pallets','Cantidad de Registros']
                    fl['Porcentaje del Total'] = (fl['Total Pallets'] / fl['Total Pallets'].sum() * 100).round(2)
                    fl = fl.sort_values('Total Pallets', ascending=False).head(top_n)
                    fl_con_total = agregar_totales(fl)
                    st.dataframe(fl_con_total.style.format({
                        'Total Pallets': '{:,.2f}', 'Cantidad de Registros': '{:,.0f}', 'Porcentaje del Total': '{:,.2f}%'
                    }), use_container_width=True)
                    st.plotly_chart(px.bar(fl, x='Formato', y='Total Pallets',
                                          title=f'Pallets por Formato - Líneas (Top {top_n})', color='Formato'),
                                   use_container_width=True)

                if df_recepciones is not None:
                    st.subheader("Recepciones - Análisis por Formato")
                    fr = df_recepciones.groupby('Formato').agg(
                        total_pallets=('total_pallets','sum'), registros=('Texto breve material','count')
                    ).reset_index()
                    fr.columns = ['Formato','Total Pallets','Cantidad de Registros']
                    fr['Porcentaje del Total'] = (fr['Total Pallets'] / fr['Total Pallets'].sum() * 100).round(2)
                    fr = fr.sort_values('Total Pallets', ascending=False).head(top_n)
                    fr_con_total = agregar_totales(fr)
                    st.dataframe(fr_con_total.style.format({
                        'Total Pallets': '{:,.2f}', 'Cantidad de Registros': '{:,.0f}', 'Porcentaje del Total': '{:,.2f}%'
                    }), use_container_width=True)
                    st.plotly_chart(px.bar(fr, x='Formato', y='Total Pallets',
                                          title=f'Pallets por Formato - Recepciones (Top {top_n})', color='Formato'),
                                   use_container_width=True)

                # Cross-source comparison
                if df_cargas is not None and df_lineas is not None and df_recepciones is not None:
                    st.subheader("Comparativa de Formatos entre Archivos")
                    # Recompute without head() limit for comparison (use original groupby)
                    c_tot = df_cargas.groupby('formato')['total_pallets'].sum().reset_index().rename(
                        columns={'formato':'Formato','total_pallets':'Cargas'})
                    l_tot = df_lineas.groupby('formato')['total_pallets'].sum().reset_index().rename(
                        columns={'formato':'Formato','total_pallets':'Líneas'})
                    r_tot = df_recepciones.groupby('Formato')['total_pallets'].sum().reset_index().rename(
                        columns={'total_pallets':'Recepciones'})

                    comp = c_tot.merge(l_tot, on='Formato', how='outer') \
                                .merge(r_tot, on='Formato', how='outer').fillna(0)
                    comp['Total Pallets'] = comp['Cargas'] + comp['Líneas'] + comp['Recepciones']

                    fig_comp = go.Figure(data=[
                        go.Bar(name='Cargas',      x=comp['Formato'], y=comp['Cargas']),
                        go.Bar(name='Líneas',       x=comp['Formato'], y=comp['Líneas']),
                        go.Bar(name='Recepciones',  x=comp['Formato'], y=comp['Recepciones']),
                    ])
                    fig_comp.update_layout(barmode='group', title='Comparativa de Pallets por Formato',
                                           xaxis_title='Formato', yaxis_title='Total Pallets')
                    st.plotly_chart(fig_comp, use_container_width=True)
                    st.dataframe(comp)

        with detalle_tab:
            st.header("Detalle por Formato")
            sel_detalle = st.selectbox("Filtrar por Formato", formato_options,
                                       index=formato_options.index(st.session_state.selected_format),
                                       key="format_selector_detalle")
            if sel_detalle != st.session_state.selected_format:
                st.session_state.selected_format = sel_detalle

            if st.session_state.selected_format != "Todos":
                show_format_details(st.session_state.selected_format, df_cargas, df_lineas, df_recepciones)
                show_product_analysis_by_period(
                    st.session_state.selected_format,
                    df_cargas, df_lineas, df_recepciones, periodo_analisis
                )
            else:
                st.info("Selecciona un formato específico para ver sus detalles")

    # ── TAB 3: Por Período ───────────────────────────────
    with tab3:
        show_time_period_analysis(df_cargas, df_lineas, df_recepciones)

    # ── TAB 4: ABC ───────────────────────────────────────
    with tab4:
        show_abc_analysis(df_cargas, df_lineas, df_recepciones)

else:
    st.info("👈 Por favor, carga los archivos CSV en el panel lateral para comenzar el análisis.")

st.sidebar.markdown("---")
st.sidebar.markdown("""
### Información
- **Cargas**: suma de lateral + trasera  
- **Líneas**: columna `pallets`  
- **Recepciones**: columna `Cant Pallet`
""")