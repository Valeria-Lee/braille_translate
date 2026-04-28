from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import nltk, spacy, unicodedata

def _delete_accents(text: str) -> str:
    nfkd_str = unicodedata.normalize('NFKD', text)
    return "".join([c for c in nfkd_str if not unicodedata.combining(c)])

def _turn_words_into_root(text: str) -> list():
    nlp = spacy.load("es_core_news_sm")
    doc = nlp(text)
    return " ".join(t.lemma_ for t in doc)

def normalize_text(text: str) -> str:
    nltk.download('stopwords', quiet=True)
    nltk.download('punkt', quiet=True)
    
    lower_text = text.lower()

    tokenized_text = nltk.word_tokenize(lower_text)
    tokenized_text = " ".join([t for t in tokenized_text])

    removed_accents = _delete_accents(tokenized_text)

    lemmarize_text = _turn_words_into_root(removed_accents)

    return "".join(lemmarize_text)

def _select_word_stemming(text: str) -> list():
    porter = nltk.PorterStemmer()

    porter_text = "".join([porter.stem(word) for word in text])

    return porter_text