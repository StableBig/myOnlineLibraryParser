import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
import os
from urllib.parse import urlsplit, unquote, urljoin
import argparse
import time
import sys


def check_for_redirect(response):
    """Проверяет ответ на редирект и выбрасывает исключение при необходимости."""
    if response.url == 'http://tululu.org/':
        raise requests.HTTPError("Redirected to the main page, resource not found.")


def parse_book_page(html_content, base_url):
    """Парсит страницу книги и возвращает данные о книге."""
    soup = BeautifulSoup(html_content, 'html.parser')

    title_author = None
    genres = []
    comments = []
    cover_url = None

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

    try:
        cover_tag = soup.find('div', class_='bookimage').find('img')
        if cover_tag:
            cover_url = urljoin(base_url, cover_tag['src'])
    except (AttributeError, KeyError) as e:
        print(f"Ошибка при извлечении обложки: {e}", file=sys.stderr)

    return {
        'title': title,
        'author': author,
        'genres': genres,
        'comments': comments,
        'cover_url': cover_url
    }


def download_txt(book_id, filename, folder='books/'):
    """Скачивание текстового файла и сохранение его под определенным именем."""
    safe_filename = sanitize_filename(filename) + '.txt'
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
    """Скачивание изображения и сохранение его в указанной папке."""
    image_filename = unquote(urlsplit(url).path.split('/')[-1])
    safe_filename = sanitize_filename(image_filename)
    os.makedirs(folder, exist_ok=True)
    file_path = os.path.join(folder, safe_filename)

    response = requests.get(url)
    check_for_redirect(response)
    response.raise_for_status()

    with open(file_path, 'wb') as file:
        file.write(response.content)
    return file_path


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
                    check_for_redirect(response)
                    response.raise_for_status()
                    break
                except requests.exceptions.HTTPError as e:
                    print(f"HTTP ошибка при обработке книги с ID {book_id}: {e}", file=sys.stderr)
                    break
                except requests.exceptions.ConnectionError as e:
                    print(f"Ошибка соединения при доступе к книге с ID {book_id}: {e}. Повтор через 5 секунд...", file=sys.stderr)
                    time.sleep(5)

            book_details = parse_book_page(response.text, book_url)
            filename = f"{book_details['title']} - {book_details['author']}"

            try:
                txt_filepath = download_txt(book_id, filename)
            except requests.exceptions.HTTPError as e:
                print(f"HTTP ошибка при скачивании текста для ID {book_id}: {e}", file=sys.stderr)
                txt_filepath = None
            except requests.exceptions.ConnectionError as e:
                print(f"Ошибка соединения при скачивании текста для ID {book_id}: {e}. Повтор через 5 секунд...", file=sys.stderr)
                time.sleep(5)
                txt_filepath = None

            if book_details['cover_url']:
                try:
                    img_filepath = download_image(book_details['cover_url'])
                except requests.exceptions.HTTPError as e:
                    print(f"HTTP ошибка при скачивании изображения {book_details['cover_url']}: {e}", file=sys.stderr)
                    img_filepath = None
                except requests.exceptions.ConnectionError as e:
                    print(f"Ошибка соединения при скачивании изображения {book_details['cover_url']}: {e}. Повтор через 5 секунд...", file=sys.stderr)
                    time.sleep(5)
                    img_filepath = None
            else:
                img_filepath = None

            if txt_filepath and img_filepath:
                print(f"Книга '{book_details['title']}' и её обложка скачаны: {txt_filepath}, {img_filepath}")
                print(f"Жанры книги: {', '.join(book_details['genres'])}")
                print(f"Комментарии к книге: {book_details['comments']}")

        except requests.RequestException as e:
            print(f"Ошибка при запросе данных книги с ID {book_id}: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
