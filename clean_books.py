#!/usr/bin/env python3
"""
Čištění knih od anglického textu Project Gutenbergu
Odstraní metadata, licence a další anglický text ze stažených e-knih
"""

import os
import re


def clean_gutenberg_text(text):
    """
    Odstraní anglický text a metadata Project Gutenbergu z knihy.
    
    Odstraňuje:
    - Úvodní informace Project Gutenbergu
    - Metadata (Title, Author, Release date, atd.)
    - Licence
    - Footer informace
    - Ostatní anglický obsah
    """
    
    # Odstraní sekci úvodem "This eBook is for the use..."
    text = re.sub(
        r'This eBook is for the use of anyone anywhere.*?before using this eBook\.\n\n',
        '',
        text,
        flags=re.DOTALL | re.IGNORECASE
    )
    
    # Odstraní "Title:", "Author:", "Release date:", atd.
    text = re.sub(r'(Title|Author|Release date|Language|Original publication|Other information):[^\n]*\n', '', text, flags=re.IGNORECASE)
    
    # Odstraní prázdné řádky s formátováním jako "        " (odsazení)
    text = re.sub(r'\n\s{4,}\n', '\n', text)
    
    # Odstraní "*** START OF THE PROJECT GUTENBERG EBOOK..."
    text = re.sub(
        r'\*{3}\s*START OF THE PROJECT GUTENBERG.*?\*{3}\n\n',
        '',
        text,
        flags=re.IGNORECASE
    )
    
    # Odstraní "*** END OF THE PROJECT GUTENBERG EBOOK..."
    text = re.sub(
        r'\n\*{3}\s*END OF THE PROJECT GUTENBERG.*?(?=\n|$)',
        '',
        text,
        flags=re.IGNORECASE | re.DOTALL
    )
    
    # Odstraní celou licence sekci (velmi dlouhý text o licence)
    text = re.sub(
        r'Updated editions will replace.*?the trademark license is very easy\..*?(?=\n\n|\Z)',
        '',
        text,
        flags=re.DOTALL | re.IGNORECASE
    )
    
    # Odstraní "THE FULL PROJECT GUTENBERG™ LICENSE" a vše za tím
    text = re.sub(
        r'THE FULL PROJECT GUTENBERG.*?(?=\Z)',
        '',
        text,
        flags=re.DOTALL | re.IGNORECASE
    )
    
    # Odstraní "START: FULL LICENSE" a všechno za tím
    text = re.sub(
        r'START:\s*FULL LICENSE.*',
        '',
        text,
        flags=re.DOTALL | re.IGNORECASE
    )
    
    # Odstraní řádky s "Credits:" atd.
    text = re.sub(r'^Credits:.*$', '', text, flags=re.MULTILINE | re.IGNORECASE)
    
    # Odstraní řádky s "www.gutenberg.org"
    text = re.sub(r'.*www\.gutenberg\.org.*\n', '', text, flags=re.IGNORECASE)
    
    # Odstraní řádky s "Project Gutenberg" (ale ponechá počáteční obsah)
    # - Jen řádky které obsahují POUZE "Project Gutenberg"
    text = re.sub(r'^\s*Project Gutenberg.*$\n?', '', text, flags=re.MULTILINE | re.IGNORECASE)
    
    # Odstraní nadměrné prázdné řádky
    text = re.sub(r'\n\n\n+', '\n\n', text)
    
    # Ořízne whitespace na začátku a konci
    text = text.strip()
    
    return text


def clean_books_in_directory(directory="."):
    """
    Projde všechny .txt soubory v adresáři a očistí je od anglického textu.
    Vytvoří kopie s příponou _cleaned.txt
    """
    
    if not os.path.isdir(directory):
        print(f"Chyba: Adresář '{directory}' neexistuje!")
        return
    
    print("="*70)
    print("ČIŠTĚNÍ KNĮ OD ANGLICKÉHO TEXTU PROJECT GUTENBERGU")
    print("="*70 + "\n")
    
    cleaned_count = 0
    errors = 0
    
    for filename in sorted(os.listdir(directory)):
        if filename.endswith('.txt') and filename.startswith('book_'):
            filepath = os.path.join(directory, filename)
            
            try:
                # Přečti původní soubor
                with open(filepath, 'r', encoding='utf-8') as f:
                    original_text = f.read()
                
                original_size = len(original_text)
                
                # Očisti text
                cleaned_text = clean_gutenberg_text(original_text)
                cleaned_size = len(cleaned_text)
                
                # Ulož očištěný soubor (přepiš původní)
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(cleaned_text)
                
                # Vypočítej redukci
                reduction = ((original_size - cleaned_size) / original_size) * 100
                
                print(f"✓ {filename}")
                print(f"  Původní: {original_size:,} bajtů → Očištěno: {cleaned_size:,} bajtů ({reduction:.1f}% redukce)")
                
                cleaned_count += 1
                
            except Exception as e:
                print(f"✗ Chyba při čištění {filename}: {e}")
                errors += 1
    
    print("\n" + "="*70)
    print(f"Celkem očištěno: {cleaned_count} souborů")
    if errors > 0:
        print(f"Chyby: {errors}")
    print("="*70 + "\n")


def main():
    """Entrypoint"""
    print()
    
    # Vstup od uživatele
    directory = input("Zadej cestu k adresáři s knihami (výchozí: .): ").strip()
    if not directory:
        directory = "."
    
    print()
    clean_books_in_directory(directory)
    
    print("Hotovo! Knihy byly očištěny od anglického textu.\n")


if __name__ == "__main__":
    main()
