import streamlit as st
from config.config import initialize_session_state
from data.data_loader import load_data
from data.layout_loader import process_layout_data
from components.ui_components import (
    render_sidebar,
    render_general_analysis,
    render_format_analysis,
    render_time_analysis,
    render_abc_analysis
)

from components.layout_components import (
    render_layout_map,
    render_capacity_controls,
    render_layout_metrics
)

from components.layout_planner import render_product_location_planner


def main():
    st.set_page_config(page_title="Análisis de Pallets", layout="wide")
    st.title("📦 Análisis de Movimiento de Pallets")

    # Inicializar estado
    initialize_session_state()

    # Renderizar sidebar y obtener archivos cargados
    uploaded_files = render_sidebar()

    if any(uploaded_files.values()):
        # Cargar datos
        data = load_data(uploaded_files)
        
        # Crear tabs principales
        tab1, tab2, tab3, tab4, tab5  = st.tabs([
            "Análisis General",
            "Análisis por Formato",
            "Análisis por Período",
            "Análisis ABC",
            "Mapa del Centro",

        ])

        # Renderizar cada sección
        with tab1:
            render_general_analysis(data)
        
        with tab2:
            render_format_analysis(data)
        
        with tab3:
            render_time_analysis(data)
        
        with tab4:
            render_abc_analysis(data)
        
        with tab5:
            st.header("Mapa del Centro")
            
            layout_file = st.file_uploader(
                "Cargar archivo de disposición del centro",
                type=['xlsx'],
                key="layout_planner_uploader"  # Clave única para este uploader
            )
            render_product_location_planner(data, layout_file)

    else:
        st.info("👈 Por favor, carga los archivos CSV en el panel lateral para comenzar el análisis.")

if __name__ == "__main__":
    main()