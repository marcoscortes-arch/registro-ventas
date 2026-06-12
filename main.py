import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime

# Configuración para pantalla móvil
st.set_page_config(page_title="Captura de Ventas", page_icon="📱", layout="centered")

# Enlace mágico directo a tu Google Apps Script
URL_MI_WEB_APP = "https://script.google.com/macros/s/AKfycbwbZWOK1Q3j54dEoefLHxwdz0N_1jtGoYjdXhaHaKjB9sZd0O5wHCNXFB1Zoy8QhVwkwQ/exec"

# URL estética para el botón de acceso rápido abajo
URL_GOOGLE_SHEETS = "https://docs.google.com/spreadsheets/d/1Cw4GQXMYOtsSPtlvPZXz48FP35Bv3E3ec6_4BeKY1Ik/edit?usp=sharing"
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

    boton_guardar = st.form_submit_button("💾 Guardar Registro de Ventas")

# --- LÓGICA DE GUARDADO ---
if boton_guardar:
    if cliente.strip() == "" or talla.strip() == "":
        st.error("⚠️ Por favor, rellena los campos obligatorios (Cliente y Talla).")
    else:
        costo_total = piezas * costo_compra
        venta_total = piezas * precio_unitario
        fecha_str = fecha.strftime("%d/%m/%Y")
        
        # Estructura limpia de datos para enviar a Google Sheets
        datos_venta = {
            "Cliente": cliente,
            "Talla": talla,
            "Piezas": piezas,
            "Genero": genero,
            "Interior": interior,
            "Fecha": fecha_str,
            "Lugar": lugar,
            "TipoPedido": tipo_pedido,
            "PrecioUnitario": precio_unitario,
            "CostoCompra": costo_compra,
            "CostoTotal": costo_total,
            "VentaTotal": venta_total
        }
        
        # --- 1. ENVÍO EN TIEMPO REAL A GOOGLE SHEETS ---
        try:
            respuesta = requests.post(URL_MI_WEB_APP, data=json.dumps(datos_venta), headers={"Content-Type": "application/json"})
            if respuesta.status_code == 200 and respuesta.json().get("status") == "success":
                st.success("✅ ¡Sincronizado con Google Sheets exitosamente!")
            else:
                st.warning("⚠️ Guardado localmente, pero la nube no procesó el registro.")
        except Exception as e:
            st.error("⚠️ Guardado localmente. Error de conexión con la nube.")
        
        # --- 2. RESPALDO EXCEL LOCAL ---
        try:
            df_local = pd.read_excel(archivo_respaldo)
            df_actualizado_local = pd.concat([df_local, pd.DataFrame([datos_venta])], ignore_index=True)
        except Exception:
            df_actualizado_local = pd.DataFrame([datos_venta])
        
        df_actualizado_local.to_excel(archivo_respaldo, index=False)
        st.success(f"💾 ¡Venta guardada en respaldo local! Total: ${venta_total:.2f}")
        
        st.rerun()

st.markdown("---")
st.subheader("🔗 Enlace Directo")
st.link_button("📊 Abrir mi Hoja de Google Sheets", URL_GOOGLE_SHEETS)
