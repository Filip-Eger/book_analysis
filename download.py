import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time

def download_czech_books():
    base_url = "https://www.gutenberg.org/browse/languages/cs.html.utf8"
    base_dir = os.getcwd()
    os.makedirs(base_dir, exist_ok=True)

    response = requests.get(base_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Najdi všechny odkazy na knihy (links to /ebooks/{id})
    book_links = []
    for link in soup.find_all('a', href=True):
        href = link['href']
        if '/ebooks/' in href and not href.startswith('/browse'):
            # Extract book ID
            try:
                book_id = int(href.split('/ebooks/')[-1].split('/')[0])
                book_links.append(f"https://www.gutenberg.org/ebooks/{book_id}")
            except ValueError:
                continue

    print(f"Nalezeno {len(book_links)} knih. Stahuji plaintext soubory...")

    # Stáhni každou knihu
    for i, book_url in enumerate(book_links, 1):
        try:
            # Extract book ID
            book_id = book_url.split('/ebooks/')[-1].rstrip('/')
            
            # Zkus hlavní URL pro plaintext
            plaintext_urls = [
                f"https://www.gutenberg.org/cache/epub/{book_id}/pg{book_id}.txt",
                f"https://www.gutenberg.org/files/{book_id}/pg{book_id}.txt",
                f"https://www.gutenberg.org/files/{book_id}/{book_id}-0.txt",
            ]
            
            file_response = None
            successful_url = None
            
            # Zkus jednotlivé URL formáty
            for plaintext_url in plaintext_urls:
                try:
                    file_response = requests.get(plaintext_url, timeout=10)
                    if file_response.status_code == 200 and len(file_response.text) > 100:
                        successful_url = plaintext_url
                        break
                except:
                    continue
            
            if file_response and successful_url:
                # Download the plaintext file
                filename = f"book_{book_id}.txt"
                filepath = os.path.join(base_dir, filename)
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(file_response.text)
                print(f"[{i}/{len(book_links)}] Staženo: {filename}")
            else:
                print(f"[{i}/{len(book_links)}] Plaintext nenalezen pro: {book_url}")
            
            # Be nice to Project Gutenberg servers
            time.sleep(1)
            
        except Exception as e:
            book_id = book_url.split('/ebooks/')[-1]
            print(f"[{i}/{len(book_links)}] Chyba při stahování {book_id}: {e}")

if __name__ == "__main__":
    download_czech_books()