# Archivo: train_model.py

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import f1_score, classification_report
import joblib # Librería para guardar el modelo

# --- FASE 1: Preparación de Datos ---
def preprocess_data(df):
    """
    Realiza el One-Hot Encoding en las variables categóricas.
    """
    # Convertir 'Tipo_Tramite' a variables dummy
    df_encoded = pd.get_dummies(df, columns=['Tipo_Tramite'], prefix='Tramite', drop_first=True)
    return df_encoded

# --- FASE 2: Entrenamiento y Evaluación ---
def train_and_evaluate_model(df_encoded):
    
    # Seleccionar Features (X) y Target (y)
    X = df_encoded.drop('Prioridad_Alta', axis=1)
    y = df_encoded['Prioridad_Alta']

    # Guardar las columnas de entrenamiento para asegurar la consistencia en la predicción
    column_names = X.columns.tolist()

    # Dividir datos en conjuntos de entrenamiento y prueba
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

    # 1. Inicializar y Entrenar el Modelo
    # Random Forest es ideal para la clasificación de prioridad
    model = RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced')
    model.fit(X_train, y_train)

    print("Modelo Random Forest entrenado.")

    # 2. Evaluación del Modelo (Usando F1-Score)
    y_pred = model.predict(X_test)
    f1 = f1_score(y_test, y_pred)

    print(f"\n--- Resultados de la Evaluación ---")
    print(f"F1-Score (Métrica clave de efectividad): {f1:.4f}")
    print("Informe de Clasificación:")
    print(classification_report(y_test, y_pred, target_names=['Normal', 'Alta']))

    return model, column_names

# --- FASE 3: Ejecución Principal ---
if __name__ == '__main__':
    try:
        # Cargar los datos generados por data_simulator.py
        data_df = pd.read_csv('municipalidad_data.csv')
    except FileNotFoundError:
        print("Error: El archivo 'municipalidad_data.csv' no se encuentra. Ejecute 'data_simulator.py' primero.")
        exit()

    processed_df = preprocess_data(data_df)
    trained_model, feature_columns = train_and_evaluate_model(processed_df)

    # Guardar el modelo entrenado y la lista de columnas para usarlos en el motor de predicción
    joblib.dump(trained_model, 'priority_model.pkl')
    joblib.dump(feature_columns, 'model_features.pkl')
    print("\nModelo y lista de features guardados como 'priority_model.pkl' y 'model_features.pkl'.")