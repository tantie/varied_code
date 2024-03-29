import requests
import json
import os
from time import sleep

# Убедимся, что папка для изображений существует
if not os.path.exists('img'):
    os.makedirs('img')

# JSON-файл
with open('data.json', 'r', encoding='utf-8') as file:
    data = json.load(file)


def download_image(url, filename):
    # Проверка, существует ли файл
    if os.path.exists(filename):
        print(f"Файл {filename} уже существует. Пропускаем.")
        return

    # Количество попыток
    attempts = 5
    for attempt in range(1, attempts + 1):
        try:
            # Пауза перед загрузкой чтобы не забанили
            sleep(attempt * 1)  # Увеличиваем паузу с каждой попыткой
            response = requests.get(url, timeout=10)  # Установим таймаут
            if response.status_code == 200:
                with open(filename, 'wb') as img:
                    img.write(response.content)
                print(f"Загружено: {filename}")
                break
            else:
                print(f"Ошибка при загрузке изображения {url}. Статус: {response.status_code}")
        except requests.exceptions.ConnectionError as e:
            print(f"Ошибка соединения при попытке {attempt}: {e}")
            if attempt == attempts:
                print("Превышено количество попыток загрузки. Переход к следующему изображению.")

# Перебор JSON и скачивание
for state, tests in data.items():
    for test in tests:
        for question in test['test']:
            if 'image' in question:
                image_url = question['image']
                filename = os.path.join('img', os.path.basename(image_url))
                download_image(image_url, filename)

print("Скачивание завершено.")
