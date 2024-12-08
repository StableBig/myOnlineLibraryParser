import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os
import json
import sys
import argparse
from pathvalidate import sanitize_filename
import time


def check_for_redirect(response):
    if len(response.history) > 0:
        final_url = response.url.rstrip('/')
        if final_url == 'http://tululu.org':
            raise requests.HTTPError(f"Redirected to the main page: {final_url}")


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


def download_txt(book_id, filename, folder):
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
    folder_path = os.path.join(folder, 'images')
    os.makedirs(folder_path, exist_ok=True)
    file_path = os.path.join(folder_path, os.path.basename(url))

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
            check_for_redirect(response)
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
    parser = argparse.ArgumentParser(description='Скачивание книг с сайта tululu.org')
    parser.add_argument('--start_page', type=int, default=1, help='С какой страницы начинать скачивание книг')
    parser.add_argument('--end_page', type=int, default=1, help='На какой странице остановить скачивание книг')
    parser.add_argument('--dest_folder', type=str, default='.', help='Путь к каталогу для сохранения файлов')
    parser.add_argument('--skip_imgs', action='store_true', help='Не скачивать обложки книг')
    parser.add_argument('--skip_txt', action='store_true', help='Не скачивать текстовые файлы книг')
    args = parser.parse_args()

    base_category_url = 'http://tululu.org/l55/'
    book_links = get_all_book_links_from_all_pages(base_category_url, start_page=args.start_page, end_page=args.end_page)

    books = []
    for book_url in book_links:
        try:
            response = requests.get(book_url)
            check_for_redirect(response)
            response.raise_for_status()

            book_details = parse_book_page(response.text, book_url)
            book_id = book_url.split('/')[-2].replace('b', '')
            filename = f"{book_details['title']} - {book_details['author']}"

            if not args.skip_txt:
                try:
                    txt_filepath = download_txt(book_id, filename, args.dest_folder)
                except requests.exceptions.RequestException as e:
                    print(f"Ошибка при скачивании текста для книги {filename}: {e}", file=sys.stderr)
                    continue
            else:
                txt_filepath = None

            if book_details['cover_url'] and not args.skip_imgs:
                try:
                    img_filepath = download_image(book_details['cover_url'], args.dest_folder)
                except requests.exceptions.RequestException as e:
                    print(f"Ошибка при скачивании обложки для книги {filename}: {e}", file=sys.stderr)
            else:
                img_filepath = None

            book_details['txt_path'] = txt_filepath
            book_details['img_path'] = img_filepath
            books.append(book_details)

            print(f"Книга '{book_details['title']}' скачана.")
        except requests.RequestException as e:
            print(f"Ошибка при обработке книги {book_url}: {e}", file=sys.stderr)

    with open(os.path.join(args.dest_folder, 'books.json'), 'w', encoding='utf-8') as file:
        json.dump(books, file, ensure_ascii=False, indent=4)
    print(f"Информация о книгах сохранена в books.json")


if __name__ == "__main__":
    main()
