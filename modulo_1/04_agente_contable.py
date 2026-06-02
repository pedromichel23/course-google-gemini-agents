import os
from google import genai
from google.genai import types

client = genai.Client()

# 1. Definimos el esquema de salida usando los tipos oficiales del SDK
# Queremos que el agente nos devuelva un objeto con 3 campos específicos
esquema_fiscal = types.Schema(
    type=types.Type.OBJECT,
    properties={
        "razonamiento": types.Schema(
            type=types.Type.STRING,
            description="El análisis paso a paso de por qué el gasto es o no indispensable para un desarrollador."
        ),
        "concepto_limpio": types.Schema(
            type=types.Type.STRING,
            description="El nombre del producto o servicio simplificado (ej: 'Servidores', 'Hardware')."
        ),
        "iva_acreditable": types.Schema(
            type=types.Type.BOOLEAN,
            description="True si el IVA se puede deducir, False si no cumple con los criterios de RESICO."
        ),
    },
    # Forzamos a que el modelo obligatoriamente tenga que llenar estos 3 campos
    required=["razonamiento", "concepto_limpio", "iva_acreditable"],
)

# 2. Configuramos el agente para que adopte el modo JSON
PROMPT_SISTEMA = """
Eres un Agente Auditor Fiscal experto en el régimen RESICO en México. 
Analiza el concepto del gasto del usuario enfocado en la actividad de Desarrollo de Software.
"""

configuracion_agente = types.GenerateContentConfig(
    system_instruction=PROMPT_SISTEMA,
    temperature=0.0,
    # REGLAS CRUCIALES PARA EL MÓDULO 1.4:
    response_mime_type="application/json", # Le decimos que responda en JSON
    response_schema=esquema_fiscal         # Le pasamos el molde que creamos arriba
)

print("🚀 Enviando gasto para auditoría estructurada...")
gasto_recibido = "Concepto: Licencia anual de GitHub Copilot Enterprise para el equipo de desarrollo"

response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents=gasto_recibido,
    config=configuracion_agente
)

# 3. Imprimimos el resultado directo
print("\n💻 Salida JSON pura generada por la IA:")
print(response.text)