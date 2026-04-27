import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import re

# quitar comas se le puedan anadir

def _remove_stopwords(text: str) -> str:
    stop_words = set(stopwords.words('spanish'))
    filtered_text = [x for x in text if x not in stop_words]

    return filtered_text

def _select_word_stemming(text) -> list():
    porter = nltk.PorterStemmer()
    # lancaster = nltk.LancasterStemmer()

    porter_text = [porter.stem(word) for word in text]

    return porter_text

def normalize_text(text: str) -> str:
    nltk.download('stopwords')
    nltk.download('punkt')
    
    lower_text = text.lower()

    tokenized_text = nltk.word_tokenize(lower_text)

    removed_stopwords = _remove_stopwords(tokenized_text)
    print(removed_stopwords)

    stemmer_text = _select_word_stemming(removed_stopwords)
    print(stemmer_text)

    return " ".join(stemmer_text)
