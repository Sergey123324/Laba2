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


class TestUTCTime(unittest.TestCase):
    def test_valid_times(self):
        valid = ["00:00:00", "23:59:59", "12:30:45Z", "12:30:45.123456Z"]
        for time in valid:
            self.assertTrue(UTC_PATTERN.fullmatch(time), f"Должно совпадать: {time}")

    def test_invalid_times(self):
        invalid = ["24:00:00", "12:60:00", "12:00:60", "12:00:00.1234567"]
        for time in invalid:
            self.assertIsNone(UTC_PATTERN.fullmatch(time), f"Не должно совпадать: {time}")

    def test_find_in_text(self):
        text = "Время: 14:30:00Z и 23:59:59.999"
        results = UTCTimeParser.find_in_text(text)
        self.assertEqual(len(results), 2)
        self.assertIn("14:30:00Z", results)


if __name__ == "__main__":
    print("Запуск: 1 - программа, 2 - тесты")
    if input("Выбор: ") == "2":
        unittest.main(verbosity=2)
    else:
        main()