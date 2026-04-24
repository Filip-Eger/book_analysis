#!/usr/bin/env python3
import os
import re

def extract_metadata(filepath):
    """Extrahuje autora a název z Project Gutenberg knihy"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read(2000)  # Čteme jen první část
        
        # Vyhledej autora
        author_match = re.search(r'Author:\s*([^\n]+)', content)
        author = author_match.group(1).strip() if author_match else "Unknown"
        
        # Vyhledej titul
        title_match = re.search(r'Title:\s*([^\n]+)', content)
        title = title_match.group(1).strip() if title_match else "Unknown"
        
        return author, title
    except Exception as e:
        print(f"Chyba při čtení {filepath}: {e}")
        return "Unknown", "Unknown"

def sanitize_filename(text):
    """Očistí text pro použití v názvu souboru"""
    # Odstraní speciální znaky a nahradí je podtržítky
    text = re.sub(r'[^\w\s\-]', '', text)
    # Nahradí mezery a pomlčky podtržítky
    text = re.sub(r'[\s\-]+', '_', text)
    # Zkrátí na 50 znaků
    return text[:50]

def rename_books(directory):
    """Přejmenuje všechny .txt soubory v adresáři"""
    if not os.path.isdir(directory):
        print(f"Adresář {directory} neexistuje!")
        return
    
    renamed_count = 0
    for filename in os.listdir(directory):
        if filename.endswith('.txt') and filename.startswith('book_'):
            filepath = os.path.join(directory, filename)
            author, title = extract_metadata(filepath)
            
            # Připrav nový název
            author_clean = sanitize_filename(author)
            title_clean = sanitize_filename(title)
            new_filename = f"book_{author_clean}_{title_clean}.txt"
            new_filepath = os.path.join(directory, new_filename)
            
            # Pokud soubor s novým názvem již existuje, přidej číslo
            counter = 1
            base_name = new_filename[:-4]
            while os.path.exists(new_filepath):
                new_filename = f"{base_name}_{counter}.txt"
                new_filepath = os.path.join(directory, new_filename)
                counter += 1
            
            # Přejmenuj soubor
            try:
                os.rename(filepath, new_filepath)
                print(f"✓ {filename} → {new_filename}")
                print(f"  Autor: {author}, Titul: {title}")
                renamed_count += 1
            except Exception as e:
                print(f"✗ Chyba při přejmenování {filename}: {e}")
    
    print(f"\nCelkem přejmenováno: {renamed_count} souborů")

if __name__ == "__main__":
    books_dir = input("Zadej cestu k adresáři s knihami (výchozí: .): ").strip()
    if not books_dir:
        books_dir = "."
    rename_books(books_dir)
