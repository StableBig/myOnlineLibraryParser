import requests
from urllib.parse import urljoin
import os
import json
import sys
import argparse
import time
from bs4 import BeautifulSoup
from download_tools import check_for_redirect, parse_book_page, download_txt, download_image


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
