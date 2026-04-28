import pytest
from utils.classification import semantic_classifier
# importing and module problems :v

test_cases = [
    # (input, expected_intent)
    ("Sube este archivo porfa", "agregar_documento"),
    ("Quiero guardar un nuevo documento", "agregar_documento"),
    ("Cargar un nuevo libro de texto", "agregar_documento"),
    ("Importar este artículo a mi biblioteca", "agregar_documento"),
    ("Añadir un nuevo registro documental", "agregar_documento"),
    ("Cargar documento nuevo para procesar", "agregar_documento"),
    ("Sube este PDF a mi colección personal", "agregar_documento"),
    ("Adjuntar archivo de investigación", "agregar_documento"),
    ("Súbete esta tarea a la nube", "agregar_documento"),
    ("Voy a subir un archivo nuevo", "agregar_documento"),
    ("Pon este documento en mi carpeta", "agregar_documento"),
    ("Anexar este reporte al sistema", "agregar_documento"),
    ("Registrar nuevo archivo en mi cuenta", "agregar_documento"),
    ("Abrir el libro que estaba leyendo ayer", "acceder_documento"),
    ("Necesito ver el documento seleccionado", "acceder_documento"),
    ("Muéstrame el archivo de la tarea", "acceder_documento"),
    ("Acceder a mis lecturas guardadas", "acceder_documento"),
    ("¿Puedes abrir el informe final en Word?", "acceder_documento"),
    ("Quiero visualizar el PDF de referencia", "acceder_documento"),
    ("Abrir el documento de mis apuntes", "acceder_documento"),
    ("Leer el archivo guardado anteriormente", "acceder_documento"),
    ("Échame la mano abriendo el PDF de ayer", "acceder_documento"),
    ("Ponme en pantalla mi lectura actual", "acceder_documento"),
    ("Ábrete el informe que guardé", "acceder_documento"),
    ("Continuar leyendo mi libro", "acceder_documento"),
    ("Recuperar mi lectura guardada", "acceder_documento"),
    ("¿Qué libros hay de ingeniería civil?", "buscar_catalogo"),
    ("Busca el documento de investigación de la semana pasada", "buscar_catalogo"),
    ("Quiero ver el catálogo de cuentos infantiles", "buscar_catalogo"),
    ("Lista todos los libros de cálculo y matemáticas", "buscar_catalogo"),
    ("¿Tienen algo de microcontroladores en la base de datos?", "buscar_catalogo"),
    ("Explorar la sección de literatura clásica", "buscar_catalogo"),
    ("Buscar cuentos de misterio y leyendas mexicanas", "buscar_catalogo"),
    ("Mostrar el inventario de libros de historia universal", "buscar_catalogo"),
    ("Chécate si hay libros de redes en la lista", "buscar_catalogo"),
    ("¿Qué archivos nuevos hay en el catálogo?", "buscar_catalogo"),
    ("Dame una lista de los libros disponibles", "buscar_catalogo"),
    ("Busca artículos sobre termodinámica", "buscar_catalogo"),
    ("Traduce este fragmento de literatura a sistema Braille", "traducir"),
    ("Pasa esta frase de mi libro a Braille", "traducir"),
    ("¿Cómo se escribe mi nombre en puntos Braille?", "traducir"),
    ("Convierte este texto universitario a Braille", "traducir"),
    ("Traducir este párrafo de cuento al Braille por favor", "traducir"),
    ("Generar la versión en Braille de este poema clásico", "traducir"),
    ("Transcribir este manual técnico al sistema Braille", "traducir"),
    ("Pasar esta lectura a formato Braille para impresión", "traducir"),
    ("Échame la mano traduciendo esto a Braille", "traducir"),
    ("¿Cómo se pone este teorema en Braille?", "traducir"),
    ("Cámbiame esta frase a puntos Braille", "traducir"),
    ("Sácame la versión en Braille de esta fábula", "traducir")
]

@pytest.mark.parametrize("query, expected_intent", test_cases)
def test_classify(query, expected_intent):
    result = semantic_classifier.classify(query)
    assert result["intent"] == expected_intent