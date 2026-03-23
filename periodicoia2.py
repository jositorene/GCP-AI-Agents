import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

import os
from dotenv import load_dotenv
from agentes import SocialMediaAgent
from agentes import VerificadorAgent
from tenacity import RetryError



# Configuración inicial
load_dotenv()
st.set_page_config(
    page_title="Flash Newspaper", 
    page_icon="images/logo.jpeg", 
    layout="wide"
)

# Cargar CSS 
def load_interface_settings():
    # Cargar style.css si existe
    if os.path.exists("style.css"):
        with open("style.css", "r", encoding="utf-8") as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

load_interface_settings()

# Inicializar Agentes (Usa tu clave aquí o en el .env)
MI_LLAVE = os.getenv("GEMINI_API_KEY") 
agente_promotor = SocialMediaAgent(api_key_interna=MI_LLAVE)
agente_verificador = VerificadorAgent(api_key=MI_LLAVE)


st.set_page_config(page_title="Periódico IA Avanzado", page_icon="📰", layout="wide")

# ===========================
# Sidebar
# ===========================
st.sidebar.title("Periódico IA")
menu = st.sidebar.radio(
    "Selecciona sección:",
    [
        "📊 Dashboard", 
        "🔍 News Research", 
        "✍️ Article Generation", 
        "✅ News Verifier", 
        "💬 Reader Interaction", 
        "📱 Social Media"
    ]
)

# ===========================
# Dashboard Avanzado
# ===========================
if menu == "📊 Dashboard":
    st.title("📊 Dashboard Principal Avanzado")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Suscriptores", "1,245", "+5%")
    col2.metric("Visitas Hoy", "3,212", "-2%")
    col3.metric("Artículos Generados", "58", "+8%")
    col4.metric("Interacciones Redes", "1,102", "+12%")

    # Gráfico de tendencias
    st.subheader("📈 Tendencias de Lectores")
    data = pd.DataFrame({
        'Día': pd.date_range(start='2026-03-01', periods=10),
        'Visitas': np.random.randint(2000, 4000, size=10),
        'Interacciones': np.random.randint(500, 1500, size=10)
    })
    st.line_chart(data.set_index('Día'))

    # Artículos recientes en tarjetas
    st.subheader("📰 Artículos Recientes")
    articles = [
        {"Título": "IA en Educación", "Autor": "Laura Pérez", "Fecha": "2026-03-09", "Resumen": "Cómo la inteligencia artificial transforma la educación en la región."},
        {"Título": "Energías Renovables", "Autor": "Carlos Ruiz", "Fecha": "2026-03-08", "Resumen": "El impacto de la energía solar y eólica en la economía local."},
        {"Título": "Deportes Locales", "Autor": "Ana Gómez", "Fecha": "2026-03-07", "Resumen": "Resumen de los eventos deportivos recientes y próximos."}
    ]
    for art in articles:
        st.markdown(f"""
        <div style="border:1px solid #ddd; padding:15px; margin-bottom:10px; border-radius:5px;">
        <h4>{art['Título']}</h4>
        <p><em>{art['Autor']} | {art['Fecha']}</em></p>
        <p>{art['Resumen']}</p>
        </div>""")

# ===========================
# News Research Agent
# ===========================
elif menu == "🔍 News Research":
    st.title("🔍 News Research Agent")
    st.markdown("Investiga tendencias y genera ideas de artículos.")
    trends = ["IA en educación", "Energías renovables", "Deportes locales", "Política regional"]
    st.subheader("Tendencias actuales")
    st.write(trends)
    idea = st.text_input("Escribe un tema para generar idea de artículo")
    if st.button("Generar idea"):
        st.success(f"Idea generada: 'Cómo {idea} está cambiando nuestra región'")

# ===========================
# Article Generation Agent
# ===========================
elif menu == "✍️ Article Generation":
    st.title("✍️ Article Generation Agent")
    topic = st.text_input("Tema del artículo")
    if st.button("Generar Artículo"):
        st.subheader(f"Artículo: {topic}")
        st.write("Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.")

# ===========================
# Fact Checking Agent
# ===========================
elif menu == "✅ News Verifier":
    # --- Cabecera con Logo ---
    col_logo, col_text = st.columns([1, 5])
    with col_logo:
        # Intentamos cargar el logo desde la carpeta images
        if os.path.exists("images/logo.jpeg"):
            st.image("images/logo.jpeg", use_container_width=True)
        else:
            st.markdown("<h1 style='text-align: center;'>⚡</h1>", unsafe_allow_html=True)     
    with col_text:
        st.markdown("<h1 style='margin-bottom: 0px;'>Flash Newspaper</h1>", unsafe_allow_html=True)
        st.subheader("Verificador de Noticias")
        st.info("Verifica tu noticia.")

    st.divider()

    # --- Área de Edición de la Noticia ---
    st.subheader("📝 Noticia a procesar")
    
    # Recuperamos la noticia del estado de la sesión o usamos un texto vacío por defecto
    noticia_previa = st.session_state.get('noticia_para_redes', """Muere Chuck Norris: El fin de una leyenda del cine y las artes marciales

MADRID – El mundo del espectáculo está de luto tras confirmarse el fallecimiento de Carlos Ray "Chuck" Norris a los 85 años. El actor, que se convirtió en un fenómeno global no solo por sus películas sino por los infinitos "datos" y memes sobre su supuesta invencibilidad, murió pacíficamente en su residencia de Texas rodeado de su familia.

Norris, seis veces campeón del mundo de karate de peso medio y fundador de su propio arte marcial, el Chun Kuk Do, saltó a la fama internacional tras su mítica pelea contra Bruce Lee en 'El furor del dragón' (1972). Sin embargo, fue su papel como el sargento Cordell Walker en la serie 'Walker, Texas Ranger' lo que lo consagró como el héroe de acción definitivo durante más de una década.

Más allá de las pantallas, Chuck Norris fue un filántropo dedicado, impulsando programas como "Kickstart Kids" para alejar a los jóvenes de las drogas a través del deporte. Su legado trasciende el cine; se convirtió en el primer occidental en alcanzar el cinturón negro de octavo grado en Taekwondo y en un icono cultural que demostró que, a veces, la realidad supera a la ficción. 

Hoy, internet se despide del hombre que, según la leyenda, "no dormía, sino que esperaba". Descanse en paz, el eterno Walker."""
)
    
    noticia_editable = st.text_area(
        "Edita el contenido antes de verificarla en caso de ser necesario:",
        value=noticia_previa,
        height=250,
        key="noticia_editor_area"
    )

    # --- Botón de Acción con el Agente ---
    # 2. Área de texto para que el usuario pueda editar o pegar una noticia nueva
    if st.button("🔍 Iniciar Verificación"):
        if not noticia_previa.strip():
            st.warning("Por favor, introduce un texto para verificar.")
        else:
            with st.spinner("Consultando fuentes confiables y analizando metadatos..."):
                try:                  
                    # Llamamos al método (asumiendo que se llama verificar_noticia o similar)
                    resultado = agente_verificador.verificar_noticia(noticia_previa)

                    # 3. Mostrar resultados con estilo visual
                    st.markdown("### 📊 Informe de Verificación")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        # Usamos la nueva clave "Estado"
                        estado = resultado.get('Estado', 'REVISIÓN')
                        if estado == "APROBADO":
                            st.metric("Veredicto", "✅ APROBADO")
                        elif estado == "RECHAZADO":
                            st.metric("Veredicto", "❌ RECHAZADO")
                        else:
                            st.metric("Veredicto", "⚠️ REVISIÓN")
                
                    with col2:
                        confianza = resultado.get('confianza', 0)
                        st.metric("Confianza", f"{confianza}%")
                
                    with col3:
                        n_fuentes = resultado.get('fuentes_consultadas', 0)
                        st.metric("Fuentes", n_fuentes)

                    # 4. Análisis Detallado
                    st.markdown("#### 📝 Análisis Detallado")
                    st.info(resultado.get('explicacion', "No hay detalles adicionales."))

                    # 5. Hallazgos y Alertas (Nuevos campos del JSON)
                    c1, c2 = st.columns(2)
                    with c1:
                        st.write("**📍 Hallazgos:**")
                        for h in resultado.get('Hallazgos', []):
                            st.write(f"- {h}")
                    with c2:
                        st.write("**🚩 Alertas:**")
                        alertas = resultado.get('Alertas')
                        if alertas:
                            st.warning(alertas) if isinstance(alertas, str) else st.write(alertas)
                        else:
                            st.write("No se detectaron alertas.")

                    # 6. Listado de Fuentes Detectadas
                    with st.expander("🔗 Ver fuentes originales (GDELT)"):
                        lista_fuentes = resultado.get('Fuentes', [])
                        if lista_fuentes:
                            if isinstance(lista_fuentes, list):
                                for f in lista_fuentes:
                                    st.write(f"- {f}")
                            else:
                                st.write(lista_fuentes)
                        else:
                            st.write("No se recuperaron fuentes específicas.")

                except Exception as e:
                    st.error(f"Error en la verificación: {str(e)}")

    st.markdown("---")
    st.caption("Nota: El sistema utiliza modelos de IA para contrastar información pública disponible hasta la fecha.")

# ===========================
# Reader Interaction Agent
# ===========================
elif menu == "💬 Reader Interaction":
    st.title("💬 Reader Interaction")
    if 'chat' not in st.session_state:
        st.session_state.chat = []

    user_input = st.text_input("Tu mensaje:")
    if st.button("Enviar"):
        if user_input:
            st.session_state.chat.append({"role": "Usuario", "message": user_input})
            st.session_state.chat.append({"role": "Agente", "message": f"Respuesta simulada a: {user_input}"})

    for msg in st.session_state.chat:
        if msg['role'] == 'Usuario':
            st.markdown(f"**Tú:** {msg['message']}")
        else:
            st.markdown(f"**Agente:** {msg['message']}")

# ===========================
# Social Media Agent
# ===========================
elif menu == "📱 Social Media":
    # --- Cabecera con Logo ---
    col_logo, col_text = st.columns([1, 5])
    with col_logo:
        # Intentamos cargar el logo desde la carpeta images
        if os.path.exists("images/logo.jpeg"):
            st.image("images/logo.jpeg", use_container_width=True)
        else:
            st.markdown("<h1 style='text-align: center;'>⚡</h1>", unsafe_allow_html=True)
            
    with col_text:
        st.markdown("<h1 style='margin-bottom: 0px;'>Flash Newspaper</h1>", unsafe_allow_html=True)
        st.subheader("Social Media Hub")
        st.info("Transforma tus noticias en contenido viral para múltiples plataformas.")

    st.divider()

    # --- Área de Edición de la Noticia ---
    st.subheader("📝 Noticia a procesar")
    
    # Recuperamos la noticia del estado de la sesión o usamos un texto vacío por defecto
    noticia_previa = st.session_state.get('noticia_para_redes', """Muere Chuck Norris: El fin de una leyenda del cine y las artes marciales

MADRID – El mundo del espectáculo está de luto tras confirmarse el fallecimiento de Carlos Ray "Chuck" Norris a los 85 años. El actor, que se convirtió en un fenómeno global no solo por sus películas sino por los infinitos "datos" y memes sobre su supuesta invencibilidad, murió pacíficamente en su residencia de Texas rodeado de su familia.

Norris, seis veces campeón del mundo de karate de peso medio y fundador de su propio arte marcial, el Chun Kuk Do, saltó a la fama internacional tras su mítica pelea contra Bruce Lee en 'El furor del dragón' (1972). Sin embargo, fue su papel como el sargento Cordell Walker en la serie 'Walker, Texas Ranger' lo que lo consagró como el héroe de acción definitivo durante más de una década.

Más allá de las pantallas, Chuck Norris fue un filántropo dedicado, impulsando programas como "Kickstart Kids" para alejar a los jóvenes de las drogas a través del deporte. Su legado trasciende el cine; se convirtió en el primer occidental en alcanzar el cinturón negro de octavo grado en Taekwondo y en un icono cultural que demostró que, a veces, la realidad supera a la ficción. 

Hoy, internet se despide del hombre que, según la leyenda, "no dormía, sino que esperaba". Descanse en paz, el eterno Walker."""
)
    
    noticia_editable = st.text_area(
        "Edita el contenido antes de fragmentarlo:",
        value=noticia_previa,
        height=250,
        key="noticia_editor_area"
    )

    # --- Botón de Acción con el Agente ---
    if st.button("🚀 ADAPTAR A RRSS", use_container_width=True, type="primary"):
        if not noticia_editable or noticia_editable.strip() == "":
            st.warning("Por favor, introduce algún texto para procesar.")
        else:
            with st.spinner("El Agente Promotor está fragmentando el contenido..."):
                try:
                    # Llamada real al agente definido en agentes.py
                    resultado_ia = agente_promotor.generar_contenido(noticia_editable)
                    
                    # Guardamos el resultado en la sesión para que no desaparezca al interactuar
                    st.session_state.resultado_rrss = resultado_ia
                    st.success("✅ ¡Contenido adaptado con éxito!")
                except RetryError:
                    # Este error sale si Tenacity agota los 3 intentos
                    st.error("⚠️ La IA está saturada ahora mismo. Por favor, espera 1 minuto antes de volver a intentarlo.")
                except Exception as e:
                    st.error(f"Hubo un error inesperado: {e}")

    # --- Visualización de Formatos (Solo si hay un resultado) ---
    if 'resultado_rrss' in st.session_state:
        st.markdown("### 📱 Propuestas de Publicación")
        
        # Creamos las pestañas para cada red social
        tab_ig, tab_x, tab_tk = st.tabs(["📸 Instagram", "🐦 X (Twitter)", "🎵 TikTok"])

        # Separamos el texto por los divisores '---' que genera el agente
        partes = st.session_state.resultado_rrss.split("---")
        
        # Función auxiliar para limpiar el texto de las cabeceras del agente
        def limpiar_bloque(texto, titulo):
            return texto.replace(titulo, "").strip()

        with tab_ig:
            with st.container(border=True):
                contenido_ig = partes[1] if len(partes) > 1 else "Formato no generado"
                st.markdown(limpiar_bloque(contenido_ig, "FORMATO INSTAGRAM:"))
                st.button("Publicar en Instagram", key="pub_ig")

        with tab_x:
            with st.container(border=True):
                contenido_x = partes[2] if len(partes) > 2 else "Formato no generado"
                st.markdown(limpiar_bloque(contenido_x, "FORMATO X (Twitter):"))
                st.button("Publicar en X", key="pub_x")

        with tab_tk:
            with st.container(border=True):
                contenido_tk = partes[3] if len(partes) > 3 else "Formato no generado"
                st.markdown(limpiar_bloque(contenido_tk, "FORMATO TIKTOK:"))
                st.button("Enviar a TikTok", key="pub_tk")
                