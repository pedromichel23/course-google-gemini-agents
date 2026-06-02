import os
from google import genai

client = genai.Client()
print("🤖 Enviando peticion a Gemini...")

response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents='Hola, estoy construyendo el primer agente de IA. Dame un saludo corto al estilo de un programdor senior.'   
)

print("\n💬  Respuesta de la IA:")
print(response.text)