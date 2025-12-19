import streamlit as st
import pandas as pd
import time
import plotly.express as px
import io
import sqlite3
import os
# IMPORTANTE: Aquí conectamos con tu archivo modular de IA
from prediction_engine import predecir_prioridad

# Configuración básica
st.set_page_config(page_title="Muni Yau", layout="wide")

# ==========================================
# CONFIGURACIÓN DE BASE DE DATOS
# ==========================================
DB_NAME = 'muni_tramites.db'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS tramites
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  fecha TEXT, 
                  ciudadano TEXT, 
                  tipo TEXT, 
                  prioridad TEXT, 
                  estado TEXT,
                  docs_completos INTEGER)''')
    conn.commit()
    conn.close()

def guardar_tramite_db(fecha, ciudadano, tipo, prioridad, estado, docs):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO tramites (fecha, ciudadano, tipo, prioridad, estado, docs_completos) VALUES (?, ?, ?, ?, ?, ?)",
              (fecha, ciudadano, tipo, prioridad, estado, docs))
    conn.commit()
    conn.close()

def cargar_tramites_db():
    if not os.path.exists(DB_NAME):
        init_db()
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM tramites", conn)
    conn.close()
    return df

def actualizar_estado_db(df_editado):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM tramites")
    df_editado.to_sql('tramites', conn, if_exists='append', index=False)
    conn.commit()
    conn.close()

# Inicializamos la BD al arrancar
init_db()

# ==========================================
# INTERFAZ GRÁFICA (UI)
# ==========================================
st.sidebar.title("Muni Yau")
st.sidebar.info("Sistema Modular v2.0")
menu = st.sidebar.radio("Menu Principal", ["Dashboard", "Nuevo Tramite", "Historial y Gestion"])

# --- VISTA 1: DASHBOARD ---
if menu == "Dashboard":
    st.title("Gestion Municipal - Dashboard")
    df = cargar_tramites_db()
    
    if df.empty:
        st.info("No hay tramites registrados aun.")
    else:
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Tramites", len(df))
        c2.metric("Observados", len(df[df['prioridad'] == 'OBSERVADO']), delta_color="inverse") 
        c3.metric("Prioridad Alta", len(df[df['prioridad'] == 'ALTA']))
        
        st.plotly_chart(px.pie(df, names='prioridad', title="Carga de Trabajo por Prioridad", 
                               color='prioridad',
                               color_discrete_map={'ALTA':'red', 'NORMAL':'blue', 'OBSERVADO':'orange'}), 
                               use_container_width=True)

# --- VISTA 2: PREDICCIÓN Y REGISTRO ---
elif menu == "Nuevo Tramite":
    st.title("Ventanilla Inteligente (AI Powered)")
    
    with st.form("form_tramite"):
        c1, c2 = st.columns(2)
        
        # Inputs básicos
        nombre = c1.text_input("Nombre del Ciudadano")
        tipo = c2.selectbox("Tipo de Tramite", ["Licencia_Construccion", "Licencia_Funcionamiento", "Registro_Civil"])
        
        # Inputs específicos para que el modelo Random Forest pueda predecir
        c3, c4 = st.columns(2)
        dias = c3.slider("Dias de Espera Acumulados", 0, 60, 0)
        obs = c4.number_input("Observaciones Previas", 0, 10, 0)
        
        docs = st.radio("Documentacion Completa", [1, 0], format_func=lambda x: "Si" if x==1 else "No")
        
        if st.form_submit_button("Analizar con IA y Registrar"):
            if not nombre:
                st.warning("Debe ingresar el nombre del ciudadano.")
            else:
                with st.spinner("Consultando motor de prediccion..."):
                    time.sleep(0.5)
                    
                    # === LLAMADA AL SCRIPT EXTERNO ===
                    # Esto usa prediction_engine.py -> train_model.py -> data_simulator.py
                    prio, conf = predecir_prioridad(tipo, docs, dias, obs)
                    
                    # Feedback Visual
                    if prio == "OBSERVADO":
                        st.error(f"ESTADO: {prio} (Certeza: {conf:.0%})")
                    elif prio == "ALTA":
                        st.success(f"PRIORIDAD: {prio} (Via Rapida) - Certeza: {conf:.0%}")
                        st.warning(f"ALERTA DE SISTEMA: Notificación enviada a {nombre}")
                    else:
                        st.info(f"PRIORIDAD: {prio} (Certeza: {conf:.0%})")
                        st.success(f"Tramite registrado correctamente.")

                    # Guardar en base de datos
                    guardar_tramite_db(
                        time.strftime("%Y-%m-%d"), 
                        nombre, 
                        tipo, 
                        prio, 
                        'Pendiente' if prio != "OBSERVADO" else "Detenido", 
                        docs
                    )

# --- VISTA 3: HISTORIAL Y EDICIÓN ---
elif menu == "Historial y Gestion":
    st.title("Gestion de Estados")
    df = cargar_tramites_db()
    
    if not df.empty:
        # Tabla editable
        edited_df = st.data_editor(
            df,
            column_config={
                "id": st.column_config.NumberColumn("ID", disabled=True, format="%d"),
                "estado": st.column_config.SelectboxColumn("Estado", options=["Pendiente", "Finalizado"], required=True),
                "prioridad": st.column_config.TextColumn("Prioridad", disabled=True),
            },
            disabled=["id", "fecha", "ciudadano", "tipo", "prioridad"],
            hide_index=True,
            use_container_width=True
        )
        
        # Guardar cambios
        if st.button("Guardar Cambios"):
            actualizar_estado_db(edited_df)
            st.success("Guardado en Base de Datos.")
            time.sleep(1)
            st.rerun()
            
        # Exportar a Excel
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            edited_df.to_excel(writer, index=False)
        st.download_button("Descargar Excel", buffer.getvalue(), "reporte.xlsx")
    else:
        st.info("Sin datos.")
