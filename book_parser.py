import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
import os
from urllib.parse import urlsplit, unquote
import argparse
import time
import sys


def parse_book_page(html_content):
    """Парсит страницу книги и возвращает данные о книге."""
    soup = BeautifulSoup(html_content, 'html.parser')

    title_author = None
    genres = []
    comments = []

    try:
        title_author_tag = soup.find('h1')
        if title_author_tag:
            title_author = title_author_tag.get_text().split('::')
            title = title_author[0].strip()
            author = title_author[1].strip() if len(title_author) > 1 else "Unknown Author"
    except (AttributeError, IndexError) as e:
        print(f"Ошибка при извлечении названия или автора: {e}", file=sys.stderr)
        title, author = "Unknown Title", "Unknown Author"

    try:
        genre_tags = soup.find('span', class_='d_book').find_all('a')
        genres = [tag.get_text().strip() for tag in genre_tags]
    except AttributeError as e:
        print(f"Ошибка при извлечении жанров: {e}", file=sys.stderr)

    try:
        comment_tags = soup.find_all('div', class_='texts')
        for tag in comment_tags:
            comment = tag.find('span', class_='black')
            if comment:
                comments.append(comment.get_text().strip())
    except AttributeError as e:
        print(f"Ошибка при извлечении комментариев: {e}", file=sys.stderr)

    return {
        'title': title,
        'author': author,
        'genres': genres,
        'comments': comments
    }


def download_txt(url, filename, folder='books/'):
    """Скачивание текстового файла и сохранение его под определенным именем."""
    safe_filename = sanitize_filename(filename) + '.txt'
    os.makedirs(folder, exist_ok=True)
    file_path = os.path.join(folder, safe_filename)

    while True:
        try:
            response = requests.get(url)
            response.raise_for_status()
            with open(file_path, 'wb') as file:
                file.write(response.content)
            return file_path
        except requests.exceptions.HTTPError as e:
            print(f"HTTP ошибка при скачивании {url}: {e}", file=sys.stderr)
            return None
        except requests.exceptions.ConnectionError as e:
            print(f"Ошибка соединения при скачивании {url}: {e}. Повтор через 5 секунд...", file=sys.stderr)
            time.sleep(5)


def download_image(url, folder='images/'):
    """Скачивание изображения и сохранение его в указанной папке."""
    image_filename = unquote(urlsplit(url).path.split('/')[-1])
    safe_filename = sanitize_filename(image_filename)
    os.makedirs(folder, exist_ok=True)
    file_path = os.path.join(folder, safe_filename)

    while True:
        try:
            response = requests.get(url)
            response.raise_for_status()
            with open(file_path, 'wb') as file:
                file.write(response.content)
            return file_path
        except requests.exceptions.HTTPError as e:
            print(f"HTTP ошибка при скачивании изображения {url}: {e}", file=sys.stderr)
            return None
        except requests.exceptions.ConnectionError as e:
            print(f"Ошибка соединения при скачивании изображения {url}: {e}. Повтор через 5 секунд...", file=sys.stderr)
            time.sleep(5)


def main():
    parser = argparse.ArgumentParser(description="Скачивание книг с сайта tululu.org")
    parser.add_argument('start_id', type=int, help="ID первой книги для скачивания")
    parser.add_argument('end_id', type=int, help="ID последней книги для скачивания")
    args = parser.parse_args()

    for book_id in range(args.start_id, args.end_id + 1):
        try:
            book_url = f'http://tululu.org/b{book_id}/'
            while True:
                try:
                    response = requests.get(book_url)
                    response.raise_for_status()
                    break
                except requests.exceptions.HTTPError as e:
                    print(f"HTTP ошибка при обработке книги с ID {book_id}: {e}", file=sys.stderr)
                    break
                except requests.exceptions.ConnectionError as e:
                    print(f"Ошибка соединения при доступе к книге с ID {book_id}: {e}. Повтор через 5 секунд...", file=sys.stderr)
                    time.sleep(5)

            book_data = parse_book_page(response.text)
            filename = f"{book_data['title']} - {book_data['author']}"
            txt_url = f'http://tululu.org/txt.php?id={book_id}'
            cover_url = f'https://tululu.org/shots/{book_id}.jpg'

            txt_filepath = download_txt(txt_url, filename)
            img_filepath = download_image(cover_url)
            if txt_filepath and img_filepath:
                print(f"Книга '{book_data['title']}' и её обложка скачаны: {txt_filepath}, {img_filepath}")
                print(f"Жанры книги: {', '.join(book_data['genres'])}")
                print(f"Комментарии к книге: {book_data['comments']}")

        except requests.RequestException as e:
            print(f"Ошибка при запросе данных книги с ID {book_id}: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
