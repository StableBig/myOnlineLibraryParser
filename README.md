# Tululu Book Downloader

Этот скрипт позволяет скачивать книги с сайта [tululu.org](https://tululu.org/), включая тексты книг, их обложки, жанры и комментарии.

## Особенности

- Скачивание текстов книг и обложек.
- Извлечение информации о названии книги, авторе, жанрах и комментариях.
- Возможность выбора диапазона ID книг для скачивания.

## Установка

Для использования скрипта убедитесь, что у вас установлен Python версии 3.6 или выше.

1. Склонируйте репозиторий:

`git clone https://github.com/StableBig/myOnlineLibraryParser.git`

2. Перейдите в каталог проекта:

`cd myOnlineLibraryParser`


## Использование

Запустите скрипт с указанием начального и конечного ID книг:

`python3 my_bs4_script.py [start_id] [end_id]`


где `[start_id]` и `[end_id]` — начальный и конечный ID книг, которые вы хотите скачать.

Например:

`python my_bs4_script.py 20 30`

Эта команда скачает книги с ID от 20 до 30.
