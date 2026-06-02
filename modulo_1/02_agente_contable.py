import os
from google import genai
from google.genai import types

client = genai.Client()
# Ahora usamos types.GenerateContentConfig
configuracion_agente = types.GenerateContentConfig(
    system_instruction="Eres un asistente contable experto en el SAT de México, Solo respondes con datos fiscales reales, eres serio, directo y no usas lenguaje informal.",
    temperature=0.0 #Queremos total determinismo. No inventar nada, ideal para matematicas y leyes.
)

print("🤖 Enviando peticion con configuracion del sistema...")

response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents='¿Qué significa que una factura sea PUE en el régimen RESICO?',
    config=configuracion_agente #Le pasamos nuestra configuracion.  
)

print("\n💬  Respuesta del Asistente Fiscal:")
print(response.text)