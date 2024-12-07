import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os
import json
import time
import sys
from pathvalidate import sanitize_filename


def check_for_redirect(response):
    if response.url == 'http://tululu.org/':
        raise requests.HTTPError("Redirected to the main page, resource not found.")


def parse_book_page(html_content, base_url):
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


def download_txt(book_id, filename, folder='books/'):
    safe_filename = sanitize_filename(f'{filename}.txt')
    os.makedirs(folder, exist_ok=True)
    file_path = os.path.join(folder, safe_filename)

    params = {'id': book_id}
    response = requests.get('http://tululu.org/txt.php', params=params)
    check_for_redirect(response)
    response.raise_for_status()

    with open(file_path, 'wb') as file:
        file.write(response.content)
    return file_path


def download_image(url, folder='images/'):
    os.makedirs(folder, exist_ok=True)
    file_path = os.path.join(folder, os.path.basename(url))

    response = requests.get(url)
    check_for_redirect(response)
    response.raise_for_status()

    with open(file_path, 'wb') as file:
        file.write(response.content)
    return file_path


def get_all_book_links_from_all_pages(base_category_url, start_page=1, end_page=1):
    all_book_links = []
    for page_number in range(start_page, end_page + 1):
        category_url = f'{base_category_url}{page_number}/'
        print(f"Парсинг страницы: {category_url}")
        try:
            response = requests.get(category_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            book_cards = soup.select('div.bookimage a')
            for link_tag in book_cards:
                book_link = urljoin(category_url, link_tag['href'])
                all_book_links.append(book_link)
        except requests.RequestException as e:
            print(f"Ошибка при запросе страницы {category_url}: {e}", file=sys.stderr)
    return all_book_links


def main():
    base_category_url = 'http://tululu.org/l55/'
    book_links = get_all_book_links_from_all_pages(base_category_url, start_page=1, end_page=1)

    book_metadata = []
    for book_url in book_links:
        try:
            response = requests.get(book_url)
            check_for_redirect(response)
            response.raise_for_status()

            book_details = parse_book_page(response.text, book_url)
            book_id = book_url.split('/')[-2].replace('b', '')
            filename = f"{book_details['title']} - {book_details['author']}"

            try:
                txt_filepath = download_txt(book_id, filename)
            except requests.exceptions.RequestException as e:
                print(f"Ошибка при скачивании текста для книги {filename}: {e}", file=sys.stderr)
                continue

            if book_details['cover_url']:
                try:
                    img_filepath = download_image(book_details['cover_url'])
                except requests.exceptions.RequestException as e:
                    print(f"Ошибка при скачивании обложки для книги {filename}: {e}", file=sys.stderr)
            else:
                img_filepath = None

            book_details['txt_path'] = txt_filepath
            book_details['img_path'] = img_filepath
            book_metadata.append(book_details)

            print(f"Книга '{book_details['title']}' скачана.")
        except requests.RequestException as e:
            print(f"Ошибка при обработке книги {book_url}: {e}", file=sys.stderr)

    with open('books.json', 'w', encoding='utf-8') as file:
        json.dump(book_metadata, file, ensure_ascii=False, indent=4)
    print(f"Информация о книгах сохранена в books.json")


if __name__ == "__main__":
    main()
