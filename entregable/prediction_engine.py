import pandas as pd
import joblib
import os
from train_model import entrenar_modelo

MODEL_FILE = 'priority_model.pkl'
COLUMNS_FILE = 'model_columns.pkl'

def cargar_modelo():
    """Carga el modelo. Si no existe, manda a entrenarlo primero."""
    if not os.path.exists(MODEL_FILE) or not os.path.exists(COLUMNS_FILE):
        entrenar_modelo()
        
    model = joblib.load(MODEL_FILE)
    columns = joblib.load(COLUMNS_FILE)
    return model, columns

def predecir_prioridad(tipo, docs, dias, obs):
    """Función principal que usa la App Web."""
    
    # 1. Cargar cerebro
    model, model_columns = cargar_modelo()
    
    # 2. Preparar el dato nuevo
    input_data = pd.DataFrame([{
        'Tipo': tipo,
        'Docs_Completos': docs,
        'Dias_Espera': dias,
        'Observaciones': obs
    }])
    
    # 3. Preprocesar (One-Hot)
    input_encoded = pd.get_dummies(input_data, columns=['Tipo'])
    
    # 4. Alinear columnas (Rellenar con 0 las que falten)
    input_final = input_encoded.reindex(columns=model_columns, fill_value=0)
    
    # 5. Predecir
    prediccion = model.predict(input_final)[0]
    probabilidad = model.predict_proba(input_final)[0][1]
    
    # 6. Resultado legible
    if docs == 0:
        return "OBSERVADO", 0.99
    elif prediccion == 1:
        return "ALTA", probabilidad
    else:
        return "NORMAL", (1 - probabilidad)
