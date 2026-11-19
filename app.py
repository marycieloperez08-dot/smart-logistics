import streamlit as st
import pandas as pd
from datetime import datetime
from PIL import Image, ImageDraw
import io
import base64

# --- CONFIGURACIÓN DE PÁGINA Y MODO DARK ---
st.set_page_config(
    page_title="SMART LOGISTICS | Sistema Inteligente de Gestión Logística",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- FUNCIÓN AUXILIAR PARA CONVERTIR IMAGEN A BASE64 ---
def obtener_base64_imagen(ruta_imagen):
    try:
        with open(ruta_imagen, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except:
        return None

logo_base64 = obtener_base64_imagen("logo_smart.png")
if not logo_base64:
    logo_base64 = obtener_base64_imagen("logo_smart.jpg")

fondo_app_base64 = obtener_base64_imagen("fondo_login.jpg")
if not fondo_app_base64:
    fondo_app_base64 = obtener_base64_imagen("fondo_login.png")

TARIFAS_RUTA = {
    "Lima - Agencia Central (Santa Anita)": 3.00,
    "Lima - Sucursal Los Olivos / Cercado": 3.00,
    "Callao - Terminal Portuario / Aeropuerto": 4.00,
    "Ica - Agencia Principal / Nazca": 6.00,
    "Junín - Huancayo / Tarma": 7.50,
    "Áncash - Huaraz / Chimbote": 8.00,
    "La Libertad - Trujillo / Pacasmayo": 9.50,
    "Lambayeque - Chiclayo": 10.00,
    "Arequipa - Agencia Parque Industrial / Cayma": 11.00,
    "Cusco - Agencia Av. de la Cultura / Wanchaq": 12.00,
    "Piura - Agencia Centro / Sullana": 12.50,
    "Amazonas - Chachapoyas": 14.00,
    "Loreto - Iquitos (Carga Fluvial / Aérea)": 16.00
}

AGENCIAS_LISTA = list(TARIFAS_RUTA.keys())

# --- INICIALIZACIÓN DE ESTADOS ---
if 'usuarios_autorizados' not in st.session_state:
    st.session_state.usuarios_autorizados = {
        "admin": {"password": "Choi san", "nombre": "Marycielo Nicole Perez Arroyo", "rol": "Administradora", "dni": "12345678", "turno": "Mañana", "experiencia": "Experimentado"},
        "paula": {"password": "123", "nombre": "Paula Andrea Rojas", "rol": "Operador de Caja", "dni": "74859612", "turno": "Mañana", "experiencia": "Experimentado"},
        "carlos": {"password": "123", "nombre": "Carlos Mendoza", "rol": "Operador de Caja", "dni": "71234567", "turno": "Tarde", "experiencia": "Nuevo"}
    }

if 'usuario_actual' not in st.session_state:
    st.session_state.usuario_actual = None

if 'mostrar_historia' not in st.session_state:
    st.session_state.mostrar_historia = False

if 'navegacion_menu' not in st.session_state:
    st.session_state.navegacion_menu = "Inicio"

if 'reg_form_key' not in st.session_state:
    st.session_state.reg_form_key = 0

if 'mensaje_guardado' not in st.session_state:
    st.session_state.mensaje_guardado = ""

if 'clientes_atendidos_total' not in st.session_state:
    st.session_state.clientes_atendidos_total = 232

if 'cajas_atencion' not in st.session_state:
    st.session_state.cajas_atencion = {
        "Caja 001": {
            "estado": "Ocupado",
            "operador": "Paula Andrea Rojas",
            "cliente": {
                "Turno": "N° 016",
                "Cliente": "Ana Sofía Torres",
                "DNI": "41928374",
                "Destinatario": "Carlos Torres",
                "DNI_Destinatario": "45891230",
                "Tramite": "Envío",
                "Modalidad": "Aéreo",
                "Origen": "Lima - Agencia Central (Santa Anita)",
                "Destino": "Cusco - Agencia Av. de la Cultura / Wanchaq",
                "Condicion_Pago": "Pagado por Remitente (En Origen)"
            }
        },
        "Caja 002": {"estado": "Vacío", "operador": "Carlos Mendoza", "cliente": None},
        "Caja 003": {"estado": "Vacío", "operador": "Marycielo Perez", "cliente": None}
    }

if 'cola_espera' not in st.session_state:
    st.session_state.cola_espera = [
        {
            "Turno": "N° 015",
            "Cliente": "Paula Jiménez",
            "DNI": "45896321",
            "Destinatario": "María Jiménez",
            "DNI_Destinatario": "40125478",
            "Tramite": "Envío",
            "Modalidad": "Terrestre",
            "Origen": "Lima - Agencia Central (Santa Anita)",
            "Destino": "Arequipa - Agencia Parque Industrial / Cayma",
            "Condicion_Pago": "Por Cobrar al Destinatario (En Destino)",
            "Hora": "10:20 a.m."
        },
        {
            "Turno": "N° 017",
            "Cliente": "Luis Alberto Salazar",
            "DNI": "72849102",
            "Destinatario": "Jorge Salazar",
            "DNI_Destinatario": "43987654",
            "Tramite": "Recojo",
            "Modalidad": "Marítimo",
            "Origen": "Loreto - Iquitos (Carga Fluvial / Aérea)",
            "Destino": "Lima - Agencia Central (Santa Anita)",
            "Condicion_Pago": "Pagado por Remitente (En Origen)",
            "Hora": "10:24 a.m."
        }
    ]

if 'contador_turno' not in st.session_state:
    st.session_state.contador_turno = 18

if 'encomiendas' not in st.session_state:
    st.session_state.encomiendas = [
        {
            "Código": "SL-000124", "DNI_Remitente": "72849102", "Remitente": "Juan Carlos Pérez",
            "DNI_Recojo": "41928374", "Persona_Recojo": "Ana Sofía Torres",
            "Tramite": "Envío", "Modalidad": "Terrestre", "Tamano": "Mediano", "Bultos": 1,
            "Condicion_Pago": "Pagado por Remitente (En Origen)",
            "Origen": "Lima - Agencia Central (Santa Anita)", "Destino": "Arequipa - Agencia Parque Industrial / Cayma",
            "Peso": 2.00, "Costo": 17.00, "Pagado": "Pagado S/ 17.00", "Estado Paquete": "En Tránsito",
            "Fecha": "18/11/2026 10:22", "Operador": "Marycielo Nicole Perez Arroyo",
            "Foto": b''
        }
    ]

if 'contador_codigo' not in st.session_state:
    st.session_state.contador_codigo = 125

if 'quejas_clientes' not in st.session_state:
    st.session_state.quejas_clientes = [
        {"Mes": "Noviembre", "Año": "2026", "Orden": "SL-000110", "Cliente": "Roberto Gómez", "Motivo": "Demora en tránsito aéreo", "Estado": "Resuelto"}
    ]

if 'chat_ia' not in st.session_state:
    st.session_state.chat_ia = "Sistema IA conectado. Pregúntame lo que necesites sobre el sistema."

# --- ESTILOS CSS MODO DARK Y TEMA OSCURO FIJO ---
if st.session_state.usuario_actual is not None and fondo_app_base64:
    app_bg_css = """
    .stApp {
        background: linear-gradient(rgba(9, 13, 22, 0.85), rgba(15, 23, 42, 0.92)), url("data:image/jpeg;base64,REPLACE_FONDO");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        color: #F8FAFC;
        font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    }
    """.replace("REPLACE_FONDO", fondo_app_base64)
else:
    app_bg_css = """
    .stApp {
        background: linear-gradient(180deg, #090D16 0%, #0F172A 100%);
        color: #F8FAFC;
        font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    }
    """

st.markdown(f"""
<style>
    {app_bg_css}
    [data-testid="stSidebar"] {{
        background-color: #0B132B;
        color: #FFFFFF;
        border-right: 1px solid #1E293B;
    }}
    [data-testid="stSidebar"] * {{
        color: #E2E8F0 !important;
    }}
    .corp-header {{
        background: rgba(30, 41, 59, 0.9);
        backdrop-filter: blur(10px);
        color: white;
        padding: 20px 28px;
        border-radius: 10px;
        margin-bottom: 24px;
        border-bottom: 4px solid #3B82F6;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.4);
    }}
    .corp-header h1 {{
        margin: 0;
        font-size: 26px;
        font-weight: 800;
        letter-spacing: 0.8px;
        color: #FFFFFF;
    }}
    .corp-header p {{
        margin: 2px 0 0 0;
        font-size: 13px;
        color: #94A3B8;
    }}
    .panel-banner {{
        background-color: rgba(30, 41, 59, 0.9);
        color: #FFFFFF;
        padding: 12px 18px;
        border-radius: 6px 6px 0 0;
        font-weight: 600;
        font-size: 15px;
        margin-bottom: 14px;
        border: 1px solid #334155;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }}
    .caja-card {{
        background-color: rgba(30, 41, 59, 0.88);
        backdrop-filter: blur(8px);
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 12px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.3);
    }}
    .caja-libre {{
        border-left: 6px solid #22C55E;
    }}
    .caja-ocupada {{
        border-left: 6px solid #3B82F6;
    }}
    .ai-box {{
        background-color: rgba(19, 30, 56, 0.9);
        border: 1px solid #3B82F6;
        border-radius: 8px;
        padding: 14px;
        margin-top: 10px;
        font-size: 13px;
        color: #F8FAFC;
        box-shadow: 0 2px 8px rgba(0,0,0,0.4);
    }}
    [data-testid="stMetric"] {{
        background-color: rgba(30, 41, 59, 0.88);
        backdrop-filter: blur(8px);
        padding: 16px;
        border-radius: 8px;
        border: 1px solid #334155;
        border-top: 4px solid #38BDF8;
        box-shadow: 0 2px 5px rgba(0,0,0,0.3);
    }}
    div.stButton > button[kind="primary"] {{
        background-color: #2563EB;
        border-color: #1D4ED8;
        color: #FFFFFF;
        font-weight: 600;
        border-radius: 6px;
    }}
    div.stButton > button[kind="primary"]:hover {{
        background-color: #1D4ED8;
        border-color: #1E40AF;
    }}
</style>
""", unsafe_allow_html=True)

def generar_imagen_paquete(codigo, origen, destino, modalidad, peso, bultos, condicion_pago, total, tamano="Mediano"):
    img = Image.new('RGB', (480, 280), color=(15, 23, 42))
    d = ImageDraw.Draw(img)
    d.rectangle([12, 12, 468, 268], outline=(51, 65, 85), width=3)
    d.rectangle([12, 12, 468, 48], fill=(30, 41, 59))
    d.text((24, 24), f"VISION IA | ESCANER - {codigo}", fill=(255, 255, 255))
    d.rectangle([90, 175, 390, 192], fill=(71, 85, 105), outline=(100, 116, 139), width=2)

    if tamano == "Pequeño":
        box = [195, 125, 285, 175]
    elif tamano == "Grande":
        box = [125, 65, 355, 175]
    else:
        box = [160, 95, 320, 175]

    d.rectangle(box, fill=(198, 156, 109), outline=(120, 82, 45), width=2)
    mid_x = (box[0] + box[2]) // 2
    mid_y = (box[1] + box[3]) // 2
    d.line([box[0], mid_y, box[2], mid_y], fill=(120, 82, 45), width=2)
    d.line([mid_x, box[1], mid_x, box[3]], fill=(120, 82, 45), width=2)
    d.rectangle([box[0]-4, box[1]-4, box[2]+4, box[3]+4], outline=(34, 197, 94), width=2)

    pago_corto = "REMITENTE PAGA" if "Remitente" in condicion_pago else "DESTINATARIO PAGA"
    d.text((24, 198), f"BULTOS: {bultos} | {pago_corto}", fill=(34, 197, 94))
    d.text((24, 220), f"ORIGEN: {origen[:16].upper()} -> DEST: {destino[:16].upper()}", fill=(248, 250, 252))
    d.text((24, 242), f"VIA: {modalidad.upper()} | PESO: {peso:.2f} kg | TOTAL: S/ {total:.2f}", fill=(56, 189, 248))

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

# ==============================================================================
# PANTALLA DE ACCESO CORPORATIVO (LOGIN PRIVADO)
# ==============================================================================
if st.session_state.usuario_actual is None:
    st.markdown("<br><br>", unsafe_allow_html=True)
    _, col_login, _ = st.columns([1, 1.4, 1])
    with col_login:
        if logo_base64:
            st.markdown(f"""
            <div style="text-align: center; margin-bottom: 22px;">
                <img src="data:image/png;base64,{logo_base64}" style="max-width: 220px; border-radius: 14px; box-shadow: 0 10px 25px rgba(0,0,0,0.6);">
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background: rgba(30, 41, 59, 0.9); padding: 30px; border-radius: 14px; box-shadow: 0 12px 30px rgba(0,0,0,0.6); text-align:center; color:white; border-top: 6px solid #3B82F6;">
                <h1 style="margin:0; font-size:28px; font-weight:800; letter-spacing:1px;">SMART LOGISTICS</h1>
            </div>
            <br>
            """, unsafe_allow_html=True)

        with st.form("form_login"):
            st.subheader("Autenticación de Personal")
            u_in = st.text_input("Usuario Corporativo", placeholder="Ingrese su usuario")
            p_in = st.text_input("Contraseña", type="password", placeholder="••••••••")
            if st.form_submit_button("Ingresar al Sistema", use_container_width=True, type="primary"):
                users = st.session_state.usuarios_autorizados
                if u_in in users and users[u_in]["password"] == p_in:
                    st.session_state.usuario_actual = users[u_in]
                    st.session_state.usuario_actual["username"] = u_in
                    st.rerun()
                else:
                    st.error("Credenciales inválidas o acceso no autorizado.")
    st.stop()

# ==============================================================================
# BARRA LATERAL Y ASISTENTE VIRTUAL IA
# ==============================================================================
user = st.session_state.usuario_actual

with st.sidebar:
    if logo_base64:
        st.markdown(f"""
        <div style="text-align: center; padding: 10px 0;">
            <img src="data:image/png;base64,{logo_base64}" width="110" style="border-radius: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.4);">
            <div style="font-size: 18px; font-weight: 800; color: #F8FAFC; margin-top: 8px; letter-spacing: 0.5px;">SMART LOGISTICS</div>
        </div>
        """, unsafe_allow_html=True)

    if st.button("📖 Ver Historia del Sistema", use_container_width=True):
        st.session_state.mostrar_historia = not st.session_state.mostrar_historia
        st.rerun()

    st.markdown("---")

    menu_items = [
        "Inicio",
        "Atención en Caja",
        "Gestión de Encomiendas y Clientes",
        "Personal",
        "Control de Cola",
        "Quejas y Reclamos",
        "Configuración"
    ]
    if user["rol"] == "Administradora":
        menu_items.insert(6, "Reportes y Administración 5S")

    if st.session_state.navegacion_menu not in menu_items:
        st.session_state.navegacion_menu = "Inicio"

    navegacion = st.radio("NAVEGACIÓN", menu_items, index=menu_items.index(st.session_state.navegacion_menu), label_visibility="collapsed")
    st.session_state.navegacion_menu = navegacion

    st.markdown("---")

    st.markdown("**ASISTENTE VIRTUAL IA**")
    en_espera = len(st.session_state.cola_espera)
    cajas_libres = sum(1 for c in st.session_state.cajas_atencion.values() if c["estado"] == "Vacío")

    if en_espera > 0:
        st.warning(f"Alerta IA: **{en_espera} cliente(s)** en cola | **{cajas_libres} caja(s)** libre(s).")
    else:
        st.success("Alerta IA: Flujo óptimo en agencia.")

    with st.form("form_ia_chat"):
        pregunta_usuario = st.text_input("Pregúntale a la IA", placeholder="Ej. ¿Cuántos clientes atendidos?")
        btn_enviar_ia = st.form_submit_button("Consultar IA", use_container_width=True, type="primary")

        if btn_enviar_ia and pregunta_usuario:
            p_low = pregunta_usuario.lower()
            clientes_exactos = st.session_state.clientes_atendidos_total
            total_enc = len(st.session_state.encomiendas) + 245
            ingresos_calc = sum([e['Costo'] for e in st.session_state.encomiendas if "Remitente" in e.get("Condicion_Pago", "")]) + 353.00

            if "paga" in p_low or "destinatario" in p_low or "remitente" in p_low or "cobrar" in p_low:
                resp = "El sistema indica automáticamente si paga el remitente (en origen) o el destinatario (en destino)."
            elif "cliente" in p_low or "atendido" in p_low or "atendidos" in p_low:
                resp = f"El sistema registra exactamente {clientes_exactos} clientes atendidos."
            elif "cola" in p_low or "espera" in p_low:
                resp = f"Hay {en_espera} clientes en cola y {cajas_libres} cajas libres."
            elif "tarifa" in p_low or "precio" in p_low or "costo" in p_low:
                resp = "Las tarifas se calculan con el peso (S/ 3.00/kg), bultos y la tarifa de destino."
            elif "encomienda" in p_low or "paquete" in p_low or "envío" in p_low:
                resp = f"Existen {total_enc} encomiendas registradas en total."
            elif "ingreso" in p_low or "dinero" in p_low:
                resp = f"Los ingresos actuales ascienden a S/ {ingresos_calc:.2f}."
            elif "queja" in p_low or "reclamo" in p_low:
                resp = f"Se tienen registrados {len(st.session_state.quejas_clientes)} reclamos."
            elif "personal" in p_low or "trabajador" in p_low:
                resp = f"Hay {len(st.session_state.usuarios_autorizados)} colaboradores activos."
            else:
                resp = f"Consulta sobre '{pregunta_usuario}': Smart Logistics operando en tiempo real."

            st.session_state.chat_ia = resp
            st.rerun()

    st.markdown(f'<div class="ai-box"><strong>Respuesta IA:</strong><br>{st.session_state.chat_ia}</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown(f"**{user['nombre']}**")
    st.caption(f"{user['rol']} | DNI: {user['dni']}")
    if st.button("Cerrar Sesión", use_container_width=True):
        st.session_state.usuario_actual = None
        st.rerun()

if st.session_state.mostrar_historia:
    st.markdown("""
    <div style="background: rgba(15, 23, 42, 0.95); border: 2px solid #3B82F6; padding: 28px; border-radius: 12px; margin-bottom: 24px; box-shadow: 0 8px 25px rgba(0,0,0,0.6);">
        <h2 style="color: #60A5FA; margin-top: 0;">📜 Historia y Origen de Smart Logistics</h2>
        <p style="color: #E2E8F0; line-height: 1.6; font-size: 15px;">
            <strong>Smart Logistics</strong> nació para digitalizar y optimizar la gestión operativa en agencias de transporte y encomiendas en el Perú, integrando control de turnos, báscula, visión artificial, bultos y paneles gerenciales con metodología 5S.
        </p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Cerrar Historia / Volver al Sistema"):
        st.session_state.mostrar_historia = False
        st.rerun()

st.markdown(f"""
<div class="corp-header">
    <div style="display:flex; justify-content:space-between; align-items:center;">
        <div>
            <h1>SMART LOGISTICS</h1>
            <p>Módulo Activo: <strong>{navegacion.upper()}</strong></p>
        </div>
        <div style="text-align:right; font-size:13px; color:#E2E8F0;">
            <div><strong>Fecha:</strong> {datetime.now().strftime('%d/%m/%Y')}</div>
            <div><strong>Usuario:</strong> {user['nombre']}</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

df_encomiendas = pd.DataFrame(st.session_state.encomiendas)

# ==============================================================================
# 1. INICIO
# ==============================================================================
if navegacion == "Inicio":
    if st.session_state.mensaje_guardado:
        st.success(st.session_state.mensaje_guardado)
        st.session_state.mensaje_guardado = ""

    fk = st.session_state.reg_form_key
    col_reg, col_seg = st.columns([1.35, 1])

    cliente_activo = None
    for c_n, c_d in st.session_state.cajas_atencion.items():
        if c_d["estado"] == "Ocupado" and c_d["cliente"] is not None:
            cliente_activo = c_d["cliente"]
            break

    if cliente_activo:
        auto_nombre = cliente_activo.get("Cliente", "")
        auto_dni = cliente_activo.get("DNI", "")
        auto_dest = cliente_activo.get("Destinatario", "")
        auto_dni_dest = cliente_activo.get("DNI_Destinatario", "")
        auto_tramite = cliente_activo.get("Tramite", "Envío")
        auto_mod = cliente_activo.get("Modalidad", "Terrestre")
        auto_origen = cliente_activo.get("Origen", AGENCIAS_LISTA[0])
        auto_destino = cliente_activo.get("Destino", AGENCIAS_LISTA[1] if AGENCIAS_LISTA[1] != auto_origen else AGENCIAS_LISTA[0])
        auto_pago = cliente_activo.get("Condicion_Pago", "Pagado por Remitente (En Origen)")
    else:
        auto_nombre, auto_dni, auto_dest, auto_dni_dest = "", "", "", ""
        auto_tramite, auto_mod = "Envío", "Terrestre"
        auto_origen = AGENCIAS_LISTA[0]
        auto_destino = AGENCIAS_LISTA[1]
        auto_pago = "Pagado por Remitente (En Origen)"

    with col_reg:
        st.markdown('<div class="panel-banner">Registro y Validación Logística</div>', unsafe_allow_html=True)

        if cliente_activo:
            st.success(f"Ticket activo en Caja: **{cliente_activo['Turno']}** — {auto_nombre}")
        else:
            st.info("Sin cliente activo en caja. Puede completar los datos del registro.")

        c_mod, c_tram = st.columns(2)
        modalidad_sel = c_mod.radio(
            "Modalidad",
            ["Terrestre", "Aéreo", "Marítimo"],
            index=["Terrestre", "Aéreo", "Marítimo"].index(auto_mod) if auto_mod in ["Terrestre", "Aéreo", "Marítimo"] else 0,
            horizontal=True,
            key=f"mod_{fk}"
        )
        tramite_sel = c_tram.radio(
            "Tipo de Trámite",
            ["Envío", "Recojo"],
            index=0 if auto_tramite == "Envío" else 1,
            horizontal=True,
            key=f"tram_{fk}"
        )

        f_rem1, f_rem2 = st.columns(2)
        remitente_nom = f_rem1.text_input("Nombre de quien Envía (Remitente)", value=auto_nombre, key=f"rem_nom_{fk}")
        remitente_dni = f_rem2.text_input("DNI del Remitente", value=auto_dni, max_chars=8, key=f"rem_dni_{fk}")

        f_rec1, f_rec2 = st.columns(2)
        persona_recojo = f_rec1.text_input("Nombre del Destinatario (Quien Recoge)", value=auto_dest, key=f"rec_nom_{fk}")
        dni_recojo = f_rec2.text_input("DNI del Destinatario", value=auto_dni_dest, max_chars=8, key=f"rec_dni_{fk}")

        f_ruta1, f_ruta2 = st.columns(2)
        origen_sel = f_ruta1.selectbox(
            "Agencia de Origen",
            AGENCIAS_LISTA,
            index=AGENCIAS_LISTA.index(auto_origen) if auto_origen in AGENCIAS_LISTA else 0,
            key=f"orig_{fk}"
        )
        destinos_disponibles = [ag for ag in AGENCIAS_LISTA if ag != origen_sel]
        dest_idx = destinos_disponibles.index(auto_destino) if auto_destino in destinos_disponibles else 0
        destino_sel = f_ruta2.selectbox(
            "Agencia de Destino (Automático desde Ticket)",
            destinos_disponibles,
            index=dest_idx,
            key=f"dest_{fk}"
        )

        condicion_pago = st.radio(
            "Condición de Pago",
            ["Pagado por Remitente (En Origen)", "Por Cobrar al Destinatario (En Destino)"],
            index=0 if "Remitente" in auto_pago else 1,
            horizontal=True,
            key=f"pago_{fk}"
        )

        c_tam, c_bul, c_peso, c_calc = st.columns([1, 0.8, 1, 1.2])
        tamano_paquete = c_tam.selectbox("Tamaño (Visión IA)", ["Pequeño", "Mediano", "Grande"], index=1, key=f"tam_{fk}")
        cantidad_bultos = c_bul.number_input("Bultos", min_value=1, max_value=50, value=1, step=1, key=f"bul_{fk}")
        peso_kg = c_peso.number_input("Peso (kg) [S/ 3/kg]", min_value=0.5, max_value=150.0, value=1.0, step=0.5, key=f"peso_{fk}")

        tarifa_p = (peso_kg * 3.00) * cantidad_bultos
        tarifa_r = TARIFAS_RUTA.get(destino_sel, 3.00)
        total_pago = tarifa_p + tarifa_r

        with c_calc:
            if "Por Cobrar" in condicion_pago:
                st.metric("Total a Cobrar", f"S/ {total_pago:.2f}", delta="Destinatario paga")
            else:
                st.metric("Total Pagado", f"S/ {total_pago:.2f}", delta="Remitente pagó")

        codigo_actual = f"SL-000{st.session_state.contador_codigo}"
        vista_previa_img = generar_imagen_paquete(
            codigo_actual, origen_sel, destino_sel, modalidad_sel, peso_kg, cantidad_bultos, condicion_pago, total_pago, tamano_paquete
        )

        if st.button("Confirmar Operación, Captura IA y Guardar", use_container_width=True, type="primary"):
            estado_pago_txt = f"Pagado S/ {total_pago:.2f}" if "Remitente" in condicion_pago else f"Por Cobrar S/ {total_pago:.2f}"
            st.session_state.encomiendas.insert(0, {
                "Código": codigo_actual,
                "DNI_Remitente": remitente_dni or "40000000",
                "Remitente": remitente_nom or "Cliente General",
                "DNI_Recojo": dni_recojo or "40000000",
                "Persona_Recojo": persona_recojo or "Destinatario",
                "Tramite": tramite_sel,
                "Modalidad": modalidad_sel,
                "Tamano": tamano_paquete,
                "Bultos": cantidad_bultos,
                "Condicion_Pago": condicion_pago,
                "Origen": origen_sel,
                "Destino": destino_sel,
                "Peso": peso_kg,
                "Costo": total_pago,
                "Pagado": estado_pago_txt,
                "Estado Paquete": "En Agencia" if tramite_sel == "Envío" else "Entregado",
                "Fecha": datetime.now().strftime("%d/%m/%Y %I:%M %p"),
                "Operador": user["nombre"],
                "Foto": vista_previa_img
            })
            st.session_state.contador_codigo += 1
            st.session_state.clientes_atendidos_total += 1

            for c_n, c_d in st.session_state.cajas_atencion.items():
                if c_d["cliente"] and (c_d["cliente"]["DNI"] == auto_dni or c_d["cliente"]["Cliente"] == remitente_nom):
                    st.session_state.cajas_atencion[c_n]["estado"] = "Vacío"
                    st.session_state.cajas_atencion[c_n]["cliente"] = None

            st.session_state.reg_form_key += 1
            st.session_state.mensaje_guardado = f"Operación {codigo_actual} guardada en el sistema."
            st.session_state.navegacion_menu = "Inicio"
            st.rerun()

    with col_seg:
        st.markdown('<div class="panel-banner">Simulación de Escáner IA</div>', unsafe_allow_html=True)
        quien_paga_txt = "Remitente paga" if "Remitente" in condicion_pago else "Destinatario paga"
        st.info(f"**Trámite:** `{tramite_sel}` | **Pago:** `{quien_paga_txt}`")
        st.write(f"**Origen:** {origen_sel}")
        st.write(f"**Destino:** {destino_sel}")
        st.image(vista_previa_img, caption=f"Escáner IA — {cantidad_bultos} Bulto(s) | {quien_paga_txt}", use_container_width=True)

# ==============================================================================
# 2. ATENCIÓN EN CAJA
# ==============================================================================
elif navegacion == "Atención en Caja":
    st.markdown('<div class="panel-banner">Control de Ventanillas y Llamado de Turnos</div>', unsafe_allow_html=True)

    cols_c = st.columns(3)
    for idx, (c_nom, c_info) in enumerate(st.session_state.cajas_atencion.items()):
        with cols_c[idx]:
            clase = "caja-libre" if c_info["estado"] == "Vacío" else "caja-ocupada"
            estado_txt = "DISPONIBLE" if c_info["estado"] == "Vacío" else f"OCUPADO - {c_info['cliente']['Cliente']}"
            st.markdown(f"""
            <div class="caja-card {clase}">
                <h4>{c_nom}</h4>
                <p><strong>Estado:</strong> {estado_txt}</p>
                <p style="font-size:12px; color:#94A3B8;">Operador: {c_info['operador']}</p>
            </div>
            """, unsafe_allow_html=True)

            if c_info["estado"] == "Vacío":
                if st.session_state.cola_espera:
                    if st.button(f"Llamar a {c_nom}", key=f"llamar_{c_nom}"):
                        sig = st.session_state.cola_espera.pop(0)
                        st.session_state.cajas_atencion[c_nom]["estado"] = "Ocupado"
                        st.session_state.cajas_atencion[c_nom]["cliente"] = sig
                        st.session_state.clientes_atendidos_total += 1
                        st.rerun()
            else:
                if st.button(f"Liberar {c_nom}", key=f"lib_{c_nom}"):
                    st.session_state.cajas_atencion[c_nom]["estado"] = "Vacío"
                    st.session_state.cajas_atencion[c_nom]["cliente"] = None
                    st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("Fila de Espera Actual en Cola")
    if st.session_state.cola_espera:
        st.dataframe(pd.DataFrame(st.session_state.cola_espera), use_container_width=True, hide_index=True)
    else:
        st.info("No hay clientes en espera.")

# ==============================================================================
# 3. GESTIÓN DE ENCOMIENDAS Y CLIENTES
# ==============================================================================
elif navegacion == "Gestión de Encomiendas y Clientes":
    st.markdown('<div class="panel-banner">Directorio Unificado de Encomiendas, Clientes y Bultos</div>', unsafe_allow_html=True)

    busq = st.text_input("Buscar por Código de Orden, DNI o Nombre", placeholder="Ej. SL-000124")
    if busq:
        c_b = busq.strip().upper()
        res = [e for e in st.session_state.encomiendas if c_b in e["Código"].upper() or c_b in e["DNI_Remitente"] or c_b in e["Remitente"].upper() or c_b in e["Persona_Recojo"].upper()]
        if res:
            for r in res:
                st.success(f"Orden {r['Código']} — Origen: {r['Origen']} -> Destino: {r['Destino']}")
                st.write(f"Estado: **{r['Estado Paquete']}** | Bultos: {r.get('Bultos', 1)} | Pago: {r.get('Condicion_Pago', 'Remitente')} ({r['Pagado']})")
                st.image(r["Foto"], width=400)
        else:
            st.warning("No se encontró coincidencia.")

    st.markdown("<br>", unsafe_allow_html=True)
    t_ter, t_aer, t_mar = st.tabs(["Terrestre", "Aéreo", "Marítimo"])
    for tab_o, mod_n in [(t_ter, "Terrestre"), (t_aer, "Aéreo"), (t_mar, "Marítimo")]:
        with tab_o:
            df_m = df_encomiendas[df_encomiendas["Modalidad"] == mod_n]
            if not df_m.empty:
                cols_mostradas = ["Código", "Tramite", "Origen", "Destino", "Tamano", "Bultos", "Peso", "Pagado", "Estado Paquete"]
                st.dataframe(df_m[cols_mostradas], use_container_width=True, hide_index=True)
            else:
                st.info(f"Sin registros en modalidad {mod_n}.")

# ==============================================================================
# 4. PERSONAL
# ==============================================================================
elif navegacion == "Personal":
    st.markdown('<div class="panel-banner">Gestión de Personal, Turnos y Bajas</div>', unsafe_allow_html=True)
    lista_p = [{"Usuario": k, "Nombre": v["nombre"], "DNI": v["dni"], "Cargo": v["rol"], "Turno": v["turno"], "Experiencia": v["experiencia"]} for k, v in st.session_state.usuarios_autorizados.items()]
    st.dataframe(pd.DataFrame(lista_p), use_container_width=True, hide_index=True)

    if user["rol"] == "Administradora":
        st.markdown("<br>", unsafe_allow_html=True)
        col_a, col_b = st.columns(2)
        with col_a:
            st.subheader("Registrar Colaborador")
            with st.form("form_alta_p"):
                an = st.text_input("Nombres y Apellidos")
                ad = st.text_input("DNI", max_chars=8)
                ar = st.selectbox("Cargo", ["Operador de Caja", "Clasificador", "Administradora"])
                au = st.text_input("Usuario")
                ap = st.text_input("Contraseña", type="password")
                at = st.selectbox("Turno", ["Mañana", "Tarde", "Noche"])
                ae = st.selectbox("Experiencia", ["Experimentado", "Nuevo"])
                if st.form_submit_button("Guardar", type="primary"):
                    if an and au and len(ad) == 8:
                        st.session_state.usuarios_autorizados[au] = {"password": ap, "nombre": an, "rol": ar, "dni": ad, "turno": at, "experiencia": ae}
                        st.success("Guardado con éxito.")
                        st.rerun()
        with col_b:
            st.subheader("Dar de Baja Trabajador")
            with st.form("form_baja_p"):
                ud = st.selectbox("Usuario a Eliminar", [u for u in st.session_state.usuarios_autorizados.keys() if u != "admin"])
                if st.form_submit_button("Eliminar", type="primary"):
                    if ud in st.session_state.usuarios_autorizados:
                        del st.session_state.usuarios_autorizados[ud]
                        st.success("Trabajador eliminado.")
                        st.rerun()

# ==============================================================================
# 5. CONTROL DE COLA
# ==============================================================================
elif navegacion == "Control de Cola":
    st.markdown('<div class="panel-banner">Gestión de Cola y Emisión de Tickets</div>', unsafe_allow_html=True)
    c_add, c_del = st.columns(2)
    with c_add:
        st.subheader("Nuevo Ingreso a la Cola")
        with st.form("form_add_c"):
            cn = st.text_input("Nombre del Cliente (Quien realiza el trámite)")
            cd = st.text_input("DNI del Cliente", max_chars=8)
            cdest = st.text_input("Nombre del Destinatario (Quien recoge)")
            cdni_dest = st.text_input("DNI del Destinatario", max_chars=8)
            ct = st.selectbox("Trámite", ["Envío", "Recojo"])
            cm = st.selectbox("Modalidad", ["Terrestre", "Aéreo", "Marítimo"])
            corigen = st.selectbox("Agencia de Origen", AGENCIAS_LISTA)
            cdestino = st.selectbox("Agencia de Destino", AGENCIAS_LISTA, index=1)
            cpago = st.selectbox("¿Quién paga?", ["Pagado por Remitente (En Origen)", "Por Cobrar al Destinatario (En Destino)"])
            if st.form_submit_button("Generar Ticket", type="primary", use_container_width=True):
                if not cn or len(cd) != 8:
                    st.error("Complete el nombre y DNI de 8 dígitos.")
                elif corigen == cdestino:
                    st.error("La agencia de origen y destino no pueden ser iguales.")
                else:
                    t_id = f"N° {st.session_state.contador_turno:03d}"
                    st.session_state.cola_espera.append({
                        "Turno": t_id,
                        "Cliente": cn,
                        "DNI": cd,
                        "Destinatario": cdest or "Titular",
                        "DNI_Destinatario": cdni_dest or cd,
                        "Tramite": ct,
                        "Modalidad": cm,
                        "Origen": corigen,
                        "Destino": cdestino,
                        "Condicion_Pago": cpago,
                        "Hora": datetime.now().strftime("%I:%M %p")
                    })
                    st.session_state.contador_turno += 1
                    st.success(f"Ticket {t_id} generado con origen y destino.")
                    st.rerun()

    with c_del:
        st.subheader("Eliminar Turno Duplicado o Erróneo")
        with st.form("form_del_c"):
            t_disp = [t["Turno"] + " - " + t["Cliente"] for t in st.session_state.cola_espera]
            tsel = st.selectbox("Seleccionar Turno a Borrar", t_disp if t_disp else ["Sin turnos"])
            if st.form_submit_button("Borrar Turno de la Cola", type="primary"):
                if t_disp and tsel != "Sin turnos":
                    tnum = tsel.split(" - ")[0]
                    st.session_state.cola_espera = [t for t in st.session_state.cola_espera if t["Turno"] != tnum]
                    st.success(f"Turno {tnum} eliminado.")
                    st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    st.dataframe(pd.DataFrame(st.session_state.cola_espera), use_container_width=True, hide_index=True)

# ==============================================================================
# 6. REPORTES Y ADMINISTRACIÓN 5S
# ==============================================================================
elif navegacion == "Reportes y Administración 5S":
    st.markdown('<div class="panel-banner">Panel Gerencial de Reportes, KPIs y Metodología 5S</div>', unsafe_allow_html=True)

    total_encomiendas_dyn = len(df_encomiendas) + 245
    ingresos_totales_dyn = sum([e['Costo'] for e in st.session_state.encomiendas if "Remitente" in e.get("Condicion_Pago", "")]) + 353.00

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Total Encomiendas", total_encomiendas_dyn, "+12%")
    k2.metric("Clientes Atendidos", st.session_state.clientes_atendidos_total, "+8%")
    k3.metric("Tiempo Promedio", "1.8 min", "-0.2 min")
    k4.metric("Eficiencia Operativa", "96.4%", "+2%")
    k5.metric("Ingresos (Origen)", f"S/ {ingresos_totales_dyn:.2f}", "+15%")

    st.markdown("<br>", unsafe_allow_html=True)
    g1, g2 = st.columns(2)
    with g1:
        st.subheader("Indicadores de Rendimiento Semanal (%)")
        df_rend = pd.DataFrame({"Eficiencia (%)": [88, 91, 94, 96, 95]}, index=["Lun", "Mar", "Mié", "Jue", "Vie"])
        st.bar_chart(df_rend, height=240)
    with g2:
        st.subheader("Flujo Operativo por Modalidad")
        df_flujo = pd.DataFrame({
            "Terrestre": [40, 48, 45, 60, 68],
            "Aéreo": [20, 25, 22, 30, 35],
            "Marítimo": [10, 12, 15, 18, 20]
        }, index=["Lun", "Mar", "Mié", "Jue", "Vie"])
        st.line_chart(df_flujo, height=240)

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("Metodología 5S Aplicada en Smart Logistics")
    s1, s2, s3, s4, s5 = st.columns(5)
    s1.info("**1. SEIRI (Clasificar)**\n\nSeparación de envíos y recogidos.")
    s2.info("**2. SEITON (Ordenar)**\n\nAsignación limpia de cajas y turnos.")
    s3.info("**3. SEISO (Limpiar)**\n\nOperación digital sin papeles.")
    s4.info("**4. SEIKETSU (Estandarizar)**\n\nTest de tarifas y procesos.")
    s5.info("**5. SHITSUKE (Disciplina)**\n\nControl diario de KPIs.")

# ==============================================================================
# 7. QUEJAS Y RECLAMOS
# ==============================================================================
elif navegacion == "Quejas y Reclamos":
    st.markdown('<div class="panel-banner">Registro y Supervisión de Quejas por Mes y Año</div>', unsafe_allow_html=True)
    c_m, c_a = st.columns(2)
    mes_f = c_m.selectbox("Mes", ["Todos", "Noviembre", "Diciembre", "Enero"])
    anio_f = c_a.selectbox("Año", ["2026", "2027"])

    df_q = pd.DataFrame(st.session_state.quejas_clientes)
    if mes_f != "Todos":
        df_q = df_q[df_q["Mes"] == mes_f]
    df_q = df_q[df_q["Año"] == anio_f]
    st.dataframe(df_q, use_container_width=True, hide_index=True)

    with st.form("form_q"):
        st.subheader("Registrar Nueva Queja de Cliente")
        qo = st.text_input("Número de Orden")
        qc = st.text_input("Nombre del Cliente")
        qm = st.text_input("Motivo del Reclamo")
        if st.form_submit_button("Guardar Reclamo", type="primary"):
            if qo and qc and qm:
                st.session_state.quejas_clientes.append({"Mes": "Noviembre", "Año": "2026", "Orden": qo, "Cliente": qc, "Motivo": qm, "Estado": "Pendiente"})
                st.success("Reclamo registrado.")
                st.rerun()

# ==============================================================================
# 8. CONFIGURACIÓN
# ==============================================================================
elif navegacion == "Configuración":
    st.markdown('<div class="panel-banner">Configuración de Hardware y Sensores</div>', unsafe_allow_html=True)
    st.success("Balanza Electrónica Industrial (Puerto COM3): **ACTIVADA Y SINCRONIZADA**")
    st.success("Escáner Óptico de Visión Artificial: **ACTIVADO**")
    st.success("Sistema de Asistencia IA: **CONECTADO Y ACTIVO**")