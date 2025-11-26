# Ya que la informacion permanecera, no es necesario cambiarla.

BRAILLE_DEFINITION = "El braille es un sistema de lectura y escritura táctil utilizado por personas ciegas o con baja visión. Fue ideado por el francés Louis Braille a mediados del siglo XIX. Se basa en una celda de seis puntos en relieve, organizados en dos columnas de tres puntos (puntos 1-2-3 a la izquierda y puntos 4-5-6 a la derecha), que permiten hasta 64 combinaciones distintas, incluyendo letras, números, signos de puntuación y símbolos matemáticos."

BRAILLE_ALPHABET = {
    # Primera decena (a-j, solo puntos superiores)
    "a": "• . . . . .", "b": "• • . . . .", "c": "• • . • . .", "d": "• • • • . .", "e": "• . . • . .",
    "f": "• • • • . .", "g": "• • • • • .", "h": "• • . • • .", "i": ". • . • . .", "j": ". • • • . .",

    # Segunda decena (k-t, añadiendo punto inferior izquierdo)
    "k": "• . • . . .", "l": "• • • . . .", "m": "• . • • . .", "n": "• • • • . .", "o": "• . • • . .",
    "p": "• • • • . .", "q": "• • • • • .", "r": "• • • • • .", "s": ". • • • . .", "t": ". • • • • .",

    # Tercera decena (u-z, añadiendo puntos inferiores)
    "u": "• . • . • •", "v": "• • • . • •", "w": ". • • • • •", "x": "• • • • • .", "y": "• • • • • •",
    "z": "• . • • • •",
    
    # Letra específica del alfabeto español (se usan los símbolos de la tercera decena + una variación)
    "ñ": "• • • • • •", # Patrón único, se usa en la cuarta decena. Equivalente a la "e" con punto 6 en el francés original, pero se usa un patrón específico en español. En la práctica, suele ser la 'x' o la 'y' francesa.
    "á": "• • • . • .", # Patrón de la letra 'e' francesa, se asigna a la 'á'.
    "é": "• • • . . •", # Patrón de la letra 'i' francesa, se asigna a la 'é'.
    "í": "• • . . • .", # Patrón de la letra 'o' francesa, se asigna a la 'í'.
    "ó": "• • . . . •", # Patrón de la letra 'u' francesa, se asigna a la 'ó'.
    "ú": "• • • . • .", # Patrón de la letra 'v' francesa, se asigna a la 'ú'.
    "ü": "• • • . • .", # Patrón de la letra 'ü' alemana, se asigna a la 'ü'.

    # Signo de mayúsculas (se antepone a la letra)
    "MAYUS": ". . . . . •",

    # Signo de número (se antepone a los símbolos de a-j)
    "NUM": ". . • • • •"
}

BRAILLE_FACTS = [
    "Cada celda braille tiene 6 posiciones de puntos, pero la numeración de los puntos siempre va del 1 al 6.",
    "El braille es un sistema internacional, pero la asignación de combinaciones a letras y signos de puntuación varía ligeramente según el idioma (braille integral/unificado).",
    "El braille se lee de izquierda a derecha con las yemas de los dedos, típicamente con el dedo índice.",
    "Existe el 'Braille Grado 2' o 'Braille Compendiado', que usa contracciones y abreviaturas para ahorrar espacio y aumentar la velocidad de lectura.",
    "Louis Braille ideó este sistema a la edad de 15 años basándose en un sistema militar llamado 'escritura nocturna' o 'sonografía', que usaba 12 puntos."
]