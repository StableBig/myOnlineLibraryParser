import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

url = 'https://tululu.org/txt.php?id=32168'

response = requests.get(url, verify=False)

if response.status_code == 200:
    with open('Пески Марса.txt', 'wb') as file:
        file.write(response.content)
    print("Книга 'Пески Марса' успешно скачана!")
else:
    print("Ошибка при скачивании книги. Код ответа:", response.status_code)
