import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def get_book_cover_image_url(book_id):
    """Получение URL обложки книги по её ID."""
    url = f'https://tululu.org/b{book_id}/'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    image_tag = soup.find('div', class_='bookimage').find('img')
    if image_tag and image_tag.get('src'):
        image_url = urljoin(url, image_tag['src'])
        return image_url
    else:
        return None

for book_id in range(1, 11):
    try:
        image_url = get_book_cover_image_url(book_id)
        if image_url:
            print(f"Обложка книги с ID {book_id}: {image_url}")
        else:
            print(f"Обложка для книги с ID {book_id} не найдена.")
    except Exception as e:
        print(f"Ошибка при обработке книги с ID {book_id}: {e}")
