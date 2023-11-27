import requests
from bs4 import BeautifulSoup


def get_book_title_and_author(book_id):
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
        return "Название или автор не найдены"


book_id = 1
title, author = get_book_title_and_author(book_id)
print(f"Название книги: {title}, Автор: {author}")
