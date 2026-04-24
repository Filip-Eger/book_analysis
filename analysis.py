#!/usr/bin/env python3
"""
ANALÝZA KNIH - KLÍČOVÁ SLOVA, FREKVENCE A VIZUALIZACE
- Odstraní anglický text a metadata z Project Gutenbergu
- Extrahuje klíčová slova pomocí TF-IDF
- Počítá frekvenci slov
- Ukládá výsledky + vizualizuje do grafů
"""

from datetime import datetime
import os
import re
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
import matplotlib.pyplot as plt
import pandas as pd

# Definice českých stopwords
CZECH_STOPWORDS = {
    'a', 'i', 'nebo', 'ale', 'v', 'na', 's', 'se', 'z', 'si', 'o', 'to', 'k', 'jako', 'je', 'pro', 'který',
    'která', 'které', 'kterého', 'kterým', 'kterými', 'tento', 'tata', 'těch', 'tom', 'tím', 'tomto',
    'tuto', 'těm', 'těmi', 'svůj', 'jeho', 'její', 'jejich', 'nám', 'tě', 'mě', 'ti', 'mu', 'ho', 'ji',
    'jej', 'nimi', 'jím', 'jich', 'jen', 'jenom', 'právě', 'teprve', 'už', 'však', 'tedy', 'totiž', 'avšak',
    'přitom', 'nicméně', 'ovšem', 'ať', 'či', 'kterak', 'kterýkoli', 'kdokoliv', 'kdekdo', 'můj', 'tvůj', 'já',
    'ty', 'on', 'ona', 'ono', 'my', 'vy', 'oni', 'ony', 'sebe', 'sobě', 'sebou', 'sám', 'sama', 'samo', 'jiný',
    'jiná', 'jiné', 'nějaký', 'nějaká', 'nějaké', 'některý', 'některá', 'některé', 'každý', 'každá', 'každé',
    'mnoho', 'málo', 'několik', 'tolik', 'tolikrát', 'tak', 'jsem', 'jest', 'když', 'jsme', 'byl', 'bylo',
    'ani', 'ještě', 'aby', 'už', 'však', 'tedy', 'totiž', 'avšak',
    # Anglická slova
    'the', 'and', 'project', 'gutenberg', 'you', 'with', 'this', 'work', 'for', 'ebook', 'is', 'illustration'
}

def clean_text(text):
    """Odstraní anglický text a metadata Project Gutenbergu"""
    text = re.sub(r'This eBook is for the use of anyone anywhere.*?before using this eBook\.\n\n',
                  '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'(Title|Author|Release date|Language|Original publication):[^\n]*\n',
                  '', text, flags=re.IGNORECASE)
    text = re.sub(r'\*{3}\s*(START|END) OF THE PROJECT GUTENBERG.*?\*{3}\n*',
                  '', text, flags=re.IGNORECASE)
    text = re.sub(r'Updated editions will replace.*?(?=\n\n|\Z)',
                  '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'THE FULL PROJECT GUTENBERG.*', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'START:\s*FULL LICENSE.*', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'.*www\.gutenberg\.org.*\n', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\n\n\n+', '\n\n', text)
    return text.strip()

def preprocess_text(text):
    """Příprava textu pro analýzu"""
    text = clean_text(text)
    text = text.lower()
    text = re.sub(r'[^\w\s]', ' ', text)
    words = text.split()
    filtered_words = [word for word in words if word not in CZECH_STOPWORDS and len(word) > 2 and not word.isdigit()]
    return ' '.join(filtered_words)

def extract_keywords_tfidf(texts, filenames, top_n=10):
    """Extrahuje klíčová slova pomocí TF-IDF"""
    processed_texts = [preprocess_text(text) for text in texts]
    vectorizer = TfidfVectorizer(max_features=1000, min_df=1, max_df=0.9)
    tfidf_matrix = vectorizer.fit_transform(processed_texts)
    feature_names = vectorizer.get_feature_names_out()
    results = []
    for i in range(len(texts)):
        doc_scores = tfidf_matrix[i].toarray().flatten()
        word_scores = [(feature_names[j], doc_scores[j]) for j in range(len(feature_names)) if doc_scores[j] > 0]
        word_scores.sort(key=lambda x: x[1], reverse=True)
        top_words = [word for word, score in word_scores[:top_n]]
        results.append((filenames[i], top_words, word_scores[:top_n]))
    return results

def calculate_word_frequencies(texts, filenames, top_n=15):
    """Počítá frekvenci slov"""
    results = []
    for text, filename in zip(texts, filenames):
        processed = preprocess_text(text)
        words = processed.split()
        word_freq = Counter(words)
        top_words = word_freq.most_common(top_n)
        results.append((filename, top_words))
    return results

def save_results_to_file(keywords_results, frequency_results, output_file="book_analysis_results.txt"):
    """Uloží výsledky analýzy do textového souboru"""
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("="*80 + "\n")
            f.write("ANALÝZA KNIH - KLÍČOVÁ SLOVA A FREKVENCE\n")
            f.write("="*80 + "\n")
            f.write(f"Datum analýzy: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n")
            f.write("="*80 + "\n\n")

            f.write("KLÍČOVÁ SLOVA (TF-IDF ANALÝZA)\n")
            f.write("-"*80 + "\n\n")
            for filename, keywords, _ in keywords_results:
                f.write(f"📚 {filename}\n")
                f.write(f"   Klíčová slova: {', '.join(keywords)}\n\n")

            f.write("="*80 + "\n")
            f.write("FREKVENCE SLOV\n")
            f.write("-"*80 + "\n\n")
            for filename, word_freqs in frequency_results:
                f.write(f"📚 {filename}\n")
                f.write(f"{'Slovo':<20} {'Četnost':>10}\n")
                f.write(f"{'-'*20} {'-'*10}\n")
                for word, freq in word_freqs:
                    f.write(f"{word:<20} {freq:>10}\n")
                f.write("\n")

            f.write("="*80 + "\n")
            f.write("Konec analýzy\n")
            f.write("="*80 + "\n")

        print(f"✓ Výsledky uloženy do {output_file}")
    except Exception as e:
        print(f"✗ Chyba při ukládání výsledků: {e}")

def plot_keyword_frequency(keywords_results, output_file="keyword_count.png"):
    """Vykreslí počet klíčových slov pro jednotlivé knihy"""
    book_names = [book.split('/')[-1][:30] + "..." for book, _, _ in keywords_results]
    keyword_counts = [len(keywords) for _, keywords, _ in keywords_results]

    plt.figure(figsize=(12, 6))
    bars = plt.barh(book_names, keyword_counts, color='skyblue')
    plt.title('Počet klíčových slov pro jednotlivé knihy', fontsize=16)
    plt.xlabel('Počet klíčových slov', fontsize=14)
    plt.ylabel('Kniha', fontsize=14)
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.savefig(output_file, dpi=200)
    plt.close()
    print(f"✓ Graf uložen do: {output_file}")

def plot_tfidf_scores(book_name, word_scores, output_file="tfidf_scores.png"):
    """Vykreslí TF-IDF skóre klíčových slov pro danou knihu"""
    words = [word for word, score in word_scores]
    scores = [score for word, score in word_scores]

    plt.figure(figsize=(12, 6))
    bars = plt.barh(words, scores, color='lightcoral')
    plt.title(f'TF-IDF skóre klíčových slov: {book_name[:30]}...', fontsize=16)
    plt.xlabel('TF-IDF skóre', fontsize=14)
    plt.ylabel('Slovo', fontsize=14)
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.savefig(output_file, dpi=200)
    plt.close()
    print(f"✓ Graf uložen do: {output_file}")

def plot_word_frequency(frequency_results, top_n=7, output_dir="freq_plots"):
    """Vykreslí frekvenci slov pro jednotlivé knihy"""
    os.makedirs(output_dir, exist_ok=True)
    for filename, word_freqs in frequency_results:
        words = [word for word, _ in word_freqs[:top_n]]
        counts = [count for _, count in word_freqs[:top_n]]
        plt.figure(figsize=(10, 5))
        bars = plt.barh(words, counts, color='lightgreen')
        plt.title(f'Nejčastější slova: {filename[:30]}...', fontsize=14)
        plt.xlabel('Četnost', fontsize=12)
        plt.ylabel('Slovo', fontsize=12)
        plt.gca().invert_yaxis()
        plt.tight_layout()
        plt.savefig(f"{output_dir}/freq_{filename.split('.')[0]}.png", dpi=200)
        plt.close()
        print(f"✓ Graf uložen do: {output_dir}/freq_{filename.split('.')[0]}.png")

def analyze_books(directory, top_n=10):
    """Hlavní funkce pro analýzu knih v adresáři"""
    if not os.path.isdir(directory):
        print(f"Chyba: Adresář '{directory}' neexistuje!")
        return

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

    # Výstup na obrazovku
    print("\n" + "="*70)
    print("KLÍČOVÁ SLOVA V KNIHÁCH (TF-IDF)")
    print("="*70 + "\n")
    for filename, keywords, word_scores in keywords_results:
        print(f"📚 {filename}")
        print(f"   Klíčová slova: {', '.join(keywords)}")
        print()

    # Uložení výsledků
    output_file = os.path.join(directory, "book_analysis_results.txt")
    save_results_to_file(keywords_results, frequency_results, output_file)

    # Vizualizace
    plot_keyword_frequency(keywords_results)
    for filename, _, word_scores in keywords_results:
        plot_tfidf_scores(filename, word_scores, f"{directory}/tfidf_{filename.split('.')[0]}.png")
    plot_word_frequency(frequency_results)

    print("\n" + "="*70)
    print("Všechny výsledky a grafy byly uloženy do adresáře s knihami!")
    print("="*70)

def main():
    """Entrypoint"""
    print("\n" + "="*70)
    print("ANALÝZA KNIH - KLÍČOVÁ SLOVA A FREKVENCE POMOCÍ TF-IDF")
    print("="*70 + "\n")

    directory = input("Zadej cestu k adresáři s knihami (výchozí: .): ").strip()
    if not directory:
        directory = "."
    print()
    analyze_books(directory, top_n=10)

if __name__ == "__main__":
    main()