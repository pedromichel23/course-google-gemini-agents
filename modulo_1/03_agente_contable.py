import os
from google import genai
from google.genai import types

client = genai.Client()

#Definimos un System Instruction robusto usando Few-Shot y Chain-of-Thought
PROMPT_SISTEMA = """
Eres un Agente Auditor Fiscal experto en el régimen RESICO en México, especializado en la industria de tecnología.
Tu tarea es evaluar conceptos de facturas de gastos y determinar si el IVA es 'Acreditable' (deducible) o 'No Acreditable'.

REGLA DE CADENA DE PENSAMIENTO (Chain-of-Thought):
Antes de dar tu veredicto, debes rellenar los pasos de 'Razonamiento'. No te saltes ningún paso.

EJEMPLOS GUIADOS (Few-Shot Prompting):

Ejemplo 1:
Usuario: "Concepto: Pago mensual de servidor en Amazon Web Services (AWS)"
Asistente:
- Razonamiento: El usuario es desarrollador. Los servidores en la nube son la infraestructura básica para alojar sus aplicaciones y trabajar. Es estrictamente indispensable.
- Veredicto: ACREDITABLE

Ejemplo 2:
Usuario: "Concepto: Consumo de alimentos en restaurante El Cardenal"
Asistente:
- Razonamiento: El régimen RESICO y la ley del IVA restringen la deducción de restaurantes a menos que ocurra en un viaje de negocios a más de 50km. No hay evidencia de viaje aquí.
- Veredicto: NO ACREDITABLE
"""
# Ahora usamos types.GenerateContentConfig
configuracion_agente = types.GenerateContentConfig(
    system_instruction=PROMPT_SISTEMA,
    temperature=0.0 #Queremos total determinismo. No inventar nada, ideal para matematicas y leyes.
)

print("🤖 Agente listo. Evaluando nuevo gasto...")

# Aquí simulamos un caso nuevo que el modelo no ha visto en los ejemplos
gasto_nuevo = "Concepto: Compra de Teclado Mecánico Ergonómico marca Keychron en Amazon"

response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents=gasto_nuevo,
    config=configuracion_agente #Le pasamos nuestra configuracion.  
)

print("\n💬  Respuesta del Asistente Fiscal:")
print(response.text)