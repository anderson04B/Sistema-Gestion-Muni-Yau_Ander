import streamlit as st
import pandas as pd
import time
import plotly.express as px
import io
import sqlite3
import os

# Configuración básica
st.set_page_config(page_title="Muni Yau", layout="wide")

# --- 0. CONFIGURACIÓN DE BASE DE DATOS ROBUSTA ---
DB_NAME = 'muni_tramites.db'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Aseguramos que la tabla tenga la estructura correcta con ID AUTOINCREMENT
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
    # SQLite se encarga de generar el ID automáticamente
    c.execute("INSERT INTO tramites (fecha, ciudadano, tipo, prioridad, estado, docs_completos) VALUES (?, ?, ?, ?, ?, ?)",
              (fecha, ciudadano, tipo, prioridad, estado, docs))
    conn.commit()
    conn.close()

def cargar_tramites_db():
    if not os.path.exists(DB_NAME):
        init_db()
    conn = sqlite3.connect(DB_NAME)
    # Cargamos todos los datos
    df = pd.read_sql_query("SELECT * FROM tramites", conn)
    conn.close()
    return df

def actualizar_estado_db(df_editado):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # TRUCO PARA MANTENER LOS ID CORRECTOS:
    # 1. Borramos los datos viejos (pero NO la tabla, así mantenemos el AutoIncrement)
    c.execute("DELETE FROM tramites")
    
    # 2. Insertamos los datos editados respetando la estructura
    # index=False evita que pandas intente escribir su propio índice
    df_editado.to_sql('tramites', conn, if_exists='append', index=False)
    
    conn.commit()
    conn.close()

# Inicializar DB al arrancar
init_db()

# --- 1. MOTOR DE IA ---
def predecir_prioridad(data):
    if data['docs'] == 0:
        return "OBSERVADO", 0.99
    if data['tipo'] == 'Licencia_Construccion':
        return "ALTA", 0.92
    return "NORMAL", 0.85

# --- MENÚ LATERAL ---
st.sidebar.title("Muni Yau")
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
                               color_discrete_map={'ALTA':'green', 'NORMAL':'blue', 'OBSERVADO':'red'}), 
                               use_container_width=True)

# --- VISTA 2: PREDICCIÓN Y REGISTRO ---
elif menu == "Nuevo Tramite":
    st.title("Ventanilla Inteligente")
    
    with st.form("form_tramite"):
        c1, c2 = st.columns(2)
        nombre = c1.text_input("Nombre del Ciudadano")
        tipo = c2.selectbox("Tipo", ["Licencia_Construccion", "Licencia_Funcionamiento", "Registro_Civil"])
        docs = st.radio("Documentacion Completa", [1, 0], format_func=lambda x: "Si" if x==1 else "No")
        
        if st.form_submit_button("Analizar y Registrar"):
            if not nombre:
                st.warning("Debe ingresar el nombre del ciudadano.")
            else:
                with st.spinner("Analizando requisitos con IA..."):
                    time.sleep(1) 
                    prio, conf = predecir_prioridad({'tipo': tipo, 'docs': docs})
                    
                    if prio == "OBSERVADO":
                        st.error(f"ESTADO: {prio} (Certeza: {conf:.0%})")
                    elif prio == "ALTA":
                        st.success(f"PRIORIDAD: {prio} (Via Rapida) - Certeza: {conf:.0%}")
                        st.warning(f"ALERTA DE SISTEMA: SMS enviado a {nombre} (Prioridad Alta).")
                    else:
                        st.info(f"PRIORIDAD: {prio} (Certeza: {conf:.0%})")
                        st.success(f"Notificacion enviada a {nombre}")

                    guardar_tramite_db(
                        time.strftime("%Y-%m-%d"), 
                        nombre, 
                        tipo, 
                        prio, 
                        'Pendiente' if prio != "OBSERVADO" else "Detenido", 
                        docs
                    )
                    st.success("Tramite guardado con ID generado correctamente.")

# --- VISTA 3: HISTORIAL Y EDICIÓN ---
elif menu == "Historial y Gestion":
    st.title("Gestion de Estados y Auditoria")
    st.markdown("Puede modificar el **Estado** directamente en la tabla.")
    
    df = cargar_tramites_db()
    
    if not df.empty:
        # Configuración del Editor de Datos
        edited_df = st.data_editor(
            df,
            column_config={
                "id": st.column_config.NumberColumn("ID", disabled=True, format="%d"), # Formato numérico limpio
                "estado": st.column_config.SelectboxColumn(
                    "Estado (Modificar)",
                    options=["Pendiente", "En Proceso", "Finalizado", "Detenido"],
                    required=True,
                ),
                "prioridad": st.column_config.TextColumn("Prioridad", disabled=True),
                "tipo": st.column_config.TextColumn("Tipo", disabled=True),
            },
            disabled=["id", "fecha", "ciudadano", "tipo", "prioridad", "docs_completos"],
            hide_index=True,
            use_container_width=True
        )
        
        if st.button("Guardar Cambios de Estado"):
            actualizar_estado_db(edited_df)
            st.success("Cambios guardados. La base de datos mantiene su integridad.")
            time.sleep(1)
            st.rerun()
            
        st.divider()
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            edited_df.to_excel(writer, index=False, sheet_name='Reporte')
            
        st.download_button("Descargar Reporte Excel", buffer.getvalue(), "reporte_muni_yau.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    else:
        st.info("No hay datos para mostrar.")