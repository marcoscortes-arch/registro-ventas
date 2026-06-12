import streamlit as st
import requests
import json
from datetime import datetime

# Configuración para pantalla móvil
st.set_page_config(page_title="Captura de Ventas", page_icon="📱", layout="centered")

# Enlaces de conexión
URL_MI_WEB_APP = "https://script.google.com/macros/s/AKfycbwbZWOK1Q3j54dEoefLHxwdz0N_1jtGoYjdXhaHaKjB9sZd0O5wHCNXFB1Zoy8QhVwkwQ/exec"
URL_GOOGLE_SHEETS = "https://docs.google.com/spreadsheets/d/1Cw4GQXMYOtsSPtlvPZXz48FP35Bv3E3ec6_4BeKY1Ik/edit?usp=sharing"

st.title("📱 Captura de Ventas")
st.write("Registra tus ventas de ropa de forma rápida. Los datos se sincronizan con Google Sheets.")

# --- FORMULARIO DE CAPTURA ---
with st.form("formulario_ventas"):
    col1, col2 = st.columns(2)
    
    with col1:
        cliente = st.text_input("👤 Cliente")
        tipo_producto = st.selectbox("👗 Tipo de Producto", ["Pijama", "Vestido", "Conjunto", "Interior"])
        talla = st.text_input("📏 Talla")
        piezas = st.number_input("📦 Piezas", min_value=1, value=1, step=1)
        genero = st.selectbox("🧒 Género", ["Niño", "Niña", "Adulto Mujer", "Adulto Hombre"])
        
        if tipo_producto == "Pijama":
            detalle_prenda = st.text_input("🩲 Detalle de Interior", placeholder="Ej: Short, Pantalón")
        elif tipo_producto == "Interior":
            detalle_prenda = st.text_input("🩲 Tipo de Prenda Interior", placeholder="Ej: Bóxer, Top, Cachetero")
        else:
            detalle_prenda = st.text_input("📝 Nota / Detalle", value=tipo_producto)
            
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
        st.error("⚠️ Por favor, rellena los campos obligatorios: Cliente y Talla.")
    else:
        fecha_str = fecha.strftime("%d/%m/%Y")
        valor_final_detalle = detalle_prenda.strip() if detalle_prenda.strip() != "" else tipo_producto

        # Enviamos las fórmulas de Excel en lugar de números fijos.
        # De esta forma, si corriges las piezas en el Sheet, el total cambia solo.
        formula_costo_total = "=C" + "ROW_PLACEHOLDER" + "*J" + "ROW_PLACEHOLDER"
        formula_venta_total = "=C" + "ROW_PLACEHOLDER" + "*I" + "ROW_PLACEHOLDER"

        datos_venta = {
            "Cliente": cliente,
            "Talla": talla,
            "Piezas": piezas,
            "Genero": genero,
            "Interior": valor_final_detalle,
            "Fecha": fecha_str,
            "Lugar": lugar,
            "TipoPedido": tipo_pedido,
            "PrecioUnitario": precio_unitario,
            "CostoCompra": costo_compra,
            "CostoTotal": "CALCULATE_FORMULA_COSTO", # El Script de Google lo convertirá en la fórmula correcta
            "VentaTotal": "CALCULATE_FORMULA_VENTA"   # El Script de Google lo convertirá en la fórmula correcta
        }
        
        try:
            respuesta = requests.post(URL_MI_WEB_APP, data=json.dumps(datos_venta), headers={"Content-Type": "application/json"})
            if respuesta.status_code == 200:
                st.success(f"✅ ¡Sincronizado correctamente! Total inicial estimado: ${piezas * precio_unitario:.2f}")
                st.balloons()
                st.rerun()
            else:
                st.error("⚠️ La nube no pudo procesar el registro.")
        except Exception as e:
            st.error("⚠️ Error de conexión.")

st.markdown("---")
st.subheader("🔗 Enlace Directo")
st.link_button("📊 Abrir mi Hoja de Google Sheets", URL_GOOGLE_SHEETS)

