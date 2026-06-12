import streamlit as st
import requests
import json
from datetime import datetime

# Configuración para pantalla móvil
st.set_page_config(page_title="Captura de Ventas", page_icon="📱", layout="centered")

# Enlace de tu Google Apps Script (Tu puente directo)
URL_MI_WEB_APP = "https://script.google.com/macros/s/AKfycbwbZWOK1Q3j54dEoefLHxwdz0N_1jtGoYjdXhaHaKjB9sZd0O5wHCNXFB1Zoy8QhVwkwQ/exec"
URL_GOOGLE_SHEETS = "https://docs.google.com/spreadsheets/d/1Cw4GQXMYOtsSPtlvPZXz48FP35Bv3E3ec6_4BeKY1Ik/edit?usp=sharing"

st.title("📱 Captura de Ventas")
st.write("Registra tus ventas de ropa de forma rápida. Los datos se sincronizan con Google Sheets.")

# --- FORMULARIO DE CAPTURA ---
with st.form("formulario_ventas"):
    col1, col2 = st.columns(2)
    
    with col1:
        cliente = st.text_input("👤 Cliente")
        tipo_producto = st.selectbox("👗 Tipo de Producto", ["Pijama", "Vestido", "Conjunto"])
        talla = st.text_input("📏 Talla")
        piezas = st.number_input("📦 Piezas", min_value=1, value=1, step=1)
        genero = st.selectbox("🧒 Género", ["Niño", "Niña", "Adulto Mujer", "Adulto Hombre"])
        
        # El campo Interior SOLO se muestra si el producto es una Pijama
        if tipo_producto == "Pijama":
            interior = st.text_input("🩲 Interior")
        else:
            interior = "" # Se envía vacío si es vestido o conjunto
            
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
    # Candado estricto: Cliente y Talla no pueden estar vacíos
    if cliente.strip() == "" or talla.strip() == "":
        st.error("⚠️ Por favor, rellena los campos obligatorios: Cliente y Talla.")
    else:
        costo_total = piezas * costo_compra
        venta_total = piezas * precio_unitario
        fecha_str = fecha.strftime("%d/%m/%Y")
        
        # Combinamos inteligentemente el campo Interior para vestidos/conjuntos
        detalle_interior = interior if tipo_producto == "Pijama" else tipo_producto

        datos_venta = {
            "Cliente": cliente,
            "Talla": talla,
            "Piezas": piezas,
            "Genero": genero,
            "Interior": detalle_interior,
            "Fecha": fecha_str,
            "Lugar": lugar,
            "TipoPedido": tipo_pedido,
            "PrecioUnitario": precio_unitario,
            "CostoCompra": costo_compra,
            "CostoTotal": costo_total,
            "VentaTotal": venta_total
        }
        
        # Envío directo a Google Sheets
        try:
            requests.post(URL_MI_WEB_APP, data=json.dumps(datos_venta), headers={"Content-Type": "application/json"})
            st.success(f"✅ ¡Sincronizado con Google Sheets exitosamente! Total: ${venta_total:.2f}")
            st.balloons()
            st.rerun()
        except Exception as e:
            st.error("⚠️ Error de conexión al intentar enviar los datos.")

st.markdown("---")
st.subheader("🔗 Enlace Directo")
st.link_button("📊 Abrir mi Hoja de Google Sheets", URL_GOOGLE_SHEETS)
