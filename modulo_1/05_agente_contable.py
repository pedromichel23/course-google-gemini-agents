import os
from google import genai
from google.genai import types

client = genai.Client()

# 1. EL MOLDE (JSON Schema): Unimos el formato con la cognición (CoT)
esquema_auditoria_dev = types.Schema(
    type=types.Type.OBJECT,
    properties={
        # Este campo obliga al modelo a usar Chain-of-Thought dentro del JSON
        "cadena_de_pensamiento": types.Schema(
            type=types.Type.STRING,
            description="Paso 1: Identificar el uso en desarrollo de software. Paso 2: Evaluar si el SAT lo considera deducible para esta actividad. Paso 3: Conclusión."
        ),
        "categoria_gasto": types.Schema(
            type=types.Type.STRING,
            description="Categoría limpia del gasto (ej: 'Infraestructura', 'Hardware', 'Suscripciones', 'No Deducible')."
        ),
        "iva_acreditable": types.Schema(
            type=types.Type.BOOLEAN,
            description="True si el desarrollador puede restar este IVA en su declaración mensual, False si no."
        )
    },
    required=["cadena_de_pensamiento", "categoria_gasto", "iva_acreditable"]
)

# 2. LAS REGLAS Y LOS EJEMPLOS (Prompt + Few-Shot)
PROMPT_SISTEMA_DEV = """
Eres un Agente Fiscal automatizado para programadores y desarrolladores de software bajo el régimen RESICO en México.
Tu trabajo es decidir si un gasto califica para el acreditamiento de IVA.

EJEMPLO GUIADO (Few-Shot en formato JSON):
Usuario: "Concepto: Licencia mensual de OpenAI API para el entorno de staging"
Asistente: {
    "cadena_de_pensamiento": "Paso 1: El desarrollador usa la API de OpenAI para integrar funciones de IA en sus apps. Paso 2: Es un insumo tecnológico directo de producción. Paso 3: El gasto es estrictamente indispensable.",
    "categoria_gasto": "Infraestructura / APIs",
    "iva_acreditable": true
}
"""

configuracion_agente = types.GenerateContentConfig(
    system_instruction=PROMPT_SISTEMA_DEV,
    temperature=0.0, # Determinismo puro, sin espacio a la creatividad matemática
    response_mime_type="application/json",
    response_schema=esquema_auditoria_dev
)

# 3. EL CASO DE PRUEBA COMPLEJO
# ¿Qué pasa si un programador compra una silla costosa alegando que es para su oficina?
print("💻 Agente Dev listo. Analizando caso complejo de hardware/ergonomía...")
gasto_dev = "Concepto: Silla de oficina ergonómica Herman Miller Aeron para el escritorio principal"

response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents=gasto_dev,
    config=configuracion_agente
)

print("\n📊 Estructura JSON final recibida de la IA:")
print(response.text)