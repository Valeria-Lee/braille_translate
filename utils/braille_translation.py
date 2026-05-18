import nltk
from nltk.tokenize import word_tokenize, sent_tokenize

def braille_translate(text: str) -> list:
    tokenized_text = _tokenize_words(text)
    tokenized_paragraph = []

    for sentence in tokenized_text:
        is_in_number_sequence = False
        sentence_result = []

        for word in sentence:
            braille_word = []
            k = 0

            for char in word:
                braille_segments, is_in_number_sequence = _translate_char(
                    char,
                    is_in_number_sequence
                )

                if isinstance(braille_segments, list):
                    braille_word.extend(braille_segments)
                else:
                    braille_word.append(braille_segments)

                if is_in_number_sequence and k < len(word) - 1:
                    if not word[k + 1].isdigit():
                        is_in_number_sequence = False

                k += 1

            is_in_number_sequence = False
            sentence_result.append(braille_word)

        tokenized_paragraph.append(sentence_result)

    return tokenized_paragraph

def _tokenize_words(text: str) -> list:
    nltk.download('punkt',     quiet=True)
    nltk.download('punkt_tab', quiet=True)
 
    tokenized_paragraph = []
    tokenized_sentences = sent_tokenize(text)
 
    for sentence in tokenized_sentences:
        words = word_tokenize(sentence)
        tokenized_paragraph.append(words)
 
    return tokenized_paragraph

def _translate_char(char: str, is_in_number_sequence: bool) -> tuple:
    mayus_char  = "⠠"
    number_char = "⠼"
 
    braille_characters = {
        "a": "⠁", "b": "⠃", "c": "⠉", "d": "⠙", "e": "⠑",
        "f": "⠋", "g": "⠛", "h": "⠓", "i": "⠊", "j": "⠚",
        "k": "⠅", "l": "⠇", "m": "⠍", "n": "⠝", "o": "⠕",
        "p": "⠏", "q": "⠟", "r": "⠗", "s": "⠎", "t": "⠞",
        "u": "⠥", "v": "⠧", "w": "⠺", "x": "⠭", "y": "⠽",
        "z": "⠵",
        "á": "⠷", "é": "⠮", "í": "⠌", "ó": "⠬", "ú": "⠾", "ü": "⠳",
        ",": "⠂", ";": "⠆", ":": "⠒", ".": "⠲",
        "¿": ["⠐", "⠢"], "?": "⠦",
        "¡": ["⠐", "⠣"], "!": "⠖",
        "'": "⠄", '"': "⠶",
        "(": ["⠐", "⠣"], ")": ["⠐", "⠜"],
        "–": "⠤", "...": ["⠲", "⠲", "⠲"],
    }
 
    numbers = {
        "1": "⠁", "2": "⠃", "3": "⠉", "4": "⠙", "5": "⠑",
        "6": "⠋", "7": "⠛", "8": "⠓", "9": "⠊", "0": "⠚",
    }
 
    if char.isupper():
        lower_char = char.lower()
        if lower_char in braille_characters:
            result = braille_characters[lower_char]
            if isinstance(result, list):
                return [mayus_char] + result, False
            return [mayus_char, result], False
        return [mayus_char, char], False
 
    if char.isdigit():
        braille_char = numbers.get(char, char)
        if not is_in_number_sequence:
            return [number_char, braille_char], True
        return braille_char, True
 
    if char.lower() in braille_characters:
        return braille_characters[char.lower()], False

    return char, False

def send_braille_characters(braille_text: list) -> list:
    result = []
    for sentence in braille_text:
        for word in sentence:
            for char in word:
                dots = convert_braille_characters_to_dots(char)
                if dots is not None:
                    result.append(dots)
            result.append([])

    if len(result) > 0:
        result.pop()
    
    return result

def convert_braille_characters_to_dots(char: str) -> list | None:
    dot_positions = {
        "⠁": [1],         "⠃": [1, 2],       "⠉": [1, 4],       "⠙": [1, 4, 5],
        "⠑": [1, 5],      "⠋": [1, 2, 4],    "⠛": [1, 2, 4, 5], "⠓": [1, 2, 5],
        "⠊": [2, 4],      "⠚": [2, 4, 5],    "⠅": [1, 3],       "⠇": [1, 2, 3],
        "⠍": [1, 3, 4],   "⠝": [1, 3, 4, 5], "⠕": [1, 3, 5],    "⠏": [1, 2, 3, 4],
        "⠟": [1,2,3,4,5], "⠗": [1, 2, 3, 5], "⠎": [2, 3, 4],    "⠞": [2, 3, 4, 5],
        "⠥": [1, 3, 6],   "⠧": [1, 2, 3, 6], "⠺": [2, 4, 5, 6], "⠭": [1, 3, 4, 6],
        "⠽": [1,3,4,5,6], "⠵": [1, 3, 5, 6], "⠷": [1, 2, 3, 5, 6], "⠮": [2, 3, 4, 6],
        "⠌": [3, 4],      "⠬": [2, 4, 6],    "⠾": [1, 2, 3, 5, 6], "⠳": [1, 2, 5, 6],
        "⠂": [2],         "⠆": [2, 3],       "⠒": [2, 5],       "⠲": [2, 5, 6],
        "⠦": [2, 3, 6],   "⠖": [2, 3, 5],    "⠄": [3],          "⠶": [2, 3, 5, 6],
        "⠤": [3, 6],      "⠐": [5, 6],       "⠢": [2, 6],       "⠣": [1, 2, 6],
        "⠜": [3, 4, 5],   "⠼": [3, 4, 5, 6], "⠠": [6],          "⠷": [1, 2, 3, 5, 6],
        "⠾": [2, 3, 4, 5, 6], "⠳": [1, 2, 5, 6], "⠬": [2, 4, 6], "⠮": [2, 3, 4, 6],
        "⠌": [3, 4],
    }
    return dot_positions.get(char)

    # 2,5,6 signo de division