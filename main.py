import requests
import os
from requests.exceptions import HTTPError
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def check_for_redirect(response):
    """Проверяет, произошел ли редирект при запросе."""
    if response.history:
        raise HTTPError('Redirection detected')

os.makedirs('books', exist_ok=True)

for book_id in range(1, 11):
    url = f'https://tululu.org/txt.php?id={book_id}'

    try:
        response = requests.get(url, verify=False)
        check_for_redirect(response)

        file_path = os.path.join('books', f'book_{book_id}.txt')
        with open(file_path, 'wb') as file:
            file.write(response.content)
        print(f"Книга {book_id} успешно скачана!")

    except HTTPError as e:
        print(f"Книга {book_id} не найдена: {e}")
    except requests.RequestException as e:
        print(f"Ошибка при скачивании книги {book_id}: {e}")
