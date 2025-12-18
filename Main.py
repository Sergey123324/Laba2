import re
import unittest

UTC_PATTERN = re.compile(
    r'^([01]\d|2[0-3]):([0-5]\d):([0-5]\d)(?:\.(\d{1,6}))?(Z)?$'
)


class UTCTimeParser:
    @staticmethod
    def find_in_text(text):
        return [match.group() for match in UTC_PATTERN.finditer(text)]

    @staticmethod
    def find_in_file(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return UTCTimeParser.find_in_text(f.read())
        except:
            return []

    @staticmethod
    def find_in_url(url):
        try:
            from urllib.request import urlopen
            with urlopen(url) as response:
                return UTCTimeParser.find_in_text(response.read().decode('utf-8'))
        except:
            return []


def main():
    print("Выберите источник:")
    print("1 - Текст\n2 - Файл\n3 - URL")
    choice = input("Ваш выбор: ").strip()

    parser = UTCTimeParser()

    if choice == "1":
        text = input("Введите текст: ")
        results = parser.find_in_text(text)
    elif choice == "2":
        path = input("Путь к файлу: ")
        results = parser.find_in_file(path)
    elif choice == "3":
        url = input("URL: ")
        results = parser.find_in_url(url)
    else:
        print("Неверный выбор")
        return

    print(f"\nНайдено {len(results)} совпадений:")
    for i, time in enumerate(results, 1):
        print(f"{i}. {time}")


