import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
import os
from urllib.parse import urlsplit, unquote

def get_book_genre(book_id):
    """Получение жанров книги по её ID."""
    url = f'https://tululu.org/b{book_id}/'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    genre_tags = soup.find('span', class_='d_book').find_all('a')
    genres = [tag.get_text().strip() for tag in genre_tags]

    return genres

# Дополнение основного цикла для включения информации о жанрах
for book_id in range(1, 11):
    try:
        title, author = get_book_title_and_author(book_id)
        if title and author:
            filename = f"{title} - {author}"
            book_url = f'http://tululu.org/txt.php?id={book_id}'
            cover_image_url = f'https://tululu.org/shots/{book_id}.jpg'
            genres = get_book_genre(book_id)

            txt_filepath = download_txt(book_url, filename)
            img_filepath = download_image(cover_image_url)
            print(f"Книга '{title}' и её обложка скачаны: {txt_filepath}, {img_filepath}")
            print(f"Жанры книги: {', '.join(genres)}")
        else:
            print(f"Книга с ID {book_id} не найдена или ошибка в её данных.")
    except Exception as e:
        print(f"Ошибка при обработке книги с ID {book_id}: {e}")
