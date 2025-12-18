# Archivo: data_simulator.py

import pandas as pd
import numpy as np

def generate_simulated_data(n_samples=1000):
    """
    Genera un DataFrame de datos simulados para el entrenamiento del modelo.
    Se utiliza una lógica básica para crear la variable objetivo 'Prioridad_Alta'
    basada en el tipo de trámite y la documentación incompleta.
    """
    data = {
        # Característica 1: Tipo de Trámite (variable categórica clave)
        'Tipo_Tramite': np.random.choice(['Licencia_Construccion', 'Licencia_Funcionamiento', 'Permiso_Ambiental', 'Registro_Civil'], n_samples),
        # Característica 2: Documentación completa (1=Sí, 0=No; influye en la prioridad)
        'Documentacion_Completa': np.random.choice([1, 0], n_samples, p=[0.8, 0.2]),
        # Característica 3: Días de Espera Histórico (para establecer patrones)
        'Dias_Espera_Historico': np.random.randint(5, 45, n_samples),
        # Característica 4: Observaciones Previas (indicador de complejidad)
        'Observaciones_Previas': np.random.randint(0, 5, n_samples),
        
        # VARIABLE OBJETIVO (TARGET): 1 para prioridad 'Alta' (crítico), 0 para 'Normal'
        'Prioridad_Alta': np.where(
            # Regla de simulación: Las licencias de construcción con documentación incompleta
            # y un historial de espera alto tienen mayor probabilidad de ser 'Alta'
            (np.random.rand(n_samples) < 0.15) | 
            (
                (np.array(['Licencia_Construccion'] * n_samples) == np.array(np.random.choice(['Licencia_Construccion', 'Otros'], n_samples))) & 
                (np.array(np.random.choice([1, 0], n_samples)) == 0) & 
                (np.random.rand(n_samples) < 0.7)
            ), 
            1, 0
        )
    }
    df = pd.DataFrame(data)
    print(f"Dataset simulado de {n_samples} registros creado.")
    return df

if __name__ == '__main__':
    # Guardar el dataset simulado para que sea usado por el script de entrenamiento
    simulated_df = generate_simulated_data()
    simulated_df.to_csv('municipalidad_data.csv', index=False)