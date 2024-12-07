import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


def check_for_redirect(response):
    if response.url == 'http://tululu.org/':
        raise requests.HTTPError("Redirected to the main page, resource not found.")


def get_all_book_links_from_page(category_url):
    try:
        response = requests.get(category_url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        book_cards = soup.find_all('div', class_='bookimage')
        if not book_cards:
            raise ValueError("Не удалось найти карточки книг.")

        book_links = []
        for card in book_cards:
            link_tag = card.find('a')
            if link_tag:
                book_link = urljoin(category_url, link_tag['href'])
                book_links.append(book_link)

        return book_links

    except requests.RequestException as e:
        print(f"Ошибка при запросе страницы категории {category_url}: {e}")
    except Exception as e:
        print(f"Ошибка при парсинге страницы: {e}")


def main():
    category_url = 'http://tululu.org/l55/'
    book_links = get_all_book_links_from_page(category_url)
    if book_links:
        print(f"Найдено {len(book_links)} ссылок на книги.")
        for link in book_links:
            print(link)


if __name__ == "__main__":
    main()
