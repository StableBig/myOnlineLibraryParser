import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os
import sys
from pathvalidate import sanitize_filename


def check_for_redirect(response):
    """Проверяет ответ на редирект и выбрасывает исключение при необходимости."""
    if len(response.history) > 0:
        final_url = response.url.rstrip('/')
        if final_url == 'http://tululu.org':
            raise requests.HTTPError(f"Redirected to the main page: {final_url}")


def parse_book_page(html_content, base_url):
    """Извлекает данные книги со страницы."""
    soup = BeautifulSoup(html_content, 'html.parser')

    try:
        title_author_text = soup.select_one('h1').get_text()
        title, author = map(str.strip, title_author_text.split('::'))
    except (AttributeError, ValueError) as e:
        print(f"Ошибка при извлечении названия или автора: {e}", file=sys.stderr)
        title, author = "Unknown Title", "Unknown Author"

    genres = [genre.get_text(strip=True) for genre in soup.select('span.d_book a')]
    comments = [comment.get_text(strip=True) for comment in soup.select('div.texts span.black')]

    try:
        cover_tag = soup.select_one('div.bookimage img')
        cover_url = urljoin(base_url, cover_tag['src']) if cover_tag else None
    except (AttributeError, KeyError) as e:
        print(f"Ошибка при извлечении обложки: {e}", file=sys.stderr)
        cover_url = None

    return {
        'title': title,
        'author': author,
        'genres': genres,
        'comments': comments,
        'cover_url': cover_url
    }


def download_txt(book_id, filename, folder):
    """Скачивает текст книги."""
    safe_filename = sanitize_filename(f'{filename}.txt')
    folder_path = os.path.join(folder, 'books')
    os.makedirs(folder_path, exist_ok=True)
    file_path = os.path.join(folder_path, safe_filename)

    params = {'id': book_id}
    response = requests.get('http://tululu.org/txt.php', params=params)
    check_for_redirect(response)
    response.raise_for_status()

    with open(file_path, 'wb') as file:
        file.write(response.content)
    return file_path


def download_image(url, folder):
    """Скачивает обложку книги."""
    folder_path = os.path.join(folder, 'images')
    os.makedirs(folder_path, exist_ok=True)
    file_path = os.path.join(folder_path, os.path.basename(url))

    response = requests.get(url)
    check_for_redirect(response)
    response.raise_for_status()

    with open(file_path, 'wb') as file:
        file.write(response.content)
    return file_path
