import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

client = genai.Client()

# 1. Definimos la FUNCIÓN REAL en Python (Lo que correrá en nuestra máquina)
def verificar_rfc_sat(rfc: str) -> dict:
    """Esta función simula una consulta a las bases de datos del SAT."""
    # En el futuro, aquí irá código real que conecte a una API o base de datos.
    rfc = rfc.upper().strip()
    
    # Simulación de lógica de negocio determinista
    if rfc.startswith("XAXX"):
        return {"estatus": "VALIDO", "tipo": "Público en General", "lista_negra": False}
    elif rfc == "BAD991231AAA":
        return {"estatus": "INVALIDO", "tipo": "Inexistente", "lista_negra": True}
    else:
        return {"estatus": "VALIDO", "tipo": "Persona Física (RESICO/Sueldos)", "lista_negra": False}


# 2. Creamos la DECLARACIÓN para la IA (El mapa que lee Gemini)
declaracion_verificar_rfc = types.FunctionDeclaration(
    name="verificar_rfc_sat",
    description="Consulta el padrón del SAT para verificar si un RFC es válido y si se encuentra en la lista negra de EFOS/EDOS.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "rfc": types.Schema(
                type=types.Type.STRING,
                description="El RFC de 12 o 13 caracteres que se desea verificar (ej: 'VECJ880326XXX')."
            ),
        },
        required=["rfc"],
    ),
)

# 3. Empaquetamos la herramienta dentro del objeto Tools
caja_de_herramientas = types.Tool(
    function_declarations=[declaracion_verificar_rfc]
)

# 4. Configuramos el agente pasándole las herramientas disponibles
configuracion = types.GenerateContentConfig(
    system_instruction="Eres un asistente fiscal. Si el usuario te da un RFC, debes verificarlo usando tus herramientas antes de dar un diagnóstico.",
    temperature=0.0,
    tools=[caja_de_herramientas] # Le damos acceso a la caja de herramientas
)

print("⚡ Enviando consulta al agente...")

response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents="Hola, necesito saber si el RFC 'BAD991231AAA' es seguro para facturarle.",
    config=configuracion
)

# Vamos a inspeccionar qué nos devolvió el modelo
print("\n🔍 ¿El modelo llamó a una función?")
if response.function_calls:
    for call in response.function_calls:
        print(f"La IA quiere ejecutar la función: -> {call.name}")
        print(f"Con los siguientes argumentos:    -> {call.args}")
else:
    print("La IA decidió no usar herramientas y respondió con texto:")
    print(response.text)