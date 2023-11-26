import os
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

os.makedirs('books', exist_ok=True)

for book_id in range(1, 11):
    url = f'https://tululu.org/txt.php?id={book_id}'

    try:
        response = requests.get(url)

        if response.status_code == 200:
            # Формируем путь к файлу
            file_path = os.path.join('books', f'book_{book_id}.txt')

            # Сохраняем содержимое в файл
            with open(file_path, 'wb') as file:
                file.write(response.content)
            print(f"Книга {book_id} успешно скачана!")
        else:
            print(f"Ошибка при скачивании книги {book_id}. Код ответа: {response.status_code}")

    except requests.RequestException as e:
        print(f"Ошибка при скачивании книги {book_id}: {e}")
