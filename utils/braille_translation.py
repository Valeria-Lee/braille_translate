import nltk
from nltk.tokenize import word_tokenize, sent_tokenize

def braille_translate(text: str) -> list:
    nltk.download('punkt')
    
    tokenized_paragraph = []
    tokenized_sentences = sent_tokenize(text)    
    
    for sentence in tokenized_sentences:
        words = word_tokenize(sentence)
        tokenized_paragraph.append(words)
    
    print(sentence)
    
    for i, sentence_list in enumerate(tokenized_paragraph):
        is_in_number_sequence = False
        
        for j, word in enumerate(sentence_list):
            braille_word = []
            
            for k, char in enumerate(word):
                braille_segments, is_in_number_sequence = _translate_char(
                    char, 
                    is_in_number_sequence
                )
                
                # braille_segments puede ser un string o una lista
                if isinstance(braille_segments, list):
                    braille_word.extend(braille_segments)
                else:
                    braille_word.append(braille_segments)
                
                # terminar secuencia numerica si el siguiente no es digito
                if is_in_number_sequence and k < len(word) - 1:
                    if not word[k + 1].isdigit():
                        is_in_number_sequence = False
            
            # terminar secuencia numerica al final de la palabra
            is_in_number_sequence = False
            
            # guardar como lista de caracteres braille individuales
            tokenized_paragraph[i][j] = braille_word
    
    return tokenized_paragraph

def _translate_char(char: str, is_in_number_sequence: bool) -> tuple[str | list, bool]:
    mayus_char = "⠠"
    number_char = "⠼"

    braille_characters = {
        "a": "⠁",
        "b": "⠃",
        "c": "⠉",
        "d": "⠙",
        "e": "⠑",
        "f": "⠋",
        "g": "⠛",
        "h": "⠓",
        "i": "⠊",
        "j": "⠚",
        "k": "⠅",
        "l": "⠇",
        "m": "⠍",
        "n": "⠝",
        "o": "⠕",
        "p": "⠏",
        "q": "⠟",
        "r": "⠗",
        "s": "⠎",
        "t": "⠞",
        "u": "⠥",
        "v": "⠧",
        "w": "⠺",
        "x": "⠭",
        "y": "⠽",
        "z": "⠵",
        "á": "⠷",
        "é": "⠮",
        "í": "⠌",
        "ó": "⠬",
        "ú": "⠾",
        "ü": "⠳",
        ",": "⠂",  # punctuation
        ";": "⠆",
        ":": "⠒",
        ".": "⠲",
        "¿": ["⠐", "⠢"],  
        "?": "⠦",
        "¡": ["⠐", "⠣"],  
        "!": "⠖",
        "'": "⠄",
        '"': "⠶",
        "(": ["⠐", "⠣"],  
        ")": ["⠐", "⠜"],  
        "–": "⠤",
        "...": ["⠲", "⠲", "⠲"]  
    }
    
    # "⠼" number indicator, international standard
    numbers = {
        "1": "⠁",
        "2": "⠃",
        "3": "⠉",
        "4": "⠙",
        "5": "⠑",
        "6": "⠋",
        "7": "⠛",
        "8": "⠓",
        "9": "⠊",
        "0": "⠚"
    }
    
    # mayusculas.
    if char.isupper():
        lower_char = char.lower() # lo hago minuscula
        
        if lower_char in braille_characters:
            result = braille_characters[lower_char]

            if isinstance(result, list):
                # pertenece a un simbolo con mas de un caracter
                return [mayus_char] + result, False
            else:
                return [mayus_char, result], False
        else:
            # en el caso de que la letra no este en el diccionario
            return [mayus_char, char], False
    
    # numeros.
    if char.isdigit():
        braille_char = numbers.get(char)
        if not is_in_number_sequence:
            # iniciar la secuencia de numeros
            return [number_char, braille_char], True
        else:
            return braille_char, True
    
    elif char.lower() in braille_characters:
        braille_symbol = braille_characters[char.lower()]
        return braille_symbol, False
    
    else:
        return char, False

def send_braille_characters(data):
    dot_positions = {
        "⠁": [1],
        "⠃": [1, 2],
        "⠉": [1, 4],
        "⠙": [1, 4, 5],
        "⠑": [1, 5],
        "⠋": [1, 2, 4],
        "⠛": [1, 2, 4, 5],
        "⠓": [1, 2, 5],
        "⠊": [2, 4],
        "⠚": [2, 4, 5],
        "⠅": [1, 3],
        "⠇": [1, 2, 3],
        "⠍": [1, 3, 4],
        "⠝": [1, 3, 4, 5],
        "⠕": [1, 3, 5],
        "⠏": [1, 2, 3, 4],
        "⠟": [1, 2, 3, 4, 5],
        "⠗": [1, 2, 3, 5],
        "⠎": [2, 3, 4],
        "⠞": [2, 3, 4, 5],
        "⠥": [1, 3, 6],
        "⠧": [1, 2, 3, 6],
        "⠺": [2, 4, 5, 6],
        "⠭": [1, 3, 4, 6],
        "⠽": [1, 3, 4, 5, 6],
        "⠵": [1, 3, 5, 6],
        "⠷": [1, 2, 3, 5, 6],
        "⠮": [2, 3, 4, 6],
        "⠌": [3, 4],
        "⠬": [2, 4, 6],
        "⠾": [1, 2, 3, 5, 6],
        "⠳": [1, 2, 5, 6],
        "⠂": [2],
        "⠆": [2, 3],
        "⠒": [2, 5],
        "⠲": [2, 5, 6],
        "⠦": [2, 3, 6],
        "⠖": [2, 3, 5],
        "⠄": [3],
        "⠶": [2, 3, 5, 6],
        "⠤": [3, 6],
        "⠐": [5, 6],
        "⠢": [2, 6],
        "⠣": [1, 2, 6],
        "⠜": [3, 4, 5],
        "⠼": [3, 4, 5, 6],
        "⠠": [6],
    }
    
    def process_word(word_list):
        result = []
        print(f"\nPalabra: {''.join(word_list)}")
        for i, braille_char in enumerate(word_list):
            positions = process_char(braille_char)
            result.append(positions)
            print(f"\nCaracter {i+1}: {braille_char} → Puntos: {positions}")
            print_braille_cell(positions)
        return result
        
    if not data:
        return []
    
    if isinstance(data, str):
        positions = process_char(data)
        print_braille_cell(positions)
        return positions
    
    if isinstance(data[0], str):
        return process_word(data)
    
    if isinstance(data[0], list):
        if data[0] and isinstance(data[0][0], list):
            result = []
            for i, sentence in enumerate(data):
                print(f"Oración {i + 1}")
                sentence_result = []
                for word in sentence:
                    word_result = process_word(word)
                    sentence_result.append(word_result)
                result.append(sentence_result)
                print()
            return result
        else:
            # lista de palabras: [[chars], [chars]]
            result = []
            for word in data:
                word_result = process_word(word)
                result.append(word_result)
            return result
    
    return []

# TODO: in order to sent them to the display
def convert_chars_to_dots(char):
    pass