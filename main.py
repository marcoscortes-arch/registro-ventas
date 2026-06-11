import streamlit as st
import pandas as pd
import requests
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# 1. Creamos la conexión segura usando los secretos de Streamlit
conn = st.connection("gsheets", type=GSheetsConnection)

# 2. Le indicamos que lea la pestaña llamada Hoja 1
df = conn.read(worksheet="Hoja 1", ttl=0)
# Configuración de la página para que se adapte perfectamente al celular
st.set_page_config(page_title="Captura de Ventas", page_icon="📱", layout="centered")

# URL de tu formulario/hoja para recibir datos
URL_GOOGLE_SHEETS = "https://docs.google.com/spreadsheets/d/1Cw4GQxMYOtsSPtlvPZXz48FP35Bv3E3ec6_4BeKY1Ik/edit?usp=sharing"

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

        # 1. Guardar de respaldo en el Excel local por seguridad
        try:
            df_local = pd.read_excel(archivo_respaldo)
            df_actualizado = pd.concat([df_local, pd.DataFrame([nueva_fila])], ignore_index=True)
        except Exception:
            df_actualizado = pd.DataFrame([nueva_fila])

        df_actualizado.to_excel(archivo_respaldo, index=False)

        # En esta etapa local nos avisa del éxito del guardado del motor
        st.success(f"✅ ¡Venta procesada con éxito! Venta Total: ${venta_total:.2f} | Costo Total: ${costo_total:.2f}")
        st.info("¡El motor local funciona! En el paso final de internet lo vincularemos en tiempo real a tu Google Sheets.")

        st.rerun()

# --- SECCIÓN DE ENLACES ---
st.markdown("---")
st.subheader("🔗 Enlace Directo")
st.link_button("📊 Abrir mi Hoja de Google Sheets", URL_GOOGLE_SHEETS)
