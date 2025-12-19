import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from data_simulator import generar_datos_historicos
import os

MODEL_FILE = 'priority_model.pkl'
COLUMNS_FILE = 'model_columns.pkl'
DATA_FILE = 'municipalidad_data.csv'

def entrenar_modelo():
    # 1. Verificar si existen datos, si no, crearlos
    if not os.path.exists(DATA_FILE):
        generar_datos_historicos()
        
    print("Iniciando entrenamiento del modelo...")
    df = pd.read_csv(DATA_FILE)
    
    # 2. Preprocesamiento (One-Hot Encoding)
    df_encoded = pd.get_dummies(df, columns=['Tipo'])
    
    X = df_encoded.drop('Prioridad_Alta', axis=1)
    y = df_encoded['Prioridad_Alta']
    
    # 3. Guardar las columnas usadas (importante para predecir después)
    model_columns = X.columns.tolist()
    
    # 4. Entrenar Random Forest
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X, y)
    
    # 5. Guardar el modelo entrenado y las columnas
    joblib.dump(clf, MODEL_FILE)
    joblib.dump(model_columns, COLUMNS_FILE)
    
    print(f"Modelo guardado en '{MODEL_FILE}'")
    print(f"Columnas guardadas en '{COLUMNS_FILE}'")

if __name__ == "__main__":
    entrenar_modelo()
