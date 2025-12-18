# Archivo: prediction_engine.py

import pandas as pd
import joblib
import numpy as np

# --- FASE 1: Cargar Modelo y Estructura ---
try:
    model = joblib.load('priority_model.pkl')
    feature_columns = joblib.load('model_features.pkl')
    print("Modelo de Priorización cargado correctamente.")
except FileNotFoundError:
    print("Error: Archivos del modelo ('priority_model.pkl' o 'model_features.pkl') no encontrados. Ejecute 'train_model.py' primero.")
    exit()

# --- FASE 2: Función de Preprocesamiento en Vivo ---
def preprocess_new_data(new_data, columns):
    """
    Asegura que el nuevo dato tenga el mismo formato (mismas columnas) que el usado en el entrenamiento.
    """
    # 1. Crear DataFrame del nuevo dato
    new_df = pd.DataFrame(new_data)
    
    # 2. Aplicar One-Hot Encoding al Tipo_Tramite
    new_df_encoded = pd.get_dummies(new_df, columns=['Tipo_Tramite'], prefix='Tramite', drop_first=True)

    # 3. Alinear las columnas (añadir columnas faltantes con valor 0)
    final_df = pd.DataFrame(0, index=new_df_encoded.index, columns=columns)
    
    # Rellenar con los valores codificados del nuevo trámite
    for col in new_df_encoded.columns:
        if col in final_df.columns:
            final_df[col] = new_df_encoded[col]

    return final_df

# --- FASE 3: Motor de Predicción y Alerta ---
def predict_and_alert(new_tramite_data):
    """
    Recibe un nuevo trámite, predice su prioridad y simula la alerta.
    """
    # Preprocesar el dato para el modelo
    processed_input = preprocess_new_data(new_tramite_data, feature_columns)
    
    # Realizar la Predicción
    prediccion_prioridad = model.predict(processed_input)[0]

    # Activar la lógica del Sistema de Alertas
    print("\n==============================================")
    print(f"Trámite Ingresado: {new_tramite_data['Tipo_Tramite'][0]}")
    
    if prediccion_prioridad == 1:
        resultado = "ALTA"
        print(f"[ ML] Prioridad Predicha: {resultado}. **Activando Alerta Ciudadana**.")
        # Lógica para enviar SMS/Email (simulada)
    else:
        resultado = "NORMAL"
        print(f"[ ML] Prioridad Predicha: {resultado}. En Cola Estándar.")
    
    print("==============================================")
    return resultado

# --- FASE 4: Casos de Prueba ---
if __name__ == '__main__':
    # Caso 1: Trámite con alta probabilidad de ser crítico (Licencia de Construcción, incompleto)
    critico_data = {
        'Tipo_Tramite': ['Licencia_Construccion'], 
        'Documentacion_Completa': [0],              
        'Dias_Espera_Historico': [40], # Alto historial de espera
        'Observaciones_Previas': [3]
    }
    predict_and_alert(critico_data)

    # Caso 2: Trámite de baja complejidad (Registro Civil, completo)
    normal_data = {
        'Tipo_Tramite': ['Registro_Civil'], 
        'Documentacion_Completa': [1],              
        'Dias_Espera_Historico': [5],
        'Observaciones_Previas': [0]
    }
    predict_and_alert(normal_data)