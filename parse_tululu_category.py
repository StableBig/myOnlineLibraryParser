import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


def check_for_redirect(response):
    if response.url == 'http://tululu.org/':
        raise requests.HTTPError("Redirected to the main page, resource not found.")


def get_first_book_link(category_url):
    try:
        response = requests.get(category_url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        book_card = soup.find('div', class_='bookimage')
        if not book_card:
            raise ValueError("Не удалось найти карточку книги.")

        link_tag = book_card.find('a')
        if not link_tag:
            raise ValueError("Не удалось найти ссылку на книгу.")

        book_link = urljoin(category_url, link_tag['href'])
        return book_link

    except requests.RequestException as e:
        print(f"Ошибка при запросе страницы категории {category_url}: {e}")
    except Exception as e:
        print(f"Ошибка при парсинге страницы: {e}")


def main():
    category_url = 'http://tululu.org/l55/'
    first_book_link = get_first_book_link(category_url)
    if first_book_link:
        print(f"Ссылка на первую книгу: {first_book_link}")


if __name__ == "__main__":
    main()
