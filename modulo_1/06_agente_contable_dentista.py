import os
from google import genai
from google.genai import types

client = genai.Client()

# 1. ESQUEMA: Obligamos al JSON a incluir el "Razonamiento" como un campo de texto
esquema_avanzado = types.Schema(
    type=types.Type.OBJECT,
    properties={
        # Aquí vive el Chain-of-Thought dentro del JSON
        "cadena_de_pensamiento": types.Schema(
            type=types.Type.STRING,
            description="Analiza primero la actividad del dentista, luego evalúa si el concepto es indispensable y finalmente justifica tu decisión."
        ),
        "iva_acreditable": types.Schema(
            type=types.Type.BOOLEAN,
            description="True si pasa la auditoría de deducibilidad, False de lo contrario."
        )
    },
    required=["cadena_de_pensamiento", "iva_acreditable"]
)

# 2. PROMPT: Usamos Few-Shot para enseñarle cómo llenar el JSON correctamente
PROMPT_SISTEMA_MIXTO = """
Eres un Agente Auditor Fiscal para dentistas en México. 
Analiza el gasto y devuelve la respuesta estrictamente en el formato JSON requerido.

EJEMPLO GUIADO (Few-Shot en formato JSON):
Usuario: "Concepto: Compra de una pieza de mano de alta velocidad NSK"
Asistente: {
    "cadena_de_pensamiento": "1. Actividad: Dentista requiere herramientas para remover caries. 2. Análisis: La pieza de mano es el taladro dental básico para operar. 3. Conclusión: Es estrictamente indispensable.",
    "iva_acreditable": true
}
"""

configuracion_agente = types.GenerateContentConfig(
    system_instruction=PROMPT_SISTEMA_MIXTO,
    temperature=0.0,
    response_mime_type="application/json",
    response_schema=esquema_avanzado # Forzamos la estructura
)

# 3. EVALUACIÓN DE UN CASO COMPLEJO (Gasto personal metido en la clínica)
print("🦷 Evaluando caso ambiguo...")
gasto_dudoso = "Concepto: Compra de 3 paquetes de café gourmet en grano y una cafetera de cápsulas Nespresso"

response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents=gasto_dudoso,
    config=configuracion_agente
)

print(response.text)