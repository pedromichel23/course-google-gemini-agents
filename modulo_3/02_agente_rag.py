import os
from google import genai
from google.genai import types
import chromadb
from dotenv import load_dotenv

load_dotenv()
client = genai.Client()

# 1. INICIALIZACIÓN E INDEXACIÓN (Igual al paso anterior, pero con el modelo correcto)
chroma_client = chromadb.EphemeralClient()
coleccion_sat = chroma_client.create_collection(name="ley_sat_resico")

documentos_fiscales = [
    "Artículo 113-E LISR: Las personas físicas que realicen actividades empresariales, profesionales u otorguen el uso o goce temporal de bienes, podrán optar por pagar el impuesto sobre la renta en el régimen RESICO, siempre que sus ingresos no excedan de 3.5 millones de pesos al año.",
    "Criterio IVA 2026: El Impuesto al Valor Agregado (IVA) cobrado por servicios de desarrollo de software exportados al extranjero (tasa 0%) permite la acreditación del IVA pagado en gastos indispensables de operación local.",
    "Regla de Deducciones Generales: Los gastos médicos, dentales y hospitalarios son deducciones personales anuales aplicables para sueldos y salarios, pero NO son aplicables mensualmente en el régimen RESICO."
]

# Generamos los embeddings usando el modelo validado gemini-embedding-2
vectores_documentos = []
for texto in documentos_fiscales:
    embedding_response = client.models.embed_content(
        model="gemini-embedding-2",
        contents=texto
    )
    vectores_documentos.append(embedding_response.embeddings[0].values)

coleccion_sat.add(
    embeddings=vectores_documentos,
    documents=documentos_fiscales,
    ids=[f"id_ley_{i}" for i in range(len(documentos_fiscales))]
)

# =====================================================================
# 2. EL FLUJO RAG: PREGUNTA -> BUSQUEDA -> PROMPT -> RESPUESTA
# =====================================================================

# Pregunta compleja del usuario
pregunta_usuario = "Hola, soy programador y exporto software a USA. ¿Qué onda con mi IVA de los gastos de aquí de México?"
print(f"⚡ [Usuario]: {pregunta_usuario}")

# Paso A: Generar el embedding de la pregunta
embedding_pregunta = client.models.embed_content(
    model="gemini-embedding-2",
    contents=pregunta_usuario
)
vector_pregunta = embedding_pregunta.embeddings[0].values

# Paso B: Recuperar (Retrieve) el fragmento de la ley más cercano en ChromaDB
resultados_busqueda = coleccion_sat.query(
    query_embeddings=[vector_pregunta],
    n_results=1
)
documento_recuperado = resultados_busqueda['documents'][0][0]
print(f"📥 [RAG]: Fragmento legal recuperado de la Base Vectorial: '{documento_recuperado[:40]}...'")

# Paso C: Inyección de Contexto (Augment). Creamos un prompt blindado.
PROMPT_SISTEMA_RAG = f"""
Eres un Asistente Contable experto para desarrolladores de software en México.
Tu tarea es responder la duda del usuario utilizando ÚNICAMENTE el fragmento de la ley proveído en el bloque de CONTEXTO LEGAL.

CONTEXTO LEGAL:
\"\"\"
{documento_recuperado}
\"\"\"

Reglas estrictas:
1. Responde de forma clara, profesional y directa.
2. Si la respuesta no se puede deducir del CONTEXTO LEGAL, di amablemente: 'Lo siento, no cuento con esa información en mi base de datos fiscal'. No inventes nada fuera del contexto.
"""

configuracion_agente = types.GenerateContentConfig(
    system_instruction=PROMPT_SISTEMA_RAG,
    temperature=0.0 # Determinismo total
)

# Paso D: Generar respuesta (Generate)
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents=pregunta_usuario,
    config=configuracion_agente
)

print("\n💬 [Asistente Fiscal - Respuesta con RAG]:")
print(response.text)