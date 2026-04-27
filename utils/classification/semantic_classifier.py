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
        "¿puedes abrir el informe final en formato word?",
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
        "traduce este fragmento de literatura a sistema braille",
        "pasa esta frase de mi libro a braille",
        "¿cómo se escribe mi nombre en puntos braille?",
        "convierte este texto universitario a braille",
        "traducir este párrafo de cuento al braille, por favor",
        "generar la versión en braille de este poema clásico",
        "transcribir este manual técnico al sistema braille",
        "pasar esta lectura a formato braille para impresión",
        "traducir esta frase a braille",
        "traducir este teorema matemático al sistema braille"        
    ]
}

confidence_treholds = {
    "agregar_documento": 0.0,
    "acceder_documento": 0.0,
    "buscar_catalogo": 0.0,
    "traducir": 0.8,
    "fallback": 0.0
}

model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

intent_embeddings = {}

for intent_name, phrases in task_intents.items():
    normalized_intents = [normalize_text(phrase) for phrase in phrases]
    print(f"el tipo de normalized intents: {type(normalized_intents[0])}")
    intent_embeddings[intent_name] = model.encode(normalized_intents)

def classify(user_query: str):
    normalized_input = normalize_text(user_query)

    input_sentence = normalized_input
    input_embeddings = model.encode([input_sentence])

    similarities = {}
    prev_top_score = None
    top_intent = None

    for intent_name, intents in intent_embeddings.items():
        similarities[intent_name] = model.similarity(input_embeddings, intents)

    for intent_name in similarities.keys():
        current_score = similarities[intent_name].max()
        current_intent = intent_name

        if prev_top_score == None:
            prev_top_score = current_score
            top_intent = current_intent
        else:         
            if current_score > prev_top_score:
                prev_top_score = current_score
                top_intent = intent_name
    
    print(prev_top_score, top_intent)

    # this is where a value is return, maybe a string so i can match it from main for executing
    if prev_top_score > confidence_treholds[top_intent]:
        res = {
            "intent": top_intent,
            "confidence": prev_top_score.item()
        }

        print(res)

        return res
    elif prev_top_score > confidence_treholds[intent_name] - 0.2:
        # ask clarification: is this what you wanted to do?
        pass
    else:
        # reprompt
        pass
