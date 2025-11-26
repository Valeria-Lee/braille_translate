import unittest
from braille_translation import braille_translate 

class TestBrailleTranslate(unittest.TestCase):
    def test_basic_translation(self):
        text = "casa"
        # braille: c=⠉, a=⠁, s=⠎, a=⠁. 
        # resultado esperado: [ [['⠉', '⠁', '⠎', '⠁']] ]
        expected = [[['⠉', '⠁', '⠎', '⠁']]] 
        self.assertEqual(braille_translate(text), expected, "La traducción básica de letras falló.")

    def test_number_sequence(self):
        text = "el 123" 
        # braille: e=⠑, l=⠇. Espacio. 123 = ⠼⠁⠃⠉.
        # resultado: [ [['⠑', '⠇'], ['⠼', '⠁', '⠃', '⠉']] ]
        expected = [[['⠑', '⠇'], ['⠼', '⠁', '⠃', '⠉']]]
        self.assertEqual(braille_translate(text), expected, "La secuencia numérica falló.")

    def test_diacritics_and_special_chars(self):
        text = "¿qué?"
        # NLTK tokeniza como: ['¿qué', '?'] o ['¿', 'qué', '?']
        # Asumiendo tokenización: ['¿qué', '?']
        # ¿qué = ⠐⠢⠟⠥⠮, ? = ⠦
        # resultado: [ [['⠐', '⠢', '⠟', '⠥', '⠮'], ['⠦']] ]
        expected = [[['⠐', '⠢', '⠟', '⠥', '⠮'], ['⠦']]]
        self.assertEqual(braille_translate(text), expected, "La traducción de caracteres especiales falló.")

    def test_multi_paragraph(self):
        text = "Hola mundo. Adios mundo."
        # sent_tokenize separa las dos oraciones
        # word_tokenize separa el punto como token independiente
        # Primera oración: "Hola mundo."
        #   - Hola = ⠠⠓⠕⠇⠁ (mayus H)
        #   - mundo = ⠍⠥⠝⠙⠕
        #   - . = ⠲ (separado)
        # Segunda oración: "Adios mundo."
        #   - Adios = ⠠⠁⠙⠊⠕⠎ (mayus A)
        #   - mundo = ⠍⠥⠝⠙⠕
        #   - . = ⠲ (separado)
        expected = [
            [['⠠', '⠓', '⠕', '⠇', '⠁'], ['⠍', '⠥', '⠝', '⠙', '⠕'], ['⠲']], 
            [['⠠', '⠁', '⠙', '⠊', '⠕', '⠎'], ['⠍', '⠥', '⠝', '⠙', '⠕'], ['⠲']]
        ]
        self.assertEqual(braille_translate(text), expected, "La estructura de oraciones/párrafos falló.")

    def test_uppercase_indicator(self):
        text = "A"
        # A mayus = ⠠⠁
        expected = [[['⠠', '⠁']]]
        self.assertEqual(braille_translate(text), expected, "El indicador de mayúsculas falló.")

    def test_mixed_case(self):
        text = "Hola"
        # H mayus = ⠠⠓, ola = ⠕⠇⠁
        expected = [[['⠠', '⠓', '⠕', '⠇', '⠁']]]
        self.assertEqual(braille_translate(text), expected, "La mezcla de mayúsculas falló.")

if __name__ == '__main__':
    unittest.main()