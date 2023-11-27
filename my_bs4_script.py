import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
import os
from urllib.parse import urlsplit, unquote

def parse_book_page(html_content):
    """Парсит страницу книги и возвращает данные о книге."""
    soup = BeautifulSoup(html_content, 'html.parser')

    title_author_tag = soup.find('h1')
    title, author = None, None
    if title_author_tag:
        title_author = title_author_tag.get_text().split('::')
        title = title_author[0].strip()
        author = title_author[1].strip()

    genre_tags = soup.find('span', class_='d_book').find_all('a')
    genres = [tag.get_text().strip() for tag in genre_tags]

    comments = []
    comment_tags = soup.find_all('div', class_='texts')
    for tag in comment_tags:
        comment = tag.find('span', class_='black')
        if comment:
            comments.append(comment.get_text().strip())

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

    response = requests.get(url)
    if response.status_code == 200:
        with open(file_path, 'wb') as file:
            file.write(response.content)
        return file_path
    else:
        raise Exception(f'Ошибка при скачивании файла: HTTP {response.status_code}')

def download_image(url, folder='images/'):
    """Скачивание изображения и сохранение его в указанной папке."""
    image_filename = unquote(urlsplit(url).path.split('/')[-1])
    safe_filename = sanitize_filename(image_filename)
    os.makedirs(folder, exist_ok=True)
    file_path = os.path.join(folder, safe_filename)

    response = requests.get(url)
    if response.status_code == 200:
        with open(file_path, 'wb') as file:
            file.write(response.content)
        return file_path
    else:
        raise Exception(f'Ошибка при скачивании изображения: HTTP {response.status_code}')

for book_id in range(1, 11):
    try:
        book_url = f'http://tululu.org/b{book_id}/'
        response = requests.get(book_url)
        if response.status_code == 200:
            book_data = parse_book_page(response.text)

            filename = f"{book_data['title']} - {book_data['author']}"
            txt_url = f'http://tululu.org/txt.php?id={book_id}'
            cover_url = f'https://tululu.org/shots/{book_id}.jpg'

            txt_filepath = download_txt(txt_url, filename)
            img_filepath = download_image(cover_url)
            print(f"Книга '{book_data['title']}' и её обложка скачаны: {txt_filepath}, {img_filepath}")
            print(f"Жанры книги: {', '.join(book_data['genres'])}")
            print(f"Комментарии к книге: {book_data['comments']}")
        else:
            print(f"Книга с ID {book_id} не найдена или ошибка в её данных.")
    except Exception as e:
        print(f"Ошибка при обработке книги с ID {book_id}: {e}")
