
import csv
import spacy
from collections import defaultdict

nlp = spacy.load("ru_core_news_sm")

def load_intents(file_path="intents_args.csv"):
    intents = defaultdict(set)
    with open(file_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            doc = nlp(row["phrase"].strip())
            for token in doc:
                if not token.is_stop and token.is_alpha:
                    intents[row["intent"]].add(token.lemma_)
    return intents

INTENTS = load_intents()

def recognize_intent(text: str):
    doc = nlp(text.lower())
    lemmas = {token.lemma_ for token in doc if not token.is_stop and token.is_alpha}

    best_intent = None
    best_score = 0
    for intent, keywords in INTENTS.items():
        score = len(lemmas.intersection(keywords))
        if score > best_score:
            best_score = score
            best_intent = intent

    if best_score < 1:
        return None
    return best_intent
