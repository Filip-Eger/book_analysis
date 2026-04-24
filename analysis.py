#!/usr/bin/env python3
"""
Analýza knih - extrakce klíčových slov pomocí TF-IDF a počítání frekvencí
"""

import os
import re
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from datetime import datetime

# Definice českých stopwords
CZECH_STOPWORDS = {
    'a', 'i', 'nebo', 'ale', 'v', 'na', 's', 'se', 'z', 'si', 'o', 'to', 'k', 'jako', 'je', 'pro', 'který',
    'která', 'které', 'kterého', 'kterým', 'kterými', 'tento', 'tato', 'toto', 'těch', 'tom', 'tím', 'tomto',
    'tuto', 'tato', 'těm', 'těmi', 'svůj', 'jeho', 'její', 'jejich', 'nám', 'tě', 'mě', 'ti', 'mu', 'ho', 'ji',
    'jej', 'nimi', 'jím', 'jich', 'jen', 'jenom', 'právě', 'teprve', 'už', 'však', 'tedy', 'totiž', 'avšak',
    'přitom', 'nicméně', 'ovšem', 'ať', 'či', 'kterak', 'kterýkoli', 'kdokoliv', 'kdekdo', 'můj', 'tvůj', 'já',
    'ty', 'on', 'ona', 'ono', 'my', 'vy', 'oni', 'ony', 'sebe', 'sobě', 'sebou', 'sám', 'sama', 'samo', 'jiný',
    'jiná', 'jiné', 'nějaký', 'nějaká', 'nějaké', 'některý', 'některá', 'některé', 'každý', 'každá', 'každé',
    'mnoho', 'málo', 'několik', 'tolik', 'tolikrát', 'tak', 'jsem', 'jest', 'když', 'jsme', 'byl', 'bylo',
    'ani', 'ještě', 'aby', 'už', 'však', 'tedy', 'totiž', 'avšak'
    # Anglická slova
    'the', 'and', 'project', 'gutenberg', 'you', 'with', 'this', 'work', 'for', 'ebook', 'is'
}
#CZECH_STOPWORDS_ = {
#    # Základní české stopwords
#    'a', 'i', 'nebo', 'ale', 'v', 'na', 's', 'se', 'z', 'si', 'o', 'to', 'k', 'jako', 'je', 'pro', 'který',
#    'která', 'které', 'kterého', 'kterým', 'kterými', 'tento', 'tato', 'toto', 'těch', 'tom', 'tím', 'tomto',
#    'tuto', 'tata', 'těm', 'těmi', 'svůj', 'jeho', 'její', 'jejich', 'nám', 'tě', 'mě', 'ti', 'mu', 'ho', 'ji',
#    'jej', 'nimi', 'jím', 'jich', 'jen', 'jenom', 'právě', 'teprve', 'už', 'však', 'tedy', 'totiž', 'avšak',
#    'přitom', 'nicméně', 'ovšem', 'ať', 'či', 'kterak', 'kterýkoli', 'kdokoliv', 'kdekdo', 'můj', 'tvůj', 'já',
#    'ty', 'on', 'ona', 'ono', 'my', 'vy', 'oni', 'ony', 'sebe', 'sobě', 'sebou', 'sám', 'sama', 'samo', 'jiný',
#    'jiná', 'jiné', 'nějaký', 'nějaká', 'nějaké', 'některý', 'některá', 'některé', 'každý', 'každá', 'každé',
#    'mnoho', 'málo', 'několik', 'tolik', 'tolikrát', 'tak', 'jsem', 'jest', 'když', 'jsme', 'byl', 'bylo',
#    'ani', 'ještě', 'aby', 'už', 'však', 'tedy', 'totiž', 'avšak',
#
#    # Anglická slova
#    'the', 'and', 'project', 'gutenberg', 'you', 'with', 'this', 'work', 'for', 'ebook', 'is', 'illustration'
#}


def clean_text(text):
    """Odstraní anglický text a metadata Project Gutenbergu"""
    text = re.sub(r'This eBook is for the use of anyone anywhere.*?before using this eBook\.\n\n', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'(Title|Author|Release date|Language|Original publication):[^\n]*\n', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\*{3}\s*(START|END) OF THE PROJECT GUTENBERG.*?\*{3}\n*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'Updated editions will replace.*?(?=\n\n|\Z)', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'THE FULL PROJECT GUTENBERG.*', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'START:\s*FULL LICENSE.*', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'.*www\.gutenberg\.org.*\n', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\n\n\n+', '\n\n', text)
    return text.strip()


def preprocess_text(text):
    """
    Příprava textu pro analýzu:
    - čištění od anglického textu
    - převod na lowercase
    - odstranění speciálních znaků
    - odstranění stopwords
    - filtrování krátkých slov
    """
    # Očisti text od anglického obsahu
    text = clean_text(text)
    
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


def calculate_word_frequencies(texts, filenames, top_n=15):
    """
    Počítá frekvence slov v každém textu.
    
    Vrátí: seznam tuplů (filename, seznam (slovo, četnost))
    """
    print("Počítání frekvencí slov...")
    results = []
    
    for text, filename in zip(texts, filenames):
        # Příprava textu
        processed = preprocess_text(text)
        words = processed.split()
        
        # Počítání frekvencí
        word_freq = Counter(words)
        
        # Top N nejčastějších slov
        top_words = word_freq.most_common(top_n)
        results.append((filename, top_words))
    
    return results


def save_results_to_file(keywords_results, frequency_results, output_file="book_analysis_results.txt"):
    """
    Uloží výsledky analýzy do textového souboru.
    """
    print(f"Ukládání výsledků do {output_file}...")
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            # Hlavička
            f.write("="*80 + "\n")
            f.write("ANALÝZA KNIH - KLÍČOVÁ SLOVA A FREKVENCE\n")
            f.write("="*80 + "\n")
            f.write(f"Datum analýzy: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n")
            f.write("="*80 + "\n\n")
            
            # Klíčová slova (TF-IDF)
            f.write("KLÍČOVÁ SLOVA (TF-IDF ANALÝZA)\n")
            f.write("-"*80 + "\n\n")
            
            for filename, keywords in keywords_results:
                f.write(f"📚 {filename}\n")
                f.write(f"   Klíčová slova: {', '.join(keywords)}\n\n")
            
            # Frekvence slov
            f.write("\n" + "="*80 + "\n")
            f.write("FREKVENCE SLOV\n")
            f.write("-"*80 + "\n\n")
            
            for filename, word_freqs in frequency_results:
                f.write(f"📚 {filename}\n")
                f.write(f"{'Slovo':<20} {'Četnost':>10}\n")
                f.write(f"{'-'*20} {'-'*10}\n")
                
                for word, freq in word_freqs:
                    f.write(f"{word:<20} {freq:>10}\n")
                
                f.write("\n")
            
            # Konec
            f.write("="*80 + "\n")
            f.write("Konec analýzy\n")
            f.write("="*80 + "\n")
        
        print(f"✓ Výsledky úspěšně uloženy do {output_file}")
    except Exception as e:
        print(f"✗ Chyba při ukládání výsledků: {e}")


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
    keywords_results = extract_keywords_tfidf(texts, filenames, top_n)
    
    # Počítej frekvence
    frequency_results = calculate_word_frequencies(texts, filenames, top_n=15)
    
    # Výstup výsledků na obrazovku
    print("\n" + "="*70)
    print("KLÍČOVÁ SLOVA V KNIHÁCH (TF-IDF)")
    print("="*70 + "\n")
    
    for filename, keywords in keywords_results:
        print(f"📚 {filename}")
        print(f"   {', '.join(keywords)}")
        print()
    
    # Uložení výsledků do souboru
    output_file = os.path.join(directory, "book_analysis_results.txt")
    save_results_to_file(keywords_results, frequency_results, output_file)
    
    print("\n" + "="*70)


def main():
    """Entrypoint"""
    print("\n" + "="*70)
    print("ANALÝZA KNIH - KLÍČOVÁ SLOVA A FREKVENCE POMOCÍ TF-IDF")
    print("="*70 + "\n")
    
    # Vstup od uživatele
    directory = input("Zadej cestu k adresáři s knihami (výchozí: .): ").strip()
    if not directory:
        directory = "."
    
    print()
    analyze_books(directory, top_n=10)


if __name__ == "__main__":
    main()