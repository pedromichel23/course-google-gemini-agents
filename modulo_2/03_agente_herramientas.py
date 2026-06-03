import os
import json
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()
client = genai.Client()

# =====================================================================
# 1. DEFINICIÓN DE HERRAMIENTAS (Simulando operaciones del SAT)
# =====================================================================

def descargar_facturas_mes(mes: str) -> dict:
    """Descarga paquetes de CFDI (XML) desde el Web Service del SAT para un mes específico."""
    print(f"   ⚙️ [Herramienta Ejecutada]: Descargando XMLs de {mes}...")
    # Simulamos que encontramos un archivo de ingresos y uno de gastos
    return {
        "status": "Descarga Exitosa",
        "archivos_encontrados": ["ingreso_factura1.xml", "gasto_internet.xml"]
    }

def parsear_y_sumar_xmls(lista_archivos: list) -> dict:
    """Abre una lista de archivos XML del SAT, extrae y suma los montos de ingresos y el IVA de gastos."""
    print(f"   ⚙️ [Herramienta Ejecutada]: Extrayendo datos de {lista_archivos}...")
    # Simulamos los datos reales extraídos de los XML
    return {
        "ingresos_subtotal_pue": 45000.00, # Lo efectivamente cobrado
        "iva_gastos_indispensables": 1200.00, # IVA de gastos que restaremos
        "retenciones_isr_pm": 0.00
    }

# 2. DECLARACIONES PARA GEMINI
decl_descargar = types.FunctionDeclaration(
    name="descargar_facturas_mes",
    description="Descarga los XMLs del SAT para el mes solicitado.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={"mes": types.Schema(type=types.Type.STRING, description="Mes del año (ej: 'Mayo')")},
        required=["mes"]
    )
)

decl_parsear = types.FunctionDeclaration(
    name="parsear_y_sumar_xmls",
    description="Toma una lista de nombres de archivos XML y extrae la suma de ingresos e IVA de gastos.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "lista_archivos": types.Schema(
                type=types.Type.ARRAY, 
                items=types.Schema(type=types.Type.STRING),
                description="Lista de archivos XML a procesar."
            )
        },
        required=["lista_archivos"]
    )
)

caja_herramientas = types.Tool(function_declarations=[decl_descargar, decl_parsear])

# 3. PROMPT CON REGLAS DE RECONOCIMIENTO Y LÓGICA DE NEGOCIO
PROMPT_SISTEMA_RESICO = """
Eres un Agente Contable Autónomo para desarrolladores en RESICO México.
Tu objetivo es calcular los impuestos mensuales.

Reglas matemáticas deterministas que debes dictaminar:
- La tasa de ISR para ingresos de $45,000 mensuales en RESICO es del 1.1%. (Impuesto = Ingresos * 0.011).
- Debes informar al usuario el total de ingresos, el ISR a pagar, y el IVA de gastos recuperable.

Utiliza tus herramientas de forma secuencial: Primero descarga, luego parsea los archivos obtenidos.
"""

configuracion = types.GenerateContentConfig(
    system_instruction=PROMPT_SISTEMA_RESICO,
    temperature=0.0,
    tools=[caja_herramientas]
)

# Mapeo de nombres a funciones reales de Python para ejecución dinámica
HERRAMIENTAS_DISPONIBLES = {
    "descargar_facturas_mes": descargar_facturas_mes,
    "parsear_y_sumar_xmls": parsear_y_sumar_xmls
}

# =====================================================================
# 4. EL BUCLE AUTÓNOMO (Patrón ReAct)
# =====================================================================

historial_chat = [
    types.Content(role="user", parts=[types.Part.from_text(text="Hola, calcula mis impuestos del mes de Mayo por favor.")])
]

print("🚀 Iniciando bucle autónomo del agente...")
ciclo = 1

while True:
    print(f"\n🔄 --- Ciclo de Razonamiento #{ciclo} ---")
    
    # Llamamos a Gemini enviando el historial acumulado
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=historial_chat,
        config=configuracion
    )
    
    # SI LA IA DECIDE QUE NECESITA USAR HERRAMIENTAS
    if response.function_calls:
        # Guardamos la intención de la IA en el historial
        historial_chat.append(response.candidates[0].content)
        
        for call in response.function_calls:
            print(f"🤔 [IA piensa]: Requiero usar '{call.name}' con parámetros: {call.args}")
            
            # Ejecución dinámica de la herramienta seleccionada por la IA
            funcion_ejecutar = HERRAMIENTAS_DISPONIBLES[call.name]
            # Pasamos los argumentos desempaquetados usando **
            resultado_local = funcion_ejecutar(**call.args) 
            
            # Estructuramos la respuesta de la herramienta para inyectarla al historial
            respuesta_tool = types.Content(
                role="tool",
                parts=[types.Part.from_function_response(name=call.name, response=resultado_local)]
            )
            historial_chat.append(respuesta_tool)
            
        ciclo += 1
        continue # Volvemos a iniciar el ciclo 'while' para que la IA analice el resultado de la herramienta
        
    # SI LA IA YA NO NECESITA HERRAMIENTAS, SIGNIFICA QUE TERMINÓ SU TRABAJO
    else:
        print("\n🏁 [IA]: He terminado de recolectar datos y procesar la información.")
        print("\n💬 [Respuesta Final del Agente]:")
        print(response.text)
        break # Rompemos el bucle infinito exitosamente