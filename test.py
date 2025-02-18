import pandas as pd

# Leer el CSV con las opciones correctas
df = pd.read_csv('Recepciones 2024.csv',
                 sep=';',           # Separador punto y coma
                 encoding='utf-8')  # Codificación para caracteres especiales

# Convertir la columna a float para manejar decimales correctamente
df['cant_pallet'] = pd.to_numeric(df['Cant Pallet'], errors='coerce')

# Sumar la columna
suma = df['cant_pallet'].sum()

print(f"La suma total de cant_pallet es: {suma}")

# Verificaciones adicionales
print("\nVerificación de los datos:")
print(f"Número de filas: {len(df)}")
print(f"Primeros valores:")
print(df['cant_pallet'].head())