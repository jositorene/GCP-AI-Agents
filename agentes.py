# --- Librerías de Google Gemini (IA) ---
from google import genai
from google.genai import types
from google.api_core.exceptions import ResourceExhausted  # Importación directa y segura

# --- Control de Reintentos y Errores (Tenacity) ---
# He unido las dos líneas de tenacity en una sola
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# --- Herramientas de Agentes (LangChain) ---
from langchain_core.tools import tool

# --- Utilidades del Sistema ---
import json
import time
import requests

class SocialMediaAgent:
    def __init__(self, api_key_interna):
        self.client = genai.Client(api_key=api_key_interna)
        self.model_id = "models/gemini-2.5-flash-lite"
        self.config = types.GenerateContentConfig(
            system_instruction="Eres un experto en redes sociales. Transforma artículos en contenido viral para Instagram, X y TikTok. Sé creativo y conciso."
        )
    
    # Configuración de Tenacity:
    # 1. Reintenta solo si el error es RESOURCE_EXHAUSTED (429)
    # 2. Espera de forma exponencial (10s, 20s, 40s...) para dar tiempo a la API
    # 3. Se detiene tras 3 intentos para no bloquear la app infinitamente
    @retry(
        retry=retry_if_exception_type(ResourceExhausted),
        wait=wait_exponential(multiplier=20, min=20, max=120),
        stop=stop_after_attempt(5),
        reraise=True
    )

    def generar_contenido(self, texto_noticia):
        prompt = f"""
        Analiza la siguiente noticia y genera contenido para redes sociales:
        
        NOTICIA:
        {texto_noticia}

        Genera contenido siguiendo estrictamente este formato:
        ---
        FORMATO INSTAGRAM:
        - [Texto para post]: Frase impactante, resumen, hashtags.
        - [Sugerencia visual]: Descripción de imagen.
        ---
        FORMATO X (Twitter):
        - [Tweet 1]: Mensaje conciso (máx. 280 caracteres).
        - [Tweet 2]: Hilo o dato extra.
        ---
        FORMATO TIKTOK:
        - [Script TikTok]: Gancho, Desarrollo, Cierre.
        - [Ideas Visuales]: Efectos y texto.
        """
        chat = self.client.chats.create(model=self.model_id, config=self.config)
        response = chat.send_message(prompt)
        return response.text


# Implementación de MPC
# mcp_archive (histórico del periódico con RAG)
# Este es el más importante para el periódico. servidor MCP local que consulte una base de datos vectorial.
# Carga tus datos: Sube los PDF o textos del periódico a un almacenamiento (Google Drive).
# Crea un Store Vectorial: Usa ChromaDB o FAISS en el Colab.
# Herramienta RAG: Define una función de Python que busque en esa base de datos y regístrala como una "tool" para Gemini.
@tool
def mcp_archive(query: str):
    """
    Consulta el archivo histórico global y local usando el Proyecto GDELT.
    Ideal para verificar eventos pasados, cifras mencionadas en prensa y cronologías.
    """
    base_url = "https://api.gdeltproject.org/api/v2/doc/doc"

    #return "Resultado real del archivo: El presupuesto en 2023 fue de 450.000€."
    # Parámetros de la consulta
    params = {
        "query": query,
        "mode": "artlist",          # Nos devuelve una lista de artículos
        "maxrecords": 10,            # Limitamos para no saturar de tokens a Gemini
        "format": "json",
        "sort": "rel"               # Ordenar por relevancia
    }

    try:
        response = requests.get(base_url, params=params, timeout=10)

        if response.status_code == 200:
            data = response.json()
            if "articles" in data:
                # Extraemos los títulos y fuentes para que el agente verifique
                resultados = []
                for art in data["articles"]:
                    resultados.append(f"Fuente: {art['source_country']} | Título: {art['title']} | Link: {art['url']}")

                contexto = "\n".join(resultados)
                return f"Hallazgos en el archivo histórico (GDELT):\n{contexto}"
            else:
                return "No se encontraron registros históricos específicos para esa consulta en GDELT."
        else:
            return f"Error al conectar con GDELT (Código: {response.status_code})."

    except Exception as e:
        return f"Error técnico consultando el archivo GDELT: {str(e)}"

# mcp_official y mcp_stats (APIs Externas)
# [mcp_official]: Para buscar en boletines oficiales.
# [mcp_stats]: Para contrastar cifras económicas.
# En lugar de programar cada API, utilizas servidores MCP ya existentes.
# Uso de Google Search MCP: uso del servidor oficial de Google Search para que el agente navegue por la web y busque el BOE o el INE en tiempo real.
# Sequential Thinking: Se configura para que el agente primero busque la cifra y luego la compare.
@tool
def mcp_official(entidad: str, fecha: str):
    """Busca en boletines oficiales vía API o Scraping."""
    # Simulación de llamada a API real (puedes usar requests aquí)
    return f"Boletín oficial de {entidad}: Cifra confirmada de 1.2M€."

# --- CLASE DEL AGENTE TRABAJADOR (WORKER) ---

class VerificadorAgent:
    def __init__(self, api_key):
        # MODIFICADO_AQUI: El agente ya tiene su propia configuración interna
        self.client = genai.Client(api_key=api_key)
        self.model_id = "models/gemini-2.5-flash-lite"
        self.tools = [mcp_archive, mcp_official]
        self.funcs = {t.name: t for t in self.tools}

        self.config = types.GenerateContentConfig(
            tools=self.tools,
            system_instruction="""
            Eres el 'Agente Verificador' del Periódico Local.
            Tu misión: Detectar errores en datos (nombres, fechas, cifras). usando tus herramientas
            Cuentas con acceso a GDELT (mcp_archive), que es la base de datos de noticias más grande del mundo.

            Cuando recibas una noticia para verificar genera estas TAREAS:
            1. Identifica cifras o hechos clave.
            2. Usa [mcp_archive] para buscar antecedentes históricos de los nombres o eventos mencionados.
            3. Compara lo que dice la noticia actual con los registros de GDELT.
            5. Sé breve y cita las fuentes que te devuelva la herramienta.

            FORMATO DE RESPUESTA un JSON con esta estructura exacta, importante: No añadas texto fuera del JSON.
            - "Estado": [APROBADO / REVISIÓN / RECHAZADO]
            - "Hallazgos": Lista de puntos verificados.
            - "Alertas": Si hay incoherencias (ej. fechas imposibles).
            - "Fuentes": fuentes que devuelve la herramienta GDELT
            - "verificado": true/false,
            - "confianza": número del 0 al 100,
            - "fuentes_consultadas": número de links encontrados,
            - "explicacion": "Tu resumen de hallazgos, alertas y fuentes citadas"
            """,
            response_mime_type="application/json"
        )

    @retry(wait=wait_exponential(multiplier=2, min=10, max=60), stop=stop_after_attempt(5))
    def llamar_a_gemini(self, chat, mensaje):
        return chat.send_message(mensaje)

    # Este es el método que llamarán los otros agentes
    def verificar_noticia(self,instruccion: str):

        # El chat se crea internamente y se destruye al terminar la tarea (stateless)
        # o puedes mantenerlo en self si quieres que tenga memoria entre llamadas.
        chat = self.client.chats.create(model=self.model_id, config=self.config)
        response = chat.send_message(instruccion)

        # Bucle interno de herramientas (el "cerebro" del trabajador)
        for _ in range(5):
            calls = [p.function_call for p in response.candidates[0].content.parts if p.function_call]
            if not calls:
                break

            tool_responses = []
            for call in calls:
                # Ejecución de la lógica de negocio
                result = self.funcs[call.name].invoke(call.args)
                tool_responses.append(types.Part.from_function_response(
                    name=call.name,
                    response={'result': result}
                ))

            response = chat.send_message(tool_responses)
        # MODIFICADO: Convertimos el texto JSON de Gemini en un diccionario de Python
        import json
        try:
            return json.loads(response.text)
        except:
            # Fallback por si algo falla
            return {
                "verificado": False, 
                "confianza": 0, 
                "fuentes_consultadas": 0, 
                "explicacion": response.text
            }

        return response.text
