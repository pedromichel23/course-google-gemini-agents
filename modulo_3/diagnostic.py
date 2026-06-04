import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
client = genai.Client()

print("🔍 Consultando la lista oficial de modelos con el nuevo SDK...")

# Listamos todos los modelos disponibles
for model in client.models.list():
    # Usamos el atributo correcto de Pydantic: supported_actions
    if model.supported_actions and 'embedContent' in model.supported_actions:
        print(f"✅ Modelo: {model.name}")
        print(f"   Nombre para código: {model.name.split('/')[-1]}")
        print(f"   Descripción: {model.description}\n")