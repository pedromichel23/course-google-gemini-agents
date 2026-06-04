import os
from google import genai
from google.genai import types
import chromadb
from dotenv import load_dotenv

load_dotenv()
# Inicializamos el cliente de Gemini
client = genai.Client()

# 1. Inicializar ChromaDB en modo local (creará una base de datos en memoria para esta prueba)
chroma_client = chromadb.EphemeralClient()
# Creamos una 'colección' (equivalente a una tabla en bases de datos tradicionales)
coleccion_sat = chroma_client.create_collection(name="ley_sat_resico")

print("📦 Base de datos vectorial inicializada.")

# =====================================================================
# 2. ALIMENTAR LA BASE DE DATOS (Simulando fragmentos de leyes del SAT)
# =====================================================================
documentos_fiscales = [
    "Artículo 113-E LISR: Las personas físicas que realicen actividades empresariales, profesionales u otorguen el uso o goce temporal de bienes, podrán optar por pagar el impuesto sobre la renta en el régimen RESICO, siempre que sus ingresos no excedan de 3.5 millones de pesos al año.",
    "Criterio IVA 2026: El Impuesto al Valor Agregado (IVA) cobrado por servicios de desarrollo de software exportados al extranjero (tasa 0%) permite la acreditación del IVA pagado en gastos indispensables de operación local.",
    "Regla de Deducciones Generales: Los gastos médicos, dentales y hospitalarios son deducciones personales anuales aplicables para sueldos y salarios, pero NO son aplicables mensualmente en el régimen RESICO."
]

# Necesitamos convertir cada texto en un vector numérico usando Gemini
print("\n🧠 Generando Embeddings matemáticos con Gemini...")
vectores_documentos = []

for i, texto in enumerate(documentos_fiscales):
    # Usamos el modelo oficial de Google especializado en embeddings
    embedding_response = client.models.embed_content(
        model="gemini-embedding-2",
        contents=texto
    )
    # Extraemos la lista de números (el vector)
    vector = embedding_response.embeddings[0].values
    vectores_documentos.append(vector)

# Guardamos los textos junto con sus vectores numéricos en ChromaDB
coleccion_sat.add(
    embeddings=vectores_documentos,
    documents=documentos_fiscales,
    ids=[f"id_ley_{i}" for i in range(len(documentos_fiscales))]
)
print("✅ Documentos fiscales indexados en la base de datos vectorial.")

# =====================================================================
# 3. EL MOMENTO DE LA CONSULTA SEMÁNTICA
# =====================================================================
pregunta_usuario = "¿Puedo facturar si gano 2 millones y medio de pesos al año en el esquema simplificado?"
print(f"\n⚡ [Pregunta del Usuario]: '{pregunta_usuario}'")

# Convertimos la pregunta del usuario a embedding usando el mismo modelo
embedding_pregunta = client.models.embed_content(
        model="gemini-embedding-2",
        contents=pregunta_usuario
)
vector_pregunta = embedding_pregunta.embeddings[0].values

# Buscamos en ChromaDB los documentos más parecidos conceptualmente (n_results=1 trae el más cercano)
resultados_busqueda = coleccion_sat.query(
    query_embeddings=[vector_pregunta],
    n_results=1
)

print("\n🔍 [Resultado de la Búsqueda Vectorial Semántica]:")
print(f"Documento más relevante encontrado:\n-> {resultados_busqueda['documents'][0][0]}")