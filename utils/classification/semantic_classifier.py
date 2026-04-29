from utils.classification.preprocess_text import normalize_text
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

task_intents = {
    "agregar_documento": [
        "subir este archivo al sistema",
        "quiero guardar un nuevo documento",
        "cargar un nuevo libro de texto",
        "importar este artículo a mi biblioteca",
        "añadir un nuevo registro documental",
        "cargar documento nuevo para procesar",
        "sube este PDF a mi colección personal",
        "adjuntar archivo de investigación",
        "súbete esta tarea a la nube",
        "pon este documento en mi carpeta",
        "anexar este reporte al sistema",
        "registrar nuevo archivo en mi cuenta",
        "métele este archivo al sistema",
        "ándale sube este PDF ahorita",
        "voy a subir un archivo nuevo",
        "échale este documento a mi cuenta",
        "agarra este archivo y guárdalo",
        "mete este libro a mi biblioteca",
        "ayúdame a subir este documento",
        "ya estuvo, súbelo a mi carpeta",
        "pérate, voy a cargar este archivo",
        "dale y sube este PDF a mi colección",
        "subir", "cargar", "guardar", "importar", "adjuntar", "añadir",
        "registrar", "meter", "agregar",
    ],
    "acceder_documento": [
        "abrir el libro que estaba leyendo ayer",
        "necesito ver el documento seleccionado",
        "muéstrame el archivo de la tarea",
        "acceder a mis lecturas guardadas",
        "¿puedes abrir el informe final en formato word?",
        "quiero visualizar el PDF de referencia",
        "abrir el documento de apuntes",
        "leer el archivo guardado anteriormente",
        "échame la mano abriendo el PDF de ayer",
        "ponme en pantalla mi lectura actual",
        "continuar leyendo mi libro",
        "recuperar mi lectura guardada",
        "ábrete el informe que guardé",
        "ábreme el documento ese que guardé ayer",
        "jálame el archivo que tenía abierto",
        "ahorita quiero ver mi lectura de ayer",
        "órale, ábrelo ya",
        "sácame el libro que estaba checando",
        "no encuentro mi documento, ábrelo tú",
        "dale, ponme el libro ese en pantalla",
        "pérate, primero ábrelo que lo quiero leer",
        "ya estuvo, muéstrame el informe",
        "abrir", "leer", "visualizar", "acceder", "ver", "mostrar",
        "recuperar", "continuar", "reanudar",
    ],
    "buscar_catalogo": [
        "¿qué libros hay disponibles sobre ingeniería civil?",
        "busca el documento de investigación de la semana pasada",
        "quiero ver el catálogo de cuentos infantiles",
        "lista todos los libros de cálculo y matemáticas",
        "¿tienen algún documento sobre microcontroladores en la base de datos?",
        "explorar la sección de literatura clásica",
        "buscar cuentos de misterio y leyendas",
        "mostrar el inventario de libros de historia universal",
        "busca artículos sobre termodinámica",
        "¿qué archivos nuevos hay en el catálogo?",
        "chécate si hay libros de redes en la lista",
        "dame una lista de los libros disponibles",
        "a ver qué libros de física hay por ahí",
        "oye, ¿hay algo de programación en el catálogo?",
        "¿qué tienen de novelas de terror?",
        "busca algo de química pa mi tarea",
        "¿hay libros de historia en el inventario o no?",
        "¿qué hay en el catálogo de matemáticas?",
        "¿tienen algo sobre la historia de Campeche?",
        "dale, chécame si hay libros de cultura",
        "¿habrá algo de leyendas en el catálogo?",
        "pérate, busca si tienen cuentos",
        "buscar", "explorar", "listar", "checar", "consultar",
        "mostrar catálogo", "ver disponibles", "encontrar",
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
        "traducir este teorema matemático al sistema braille",
        "échame la mano traduciendo esto a braille",
        "cámbiame esta frase a puntos braille",
        "sácame la versión en braille de esta fábula",
        "¿cómo se pone este teorema en braille?",
        "pásame este texto a braille ahorita",
        "órale, conviérteme esto a puntos braille",
        "necesito que me lo pongas en braille ya",
        "¿puedes pasarme este párrafo a braille?",
        "¿cómo se escribe esto en braille?",
        "dale, pásame esta leyenda a braille",
        "pérate, conviérteme este texto a braille",
        "ya estuvo, tradúceme esto a puntos braille",
        "traducir", "convertir", "transcribir", "pasar a braille",
        "transformar", "cambiar a braille", "generar braille",
    ],
}

confidence_treholds = {
    "agregar_documento": 0.15,
    "acceder_documento": 0.15,
    "buscar_catalogo": 0.15,
    "traducir": 0.15,
}

all_phrases = []
phrase_labels = []

for intent_name, phrases in task_intents.items():
    for phrase in phrases:
        all_phrases.append(normalize_text(phrase))
        phrase_labels.append(intent_name)

vectorizer = TfidfVectorizer()
vectors = vectorizer.fit_transform(all_phrases)

def classify(user_query: str):
    normalized_input = normalize_text(user_query)

    input_sentence = normalized_input
    
    input_embeddings = vectorizer.transform([input_sentence])

    similarities = {}
    prev_top_score = None
    top_intent = None

    for intent_name, intents in intent_embeddings.items():
        similarities[intent_name] = cosine_similarity(input_embeddings, intents)

        indices = [i for i, l in enumerate(phrase_labels) if l == intent_name]
        similarities[intent_name] = cosine_similarity(input_embeddings, vectors[indices])

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

    if prev_top_score > confidence_treholds[top_intent]:
        return {
            "intent": top_intent,
            "confidence": prev_top_score.item()
        }
    elif prev_top_score > confidence_treholds[intent_name] - 0.2:
        return {
            "intent": "clarification",
            "possible_item": top_intent,
            "confidence": prev_top_score.item()
        }
    else:
        return {
            "intent": "fallback",
            "confidence": prev_top_score.item()
        }
