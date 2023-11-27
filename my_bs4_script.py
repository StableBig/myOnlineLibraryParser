import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
import os

def get_book_title_and_author(book_id):
    """Получение названия и автора книги по её ID."""
    url = f'https://tululu.org/b{book_id}/'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    title_author_tag = soup.find('h1')
    if title_author_tag:
        title_author = title_author_tag.get_text().split('::')
        title = title_author[0].strip()
        author = title_author[1].strip()
        return title, author
    else:
        return None, None

def download_txt(url, filename, folder='books/'):
    """Скачивание текстового файла и сохранение его под определенным именем."""
    safe_filename = sanitize_filename(filename) + '.txt'
    os.makedirs(folder, exist_ok=True)
    file_path = os.path.join(folder, safe_filename)

    response = requests.get(url)
    if response.status_code == 200:
        with open(file_path, 'wb') as file:
            file.write(response.content)
        return file_path
    else:
        raise Exception(f'Ошибка при скачивании файла: HTTP {response.status_code}')

# Пример использования
for book_id in range(1, 11):
    try:
        title, author = get_book_title_and_author(book_id)
        if title and author:
            filename = f"{title} - {author}"
            book_url = f'http://tululu.org/txt.php?id={book_id}'

            filepath = download_txt(book_url, filename)
            print(f"Книга '{title}' скачана и сохранена в: {filepath}")
        else:
            print(f"Книга с ID {book_id} не найдена или ошибка в её данных.")
    except Exception as e:
        print(f"Ошибка при обработке книги с ID {book_id}: {e}")
