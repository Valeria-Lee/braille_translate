# Aqui va la pequena clasificacion de tareas por keywords y asi

KEYWORDS = {
    "acceso_directo": {
        "leer": 1,
        "ir": 1,
        "seguir": 2,
        "mitad": 3,
        "continuar": 3,
        "acceder": 3,
        "libro": 3,
        "archivo": 3,
        "documento": 3,
        "que se llama": 5,
        "quiero acceder a un libro que deje a la mitad": 5,
        "quiero seguir leyendo un libro que deje a la mitad": 5,
    },
    "agregar_archivo": {
        "cargar": 1,
        "adjuntar": 1,
        "meter": 1,
        "poner": 1,
        "doc": 1,
        "documento": 2,
        "añadir": 3,
        "agregar": 3,
        "subir": 3,
        "añadir un libro": 5,
        "añadir el archivo": 5,
        "agregar mi libro": 5,
        "subir mi archivo": 5,
        "web": -3,
    },
    "repetir_comando": {
        "renglon": 1,
        "línea": 3,
        "repetir": 3,
        "decir": 3,
        "de nuevo": 3,
        "ultimos caracteres": 4,
        "otra vez": 5,
        "decirlo de nuevo": 5,
        "volver a decir": 5,
        "libro": -2,
        "buscar": -4,
        "que se llama": -5,
    },
    "busqueda_web": {
        "navegar": 1,
        "buscar": 1,
        "mejores": 1,
        "hoy": 1,
        "que": 1,
        "web": 3,
        "como es": 3,
        "internet": 3,
        "buscar": 4,
        "quiero saber": 5,
        "quiero buscar": 5,
        "que es": 5,
        "cuando es": 5,
        "libro": -2,
        "titulo": -3,
        "biblioteca": -3,
    }
}

def normalize(text: str):
    # TODO: Elimina acentos y convierte a minusculas
    text = text.lower()

def classification_engine(text: str):
    normalize(text)
    scores = {
        "acceso_directo": 0,
        "agregar_archivo": 0,
        "repetir_comando": 0,
        "busqueda_web": 0
        }

    for task, words in KEYWORDS.items():
        score = 0
        for word, cost in words.items():
            if word in text:
                score += cost
        scores[task] = score
    
    print(scores)

    # TODO: find the biggest value in the dictionary and return the assigned "task"

classification_engine("navegar a libro que se llama tal")