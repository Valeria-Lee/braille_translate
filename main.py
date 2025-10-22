
# se podria hacer con un dict
alphabet = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','ñ','r','s','t','u','v','w','x','y','z','á','é','í','ó','ú','ü']
braille_alphabet = ['⠁','⠃','⠉','⠙','⠑','⠋','⠛','⠓','⠊','⠚','⠅','⠇','⠍','⠝','⠕','⠏','⠟','⠻','⠗','⠎','⠞','⠥','⠧','⠺','⠭','⠽','⠵','⠷','⠮','⠌','⠬','⠾','⠳']

# TODO: signos de puntuacion y numeros

print(len(alphabet))
print(len(braille_alphabet))

def convert_to_braille(sentence: str):
    braille_sentence = []

    for i in range(len(sentence)):
        index = alphabet.index(sentence[i])
        char = braille_alphabet[index]
        braille_sentence.append(char)
    
    return braille_sentence

print(convert_to_braille("hola"))