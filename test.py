import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
import os
from urllib.parse import urlsplit, unquote

def get_book_comments(book_id):
    """Получение комментариев к книге по её ID."""
    url = f'https://tululu.org/b{book_id}/'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    comments = []
    comment_tags = soup.find_all('div', class_='texts')

    for tag in comment_tags:
        comment = tag.find('span', class_='black')
        if comment:
            comments.append(comment.get_text().strip())

    return comments


# Пример использования
for book_id in range(1, 11):
    try:
        comments = get_book_comments(book_id)
        print(f"Комментарии к книге с ID {book_id}: {comments}")
    except Exception as e:
        print(f"Ошибка при обработке комментариев книги с ID {book_id}: {e}")
