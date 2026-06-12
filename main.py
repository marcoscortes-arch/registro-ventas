import streamlit as st
import pandas as pd
import requests
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# Configuración de la página para que se adapte perfectamente al celular
st.set_page_config(page_title="Captura de Ventas", page_icon="📱", layout="centered")

# URL exacta de tu documento de Google Sheets para la conexión directa
URL_GOOGLE_SHEETS = "https://docs.google.com/spreadsheets/d/1Cw4GQXMYOtsSPtlvPZXz48FP35Bv3E3ec6_4BeKY1Ik/edit?usp=sharing"

# 1. Creamos la conexión base limpia sin depender del panel de Secrets
conn = st.connection("gsheets", type=GSheetsConnection)

# 2. Leemos la nube pasándole la URL directamente a la lectura
try:
    df_sheets = conn.read(spreadsheet=URL_GOOGLE_SHEETS, worksheet="Hoja 1", ttl=0)
except Exception:
    df_sheets = pd.DataFrame()

# Archivo local de respaldo por si acaso
archivo_respaldo = "Registro_Ventas_Resp.xlsx"

st.title("📱 Captura de Ventas")
st.write("Registra tus ventas de forma rápida. Los datos se sincronizan con Google Sheets.")

# --- FORMULARIO DE CAPTURA ---
with st.form("formulario_ventas"):
    col1, col2 = st.columns(2)
    
    with col1:
        cliente = st.text_input("👤 Cliente")
        talla = st.text_input("📏 Talla")
        piezas = st.number_input("📦 Piezas", min_value=1, value=1, step=1)
        genero = st.selectbox("🧒 Género", ["Niño", "Niña"])
        interior = st.text_input("🩲 Interior")
        fecha = st.date_input("📅 Fecha de venta", datetime.now())

    with col2:
        lugar = st.text_input("📍 Lugar de envío")
        tipo_pedido = st.selectbox("🚚 Tipo de pedido", [
            "Servientrega", 
            "Contra entrega Dopri", 
            "Envio Cooperativa", 
            "Retiro en Santo Domingo"
        ])
        precio_unitario = st.number_input("💵 Precio Unitario ($)", min_value=0.0, value=0.0, step=0.5)
        costo_compra = st.number_input("📉 Costo de compra ($)", min_value=0.0, value=0.0, step=0.5)

    # Botón de envío
    boton_guardar = st.form_submit_button("💾 Guardar Registro de Ventas")

# --- LÓGICA DE GUARDADO ---
if boton_guardar:
    if cliente.strip() == "" or talla.strip() == "":
        st.error("⚠️ Por favor, rellena los campos obligatorios (Cliente y Talla).")
    else:
        # Cálculos matemáticos automáticos
        costo_total = piezas * costo_compra
        venta_total = piezas * precio_unitario
        fecha_str = fecha.strftime("%d/%m/%Y")
        
        nueva_fila = {
            "Cliente": cliente,
            "Talla": talla,
            "Piezas": piezas,
            "Genero": genero,
            "Interior": interior,
            "Fecha de venta": fecha_str,
            "Lugar de envío": lugar,
            "Tipo de pedido": tipo_pedido,
            "Precio Unitario": precio_unitario,
            "Costo de compra": costo_compra,
            "Costo total": costo_total,
            "Venta total": venta_total
        }
        
        # --- 1. GUARDADO EN GOOGLE SHEETS ---
        try:
            nuevo_registro_df = pd.DataFrame([nueva_fila])
            # Combinamos la información que ya existe con la nueva fila
            df_actualizado_sheets = pd.concat([df_sheets, nuevo_registro_df], ignore_index=True)
            # Actualizamos la nube apuntando directo a la URL
            conn.update(spreadsheet=URL_GOOGLE_SHEETS, worksheet="Hoja 1", data=df_actualizado_sheets)
            st.success("✅ ¡Sincronizado con Google Sheets exitosamente!")
        except Exception as e:
            st.error(f"❌ Error al subir a Google Sheets: {e}")
        
        # --- 2. RESPALDO EXCEL LOCAL ---
        try:
            df_local = pd.read_excel(archivo_respaldo)
            df_actualizado_local = pd.concat([df_local, pd.DataFrame([nueva_fila])], ignore_index=True)
        except Exception:
            df_actualizado_local = pd.DataFrame([nueva_fila])
        
        df_actualizado_local.to_excel(archivo_respaldo, index=False)
        
        st.success(f"💾 ¡Venta guardada localmente! Venta Total: ${venta_total:.2f} | Costo Total: ${costo_total:.2f}")
        
        st.rerun()

# --- SECCIÓN DE ENLACES ---
st.markdown("---")
st.subheader("🔗 Enlace Directo")
st.link_button("📊 Abrir mi Hoja de Google Sheets", URL_GOOGLE_SHEETS)
