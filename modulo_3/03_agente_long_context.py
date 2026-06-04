import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()
client = genai.Client()

# 1. SIMULACIÓN DE UN DOCUMENTO EXTENSO (Imagina que este texto mide miles de líneas)
# Metemos datos perdidos deliberadamente en la inmensidad del texto para probar la retención de la IA.
DOCUMENTO_EXTENSO_FISCAL = """
ESTE ES EL MANUAL DE OPERACIONES FISCALES DE LA CLÍNICA DENTAL - VERSIÓN 2026
[... Cientos de líneas de texto simuladas sobre normativas de salud ...]
Sección administrativa 12: Los gastos de mantenimiento del compresor de aire dental son deducibles al 100%.
[... Más texto de relleno normativo ...]
Sección de transportación 45: Los gastos de gasolina para la camioneta de traslado de equipo clínico se acreditan al 100% de IVA siempre que se pague con tarjeta de servicio.
[... Cientos de líneas más de texto sobre higiene y permisos de COFEPRIS ...]
NOTA OCULTA EN LA PÁGINA 400: El código secreto de acceso exclusivo para la auditoría interna del sistema de facturación es 'DELTA-99-ALPHA'.
[... Fin del documento ...]
"""

# 2. CONFIGURACIÓN DEL PROMPT DE SISTEMA
# Le damos el documento completo directamente en la instrucción del sistema o en los contenidos.
PROMPT_SISTEMA_CONTEXTO_LARGO = f"""
Eres el Auditor General de la clínica. Tienes acceso al Manual de Operaciones Fiscales Completo de la empresa.
Debes responder de forma fulminante y exacta basándote en la totalidad del documento proveído abajo.

MANUAL COMPLETO:
{DOCUMENTO_EXTENSO_FISCAL}
"""

configuracion = types.GenerateContentConfig(
    system_instruction=PROMPT_SISTEMA_CONTEXTO_LARGO,
    temperature=0.0
)

# 3. CONSULTA DE UNA AGUJA EN EL PAJAR
# Le preguntamos por un dato hiper-específico que estaba enterrado en el fondo del texto.
pregunta_seguridad = "¿Cuál es el código secreto de acceso para la auditoría interna del sistema de facturación?"
print(f"⚡ [Usuario]: {pregunta_seguridad}")

print("🧠 Gemini está analizando el documento masivo en su ventana de contexto...")
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents=pregunta_seguridad,
    config=configuracion
)

print("\n💬 [Auditor Interno]:")
print(response.text)