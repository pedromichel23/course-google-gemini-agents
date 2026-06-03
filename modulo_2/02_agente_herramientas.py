import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()
client = genai.Client()

# ==========================================
# 1. NUESTRA CAJA DE HERRAMIENTAS (Igual a 2.1)
# ==========================================

def verificar_rfc_sat(rfc: str) -> dict:
    rfc = rfc.upper().strip()
    if rfc.startswith("XAXX"):
        return {"estatus": "VALIDO", "tipo": "Público en General", "lista_negra": False}
    elif rfc == "BAD991231AAA":
        return {"estatus": "INVALIDO", "tipo": "Inexistente", "lista_negra": True}
    else:
        return {"estatus": "VALIDO", "tipo": "Persona Física", "lista_negra": False}

declaracion_verificar_rfc = types.FunctionDeclaration(
    name="verificar_rfc_sat",
    description="Consulta el padrón del SAT para verificar si un RFC es válido y si está en lista negra.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "rfc": types.Schema(type=types.Type.STRING, description="RFC a verificar.")
        },
        required=["rfc"],
    ),
)

caja_de_herramientas = types.Tool(function_declarations=[declaracion_verificar_rfc])

configuracion = types.GenerateContentConfig(
    system_instruction="Eres un asistente fiscal experto. Usa tus herramientas para validar RFCs antes de dar diagnósticos.",
    temperature=0.0,
    tools=[caja_de_herramientas]
)

# ==========================================
# 2. PRIMERA LLAMADA: El usuario hace la pregunta
# ==========================================
print("⚡ [Usuario]: Hola, necesito saber si el RFC 'BAD991231AAA' es seguro.")

# Guardamos el mensaje inicial en un historial de chat que compartiremos con la IA
historial_chat = [
    types.Content(role="user", parts=[types.Part.from_text(text="Hola, necesito saber si el RFC 'BAD991231AAA' es seguro.")])
]

response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents=historial_chat,
    config=configuracion
)

# ==========================================
# 3. INTERCEPCIÓN Y EJECUCIÓN LOCAL (Módulo 2.2)
# ==========================================
if response.function_calls:
    # Añadimos la respuesta de la IA (su solicitud de función) al historial de la conversación
    historial_chat.append(response.candidates[0].content)
    
    for call in response.function_calls:
        print(f"🤖 [IA]: Necesito usar la herramienta '{call.name}' con datos: {call.args}")
        
        # Validación de qué función quiere correr la IA
        if call.name == "verificar_rfc_sat":
            # Extraemos el argumento que calculó la IA de forma segura
            rfc_argumento = call.args["rfc"]
            
            # EJECUCIÓN REAL de nuestra función nativa de Python en nuestra máquina
            resultado_funcion_real = verificar_rfc_sat(rfc=rfc_argumento)
            print(f"💻 [Backend]: Ejecutando función local... Resultado obtenido: {resultado_funcion_real}")
            
            # ==========================================
            # 4. EL CALLBACK: Enviar el resultado de vuelta (Módulo 2.3)
            # ==========================================
            
            # Construimos un objeto de tipo FunctionResponse con el JSON que arrojó nuestra función
            respuesta_para_ia = types.Content(
                role="tool", # Rol especial que indica que es el resultado de una herramienta
                parts=[
                    types.Part.from_function_response(
                        name=call.name,
                        response=resultado_funcion_real # El diccionario de Python
                    )
                ]
            )
            # Metemos el resultado al historial para que la IA se entere
            historial_chat.append(respuesta_para_ia)

    print("\n🔄 Enviando resultados de vuelta a Gemini para el veredicto final...")
    
    # Hacemos la SEGUNDA LLAMADA pasándole todo el historial acumulado
    final_response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=historial_chat,
        config=configuracion
    )
    
    print("\n💬 [Asistente Fiscal]:")
    print(final_response.text)

else:
    print("\n💬 [Asistente Fiscal]:")
    print(response.text)