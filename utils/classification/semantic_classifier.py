from sentence_transformers import SentenceTransformer
from preprocess_text import normalize_text

task_intents = {
    "agregar_documento": [
        "subir este archivo al sistema",
        "quiero guardar un nuevo documento",
        "cargar un nuevo libro de texto",
        "importar este artículo a mi biblioteca",
        "añadir un nuevo registro documental",
        "cargar documento nuevo para procesar",
        "sube este PDF a mi colección personal",
        "adjuntar archivo de investigación"
    ],
    "acceder_documento": [
        "abrir el libro que estaba leyendo ayer",
        "necesito ver el documento seleccionado",
        "muéstrame el archivo de la tarea",
        "acceder a mis lecturas guardadas",
        "¿puedes abrir el informe final en formato Word?",
        "quiero visualizar el PDF de referencia",
        "abrir el documento de apuntes",
        "leer el archivo guardado anteriormente"
    ],
    "buscar_catalogo": [
        "¿qué libros hay disponibles sobre ingeniería civil?",
        "busca el documento de investigación de la semana pasada",
        "quiero ver el catálogo de cuentos infantiles",
        "lista todos los libros de cálculo y matemáticas",
        "¿tienen algún documento sobre microcontroladores en la base de datos?",
        "explorar la sección de literatura clásica",
        "buscar cuentos de misterio y leyendas",
        "mostrar el inventario de libros de historia universal"
    ],
    "traducir": [
        "traduce este fragmento de literatura a sistema Braille",
        "pasa esta frase de mi libro a Braille",
        "¿cómo se escribe mi nombre en puntos Braille?",
        "convierte este texto universitario a Braille",
        "traducir este párrafo de cuento al Braille, por favor",
        "generar la versión en Braille de este poema clásico",
        "transcribir este manual técnico al sistema Braille",
        "pasar esta lectura a formato Braille para impresión"
    ]
}

"""
if best_score > 0.80:
    execute(intent)
elif best_score >s 0.60:
    ask_for_clarification()
else:
    ignore_or_reprompt()
"""

# TODO: add confidence thresold, and text normalization

model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

def classify(user_query: str):
    intent_embeddings = {}

    for intent_name, phrases in task_intents.items():
        intent_embeddings[intent_name] = model.encode(phrases)

    input_sentence = user_query
    input_embeddings = model.encode(input_sentence)

    similarities = {}
    prev_top_score = None
    top_intent = None

    for intent_name, intents in intent_embeddings.items():
        similarities[intent_name] = model.similarity(input_embeddings, intents)

    print(similarities)

    # loop through it to get max value per intent and intent name
    for intent_name in similarities.keys():
        if prev_top_score == None:
            top_score = similarities[intent_name].max()
            prev_top_score = top_score
            top_intent = intent_name
        else:    
            current_score = similarities[intent_name].max()
            
            if current_score > prev_top_score:
                prev_top_score = current_score
                top_intent = intent_name
    
    print(prev_top_score, top_intent)

classify("Hola, como estas? Esto es una oracion, supongo.")