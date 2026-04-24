#!/usr/bin/env python3
"""
Analýza knih - extrakce klíčových slov pomocí TF-IDF
"""

import os
import re
from sklearn.feature_extraction.text import TfidfVectorizer
import nltk
from nltk.tokenize import word_tokenize

# Stáhnout potřebné zdroje pro nltk (proved jednou)
nltk.download('punkt')
nltk.download('stopwords')

# Definice českých stopwords
CZECH_STOPWORDS = {
    'a', 'i', 'nebo', 'ale', 'v', 'na', 's', 'se', 'z', 'si', 'o', 'to', 'k', 'jako', 'je', 'pro', 'který',
    'která', 'které', 'kterého', 'kterým', 'kterými', 'tento', 'tato', 'toto', 'těch', 'tom', 'tím', 'tomto',
    'tuto', 'tato', 'těm', 'těmi', 'svůj', 'jeho', 'její', 'jejich', 'nám', 'tě', 'mě', 'ti', 'mu', 'ho', 'ji',
    'jej', 'nimi', 'jím', 'jich', 'jen', 'jenom', 'právě', 'teprve', 'už', 'však', 'tedy', 'totiž', 'avšak',
    'přitom', 'nicméně', 'ovšem', 'ať', 'či', 'kterak', 'kterýkoli', 'kdokoliv', 'kdekdo', 'můj', 'tvůj', 'já',
    'ty', 'on', 'ona', 'ono', 'my', 'vy', 'oni', 'ony', 'sebe', 'sobě', 'sebou', 'sám', 'sama', 'samo', 'jiný',
    'jiná', 'jiné', 'nějaký', 'nějaká', 'nějaké', 'některý', 'některá', 'některé', 'každý', 'každá', 'každé',
    'mnoho', 'málo', 'několik', 'tolik', 'tolikrát'
}

# Definice českých stopwords
CZECH_STOPWORDS = {
    'a', 'i', 'nebo', 'ale', 'v', 'na', 's', 'se', 'z', 'si', 'o', 'to', 'k', 'jako', 'je', 'pro', 'který',
    'která', 'které', 'kterého', 'kterým', 'kterými', 'tento', 'tato', 'toto', 'těch', 'tom', 'tím', 'tomto',
    'tuto', 'tato', 'těm', 'těmi', 'svůj', 'jeho', 'její', 'jejich', 'nám', 'tě', 'mě', 'ti', 'mu', 'ho', 'ji',
    'jej', 'nimi', 'jím', 'jich', 'jen', 'jenom', 'právě', 'teprve', 'už', 'však', 'tedy', 'totiž', 'avšak',
    'přitom', 'nicméně', 'ovšem', 'ať', 'či', 'kterak', 'kterýkoli', 'kdokoliv', 'kdekdo', 'můj', 'tvůj', 'já',
    'ty', 'on', 'ona', 'ono', 'my', 'vy', 'oni', 'ony', 'sebe', 'sobě', 'sebou', 'sám', 'sama', 'samo', 'jiný',
    'jiná', 'jiné', 'nějaký', 'nějaká', 'nějaké', 'některý', 'některá', 'některé', 'každý', 'každá', 'každé',
    'mnoho', 'málo', 'několik', 'tolik', 'tolikrát'
}

def preprocess_text(text):
    """
    Příprava textu pro analýzu:
    - převod na lowercase
    - odstranění speciálních znaků
    - odstranění stopwords
    - filtrování krátkých slov
    """
    # Převod na malá písmena
    text = text.lower()
    
    # Odstranění speciálních znaků, ponechání pouze slov a mezer
    text = re.sub(r'[^\w\s]', ' ', text)
    
    # Rozdělení na slova
    words = text.split()
    
    # Filtrování: odstraň stopwords a krátká slova
    filtered_words = [
        word for word in words 
        if word not in CZECH_STOPWORDS and len(word) > 2 and not word.isdigit()
    ]
    
    return ' '.join(filtered_words)


def extract_keywords_tfidf(texts, filenames, top_n=10):
    """
    Extrahuje klíčová slova z textů pomocí TF-IDF.
    
    Parametry:
    - texts: seznam textů
    - filenames: seznam názvů souborů (pro výstup)
    - top_n: počet klíčových slov na soubor
    
    Vrátí: seznam seznamů klíčových slov
    """
    # Příprava textů
    print("Příprava textů...")
    processed_texts = [preprocess_text(text) for text in texts]
    
    # TF-IDF vektorizace
    print("Výpočet TF-IDF...")
    vectorizer = TfidfVectorizer(
        max_features=1000,      # Limituj na 1000 nejčastějších slov
        min_df=1,               # Slovo se musí vyskytovat alespoň 1x
        max_df=0.9,             # Slovo se nesmí vyskytovat ve více než 90% dokumentů
    )
    tfidf_matrix = vectorizer.fit_transform(processed_texts)
    feature_names = vectorizer.get_feature_names_out()
    
    # Extrakce klíčových slov pro každý dokument
    print("Extrakce klíčových slov...")
    results = []
    for i in range(len(texts)):
        # Získej skóry TF-IDF pro tento dokument
        doc_scores = tfidf_matrix[i].toarray().flatten()
        
        # Spoj slova se skóry a seřaď sestupně
        word_scores = [(feature_names[j], doc_scores[j]) 
                      for j in range(len(feature_names)) if doc_scores[j] > 0]
        word_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Vezmi top N
        top_words = [word for word, score in word_scores[:top_n]]
        results.append((filenames[i], top_words))
    
    return results


def analyze_books(directory, top_n=10):
    """Hlavní funkce pro analýzu knih v adresáři"""
    
    if not os.path.isdir(directory):
        print(f"Chyba: Adresář '{directory}' neexistuje!")
        return
    
    # Načti všechny .txt soubory
    texts = []
    filenames = []
    
    print(f"Hledám .txt soubory v {directory}...\n")
    for filename in sorted(os.listdir(directory)):
        if filename.endswith('.txt'):
            filepath = os.path.join(directory, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    text = f.read()
                    texts.append(text)
                    filenames.append(filename)
                    print(f"✓ Načten: {filename}")
            except Exception as e:
                print(f"✗ Chyba při čtení {filename}: {e}")
    
    if not texts:
        print("Nebyl nalezen žádný .txt soubor!")
        return
    
    print(f"\nCelkem načteno: {len(texts)} souborů\n")
    
    # Extrahuj klíčová slova
    results = extract_keywords_tfidf(texts, filenames, top_n)
    
    # Výstup výsledků
    print("\n" + "="*70)
    print("KLÍČOVÁ SLOVA V KNIHÁCH")
    print("="*70 + "\n")
    
    for filename, keywords in results:
        print(f"📚 {filename}")
        print(f"   {', '.join(keywords)}")
        print()


def main():
    """Entrypoint"""
    print("\n" + "="*70)
    print("ANALÝZA KNIH - EXTRAKCE KLÍČOVÝCH SLOV POMOCÍ TF-IDF")
    print("="*70 + "\n")
    
    # Vstup od uživatele
    directory = input("Zadej cestu k adresáři s knihami (výchozí: .): ").strip()
    if not directory:
        directory = "."
    
    print()
    analyze_books(directory, top_n=10)


if __name__ == "__main__":
    main()