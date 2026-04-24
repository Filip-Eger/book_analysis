import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def download_czech_books():
    base_url = "https://www.gutenberg.org/browse/languages/cs.html.utf8"
    base_dir = os.getcwd()
    os.makedirs(base_dir, exist_ok=True)

    response = requests.get(base_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Najdi všechny odkazy na knihy
    book_links = []
    for link in soup.find_all('a', href=True):
        href = link['href']
        if '/ebooks/' in href and 'plaintext' in href:
            book_links.append(urljoin(base_url, href))

    # Stáhni každou knihu
    for book_url in book_links:
        book_id = book_url.split('/')[-1]
        download_url = f"https://www.gutenberg.org/files/{book_id}/{book_id}-0.txt"
        book_title = book_url.split('/')[-2].replace('-', '_') + '.txt'

        try:
            book_response = requests.get(download_url)
            book_response.raise_for_status()
            with open(os.path.join(base_dir, book_title), 'w', encoding='utf-8') as f:
                f.write(book_response.text)
            print(f"Staženo: {book_title}")
        except Exception as e:
            print(f"Chyba při stahování {book_title}: {e}")

if __name__ == "__main__":
    download_czech_books()