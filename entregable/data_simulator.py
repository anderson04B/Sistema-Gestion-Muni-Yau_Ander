import pandas as pd
import numpy as np
import os

def generar_datos_historicos(n_samples=1000):
    """Genera un CSV con datos simulados de trámites."""
    print("Generando datos históricos simulados...")
    
    data = {
        'Tipo': np.random.choice(['Licencia_Construccion', 'Licencia_Funcionamiento', 'Registro_Civil'], n_samples),
        'Docs_Completos': np.random.choice([1, 0], n_samples, p=[0.7, 0.3]),
        'Dias_Espera': np.random.randint(1, 60, n_samples),
        'Observaciones': np.random.randint(0, 5, n_samples)
    }
    df = pd.DataFrame(data)
    
    # Reglas lógicas para el target (Lo que la IA debe aprender)
    # CONDICIÓN: Si faltan documentos O es Construcción con demora -> ALTA
    condiciones = (
        (df['Docs_Completos'] == 0) | 
        ((df['Tipo'] == 'Licencia_Construccion') & (df['Dias_Espera'] > 15))
    )
    
    # Asignamos etiquetas de texto explícitas: "ALTA" o "NORMAL"
    df['Prioridad'] = np.where(condiciones, 'ALTA', 'NORMAL')
    
    # Guardar archivo
    df.to_csv('municipalidad_data.csv', index=False)
    print("Archivo 'municipalidad_data.csv' creado exitosamente con etiquetas.")

if __name__ == "__main__":
    generar_datos_historicos()
