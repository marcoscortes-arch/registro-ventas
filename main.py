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
        # Agregamos 'Interior' a la lista principal de productos
        tipo_producto = st.selectbox("👗 Tipo de Producto", ["Pijama", "Vestido", "Conjunto", "Interior"])
        talla = st.text_input("📏 Talla")
        piezas = st.number_input("📦 Piezas", min_value=1, value=1, step=1)
        genero = st.selectbox("🧒 Género", ["Niño", "Niña", "Adulto Mujer", "Adulto Hombre"])
        
        # El campo de detalle se adapta de forma inteligente según el producto elegido
        if tipo_producto == "Pijama":
            detalle_prenda = st.text_input("🩲 Detalle de Interior", placeholder="Ej: Short, Pantalón")
        elif tipo_producto == "Interior":
            detalle_prenda = st.text_input("🩲 Tipo de Prenda Interior", placeholder="Ej: Bóxer, Top, Cachetero")
        else:
            # Para Vestidos o Conjuntos se llena solo de forma automática
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
    # Candado estricto: Cliente y Talla son obligatorios
    if cliente.strip() == "" or talla.strip() == "":
        st.error("⚠️ Por favor, rellena los campos obligatorios: Cliente y Talla.")
    else:
        costo_total = piezas * costo_compra
        venta_total = piezas * precio_unitario
        fecha_str = fecha.strftime("%d/%m/%Y")
        
        # Si el detalle quedó vacío, le asignamos el tipo de producto por defecto
        valor_final_detalle = detalle_prenda.strip() if detalle_prenda.strip() != "" else tipo_producto

        # Estructura mapeada idéntica a tu Google Sheets
        datos_venta = {
            "Cliente": cliente,
            "Talla": talla,
            "Piezas": piezas,
            "Genero": genero,
            "Interior": valor_final_detalle, # Manda la información directo a la columna 'Interior'
            "Fecha": fecha_str,
            "Lugar": lugar,
            "TipoPedido": tipo_pedido,
            "PrecioUnitario": precio_unitario,
            "CostoCompra": costo_compra,
            "CostoTotal": costo_total,
            "VentaTotal": venta_total
        }
        
        # Envío directo a Google Sheets sin intermediarios
        try:
            respuesta = requests.post(URL_MI_WEB_APP, data=json.dumps(datos_venta), headers={"Content-Type": "application/json"})
            if respuesta.status_code == 200:
                st.success(f"✅ ¡Sincronizado con Google Sheets exitosamente! Total: ${venta_total:.2f}")
                st.balloons()
                st.rerun()
            else:
                st.error("⚠️ La nube no pudo procesar el registro correctamente.")
        except Exception as e:
            st.error("⚠️ Error de conexión al intentar enviar los datos.")

st.markdown("---")
st.subheader("🔗 Enlace Directo")
st.link_button("📊 Abrir mi Hoja de Google Sheets", URL_GOOGLE_SHEETS)
