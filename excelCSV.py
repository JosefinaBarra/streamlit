import concurrent.futures
import pandas as pd
import re
from pathlib import Path

def excel_to_looker_csv(excel_file, sheet_name=None, output_file=None):
    try:
        print(f"\nProcesando: {excel_file}")
        
        # Leer Excel manteniendo todas las columnas
        df = pd.read_excel(excel_file, sheet_name=sheet_name, parse_dates=True)
        
        # Guardar los nombres originales de las columnas que necesitamos mapear
        columna_cantidad = df.columns[9]
        columna_formato = df.columns[29]
        columna_fecha = df.columns[4]
        
        # Crear una copia de las columnas necesarias con los nombres requeridos
        df['cant_pallet'] = df[columna_cantidad]
        df['formato'] = df[columna_formato]
        df['fecha_de_entrada'] = df[columna_fecha]
        
        # Convertir tipos de datos solo para las columnas requeridas
        df['cant_pallet'] = pd.to_numeric(df['cant_pallet'], errors='coerce')
        df['fecha_de_entrada'] = pd.to_datetime(df['fecha_de_entrada'], errors='coerce')
        df['formato'] = df['formato'].astype(str)
        
        # Generar nombre de salida si no se especificó
        if not output_file:
            output_file = Path(excel_file).stem + "_looker.csv"
        
        # Guardar CSV con todas las columnas
        df.to_csv(
            output_file,
            index=False,
            date_format='%Y-%m-%d',
            float_format='%.3f',
            encoding='utf-8'
        )
        
        # Imprimir resumen
        print(f"✅ Completado: {excel_file} -> {output_file}")
        print(f"Columnas totales: {len(df.columns)}")
        print(f"Registros procesados: {len(df)}")
        print(f"Cantidad total de pallets: {df['cant_pallet'].sum():.3f}")
        
        # Verificar que las columnas requeridas existen y tienen datos válidos
        registros_validos = df.dropna(subset=['cant_pallet', 'fecha_de_entrada', 'formato'])
        print(f"Registros con datos válidos en columnas requeridas: {len(registros_validos)}")
        
        return output_file
        
    except Exception as e:
        print(f"❌ Error en {excel_file}: {str(e)}")
        raise

def convert_multiple_files(excel_files, max_workers=2):
    """
    Convierte múltiples archivos Excel a CSV en paralelo
    
    Args:
        excel_files: Lista de tuplas (archivo_excel, hoja, archivo_salida)
        max_workers: Número máximo de procesos paralelos
    """
    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
        # Crear lista de futuros
        futures = []
        for excel_file, sheet, output in excel_files:
            future = executor.submit(excel_to_looker_csv, excel_file, sheet, output)
            futures.append(future)
        
        # Esperar resultados
        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result()
                print(f"Archivo procesado: {result}")
            except Exception as e:
                print(f"Error en la conversión: {e}")

# Ejemplo de uso
if __name__ == "__main__":
    # Lista de archivos a convertir: (excel_file, sheet_name, output_file)
    archivos = [
        ("data/Recepciones.xlsx", "Hoja1", "Recepciones.csv")
    ]
    
    # Convertir todos los archivos en paralelo
    convert_multiple_files(archivos, max_workers=2)