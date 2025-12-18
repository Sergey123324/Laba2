import re
from typing import List, Tuple, Optional, Dict, Set
from dataclasses import dataclass
from enum import Enum


class RomanNumeralValidation(Enum):
    VALID = "VALID"
    INVALID_FORMAT = "INVALID_FORMAT"
    INVALID_ORDER = "INVALID_ORDER"
    INVALID_REPETITION = "INVALID_REPETITION"
    INVALID_SUBTRACTION = "INVALID_SUBTRACTION"
    EMPTY = "EMPTY"


@dataclass
class RomanNumeralResult:
    numeral: str
    value: Optional[int] = None
    status: RomanNumeralValidation = RomanNumeralValidation.VALID
    position: Optional[Tuple[int, int]] = None
    error_details: Optional[str] = None


class RomanNumerals:

    ROMAN_VALUES = {
        'M': 1000,
        'D': 500,
        'C': 100,
        'L': 50,
        'X': 10,
        'V': 5,
        'I': 1
    }

    ORDER = ['M', 'D', 'C', 'L', 'X', 'V', 'I']

    SUBTRACTION_RULES = {
        'I': ['V', 'X'],
        'X': ['L', 'C'],
        'C': ['D', 'M'],
        'V': [],
        'L': [],
        'D': [],
        'M': []
    }

    MAX_REPETITIONS = {
        'I': 3,
        'X': 3,
        'C': 3,
        'M': 3,
        'V': 1,
        'L': 1,
        'D': 1
    }

    INVALID_COMBINATIONS = {
        'IIII', 'VV', 'XXXX', 'LL', 'CCCC', 'DD', 'MMMMM',
        'IL', 'IC', 'ID', 'IM',
        'XD', 'XM',
        'VX', 'VL', 'VC', 'VD', 'VM',
        'LC', 'LD', 'LM',
        'DM',
        'IIV', 'IIX', 'XXL', 'XXC', 'CCD', 'CCM',
    }

    def __init__(self):
        self.roman_pattern = re.compile(
            r'(?<!\w)'  
            r'[MDCLXVI]+' 
            r'(?!\w)'
        )

        self.strict_pattern = re.compile(
            r'^'
            r'M{0,3}'  
            r'(CM|CD|D?C{0,3})' 
            r'(XC|XL|L?X{0,3})'  
            r'(IX|IV|V?I{0,3})' 
            r'$'
        )

    def validate_roman_numeral(self, roman: str) -> RomanNumeralResult:
        roman = roman.strip().upper()

        if not roman:
            return RomanNumeralResult(
                numeral=roman,
                status=RomanNumeralValidation.EMPTY,
                error_details="Пустая строка"
            )

        invalid_chars = [c for c in roman if c not in self.ROMAN_VALUES]
        if invalid_chars:
            return RomanNumeralResult(
                numeral=roman,
                status=RomanNumeralValidation.INVALID_FORMAT,
                error_details=f"Недопустимые символы: {', '.join(set(invalid_chars))}"
            )

        if not self.strict_pattern.match(roman):
            return RomanNumeralResult(
                numeral=roman,
                status=RomanNumeralValidation.INVALID_FORMAT,
                error_details="Не соответствует структуре римских чисел"
            )

        for invalid in self.INVALID_COMBINATIONS:
            if invalid in roman:
                return RomanNumeralResult(
                    numeral=roman,
                    status=RomanNumeralValidation.INVALID_SUBTRACTION,
                    error_details=f"Запрещенная комбинация: {invalid}"
                )

        for symbol, max_rep in self.MAX_REPETITIONS.items():
            pattern = re.compile(f'{symbol}{{{max_rep + 1},}}')
            if pattern.search(roman):
                return RomanNumeralResult(
                    numeral=roman,
                    status=RomanNumeralValidation.INVALID_REPETITION,
                    error_details=f"Символ '{symbol}' повторяется более {max_rep} раз"
                )

        prev_value = float('inf')
        i = 0
        n = len(roman)

        while i < n:
            current_char = roman[i]
            current_value = self.ROMAN_VALUES[current_char]

            if i + 1 < n:
                next_char = roman[i + 1]
                next_value = self.ROMAN_VALUES[next_char]

                if current_value < next_value:
                    if next_char not in self.SUBTRACTION_RULES.get(current_char, []):
                        return RomanNumeralResult(
                            numeral=roman,
                            status=RomanNumeralValidation.INVALID_SUBTRACTION,
                            error_details=f"Некорректное вычитание: {current_char}{next_char}"
                        )

                    if i + 2 < n and roman[i + 2] == current_char:
                        return RomanNumeralResult(
                            numeral=roman,
                            status=RomanNumeralValidation.INVALID_SUBTRACTION,
                            error_details=f"Вычитаемый символ '{current_char}' не может повторяться"
                        )

                    if next_value > current_value * 10:
                        return RomanNumeralResult(
                            numeral=roman,
                            status=RomanNumeralValidation.INVALID_SUBTRACTION,
                            error_details=f"Вычитание слишком большого значения: {current_char}{next_char}"
                        )

                    value = next_value - current_value
                    i += 2
                else:
                    value = current_value
                    i += 1
            else:
                value = current_value
                i += 1

            if value > prev_value:
                return RomanNumeralResult(
                    numeral=roman,
                    status=RomanNumeralValidation.INVALID_ORDER,
                    error_details="Некорректный порядок значений"
                )

            prev_value = value

        arabic_value = self.roman_to_arabic(roman)
        return RomanNumeralResult(
            numeral=roman,
            value=arabic_value,
            status=RomanNumeralValidation.VALID
        )

    def roman_to_arabic(self, roman: str) -> int:
        total = 0
        prev_value = 0

        for char in reversed(roman.upper()):
            value = self.ROMAN_VALUES[char]
            if value < prev_value:
                total -= value
            else:
                total += value
            prev_value = value

        return total

    def arabic_to_roman(self, num: int) -> str:
        if not 1 <= num <= 3999:
            raise ValueError("Число должно быть в диапазоне 1-3999")

        conversions = [
            (1000, 'M'),
            (900, 'CM'),
            (500, 'D'),
            (400, 'CD'),
            (100, 'C'),
            (90, 'XC'),
            (50, 'L'),
            (40, 'XL'),
            (10, 'X'),
            (9, 'IX'),
            (5, 'V'),
            (4, 'IV'),
            (1, 'I')
        ]

        result = []
        for value, symbol in conversions:
            while num >= value:
                result.append(symbol)
                num -= value

        return ''.join(result)

    def find_roman_numerals_in_text(self, text: str, strict: bool = True) -> List[RomanNumeralResult]:

        results = []

        if strict:
            matches = self.strict_pattern.finditer(text.upper())
        else:
            matches = self.roman_pattern.finditer(text.upper())

        for match in matches:
            roman_num = match.group()
            start, end = match.span()

            if strict:
                validation_result = RomanNumeralResult(
                    numeral=roman_num,
                    value=self.roman_to_arabic(roman_num),
                    status=RomanNumeralValidation.VALID,
                    position=(start, end)
                )
            else:
                validation_result = self.validate_roman_numeral(roman_num)
                validation_result.position = (start, end)

            results.append(validation_result)

        return results

    def find_and_convert_in_text(self, text: str) -> List[Dict]:
        results = []
        roman_results = self.find_roman_numerals_in_text(text, strict=True)

        for roman_result in roman_results:
            if roman_result.status == RomanNumeralValidation.VALID:
                results.append({
                    'roman': roman_result.numeral,
                    'arabic': roman_result.value,
                    'position': roman_result.position,
                    'text_context': self._get_context(text, roman_result.position)
                })

        return results

    def _get_context(self, text: str, position: Tuple[int, int], context_chars: int = 20) -> str:
        start, end = position
        context_start = max(0, start - context_chars)
        context_end = min(len(text), end + context_chars)

        context = text[context_start:context_end]

        if context_start > 0:
            context = "..." + context
        if context_end < len(text):
            context = context + "..."

        offset = 3 if context_start > 0 else 0
        marked = (context[:start - context_start + offset] +
                  ">>>" + context[start - context_start + offset:end - context_start + offset] + "<<<" +
                  context[end - context_start + offset:])

        return marked

    def analyze_text_file(self, file_path: str) -> Dict:
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
        except UnicodeDecodeError:
            with open(file_path, 'r', encoding='cp1251') as file:
                text = file.read()

        all_candidates = self.find_roman_numerals_in_text(text, strict=False)
        valid_numerals = [r for r in all_candidates if r.status == RomanNumeralValidation.VALID]

        return {
            'total_characters': len(text),
            'total_lines': text.count('\n') + 1,
            'candidates_found': len(all_candidates),
            'valid_numerals': len(valid_numerals),
            'numerals': [{
                'roman': r.numeral,
                'arabic': r.value,
                'line': text[:r.position[0]].count('\n') + 1 if r.position else None,
                'position': r.position
            } for r in valid_numerals],
            'validation_stats': {
                status.value: len([r for r in all_candidates if r.status == status])
                for status in RomanNumeralValidation
            }
        }


def interactive_demo():
    roman = RomanNumerals()

    print("=" * 60)
    print("РИМСКИЕ ЧИСЛА: ПРОВЕРКА И ПОИСК")
    print("=" * 60)

    while True:
        print("\nВыберите действие:")
        print("1. Проверить одно римское число")
        print("2. Конвертировать арабское число в римское")
        print("3. Найти римские числа в тексте")
        print("4. Проанализировать текстовый файл")
        print("5. Примеры корректных и некорректных чисел")
        print("6. Тестовый прогон")
        print("0. Выход")

        choice = input("\nВаш выбор: ").strip()

        if choice == '0':
            print("До свидания!")
            break

        elif choice == '1':
            numeral = input("Введите римское число: ").strip()
            result = roman.validate_roman_numeral(numeral)

            print(f"\nРезультат проверки: {result.numeral}")
            print(f"Статус: {result.status.value}")

            if result.status == RomanNumeralValidation.VALID:
                print(f"Арабское значение: {result.value}")
                print(f"Римское: {result.numeral} = {result.value}")
            else:
                print(f"Ошибка: {result.error_details}")

        elif choice == '2':
            try:
                arabic = int(input("Введите арабское число (1-3999): ").strip())
                roman_num = roman.arabic_to_roman(arabic)
                print(f"\n{arabic} = {roman_num}")

                back_to_arabic = roman.roman_to_arabic(roman_num)
                print(f"Обратная проверка: {roman_num} = {back_to_arabic}")

            except ValueError as e:
                print(f"Ошибка: {e}")

        elif choice == '3':
            text = input("Введите текст для анализа:\n").strip()
            if not text:
                print("Используем тестовый текст...")
                text = """
                В Древнем Риме год MMXXIV (2024) был бы записан так.
                Глава I, раздел III, пункт IV.
                Некорректные числа: XXXX, VX, IC, IIX.
                Король Людовик XIV (14) правил в XVII (17) веке.
                Популярные фильмы: Star Wars: Episode I, II, III, IV, V, VI.
                """
                print(f"Текст: {text}")

            results = roman.find_and_convert_in_text(text)

            if results:
                print(f"\nНайдено {len(results)} корректных римских чисел:")
                for i, result in enumerate(results, 1):
                    print(f"\n{i}. {result['roman']} = {result['arabic']}")
                    print(f"   Контекст: {result['text_context']}")
            else:
                print("\nКорректных римских чисел не найдено.")

        elif choice == '4':
            file_path = input("Введите путь к файлу: ").strip()
            try:
                analysis = roman.analyze_text_file(file_path)

                print(f"\nАнализ файла:")
                print(f"Всего символов: {analysis['total_characters']}")
                print(f"Строк: {analysis['total_lines']}")
                print(f"Найдено кандидатов: {analysis['candidates_found']}")
                print(f"Корректных римских чисел: {analysis['valid_numerals']}")

                print("\nСтатистика валидации:")
                for status, count in analysis['validation_stats'].items():
                    print(f"  {status}: {count}")

                if analysis['numerals']:
                    print("\nНайденные числа:")
                    for numeral in analysis['numerals']:
                        print(f"  {numeral['roman']} = {numeral['arabic']} (строка {numeral['line']})")

            except FileNotFoundError:
                print(f"Файл {file_path} не найден.")
            except Exception as e:
                print(f"Ошибка при чтении файла: {e}")

        elif choice == '5':
            print("\nПримеры КОРРЕКТНЫХ римских чисел:")
            correct_examples = [
                "I", "IV", "V", "IX", "X", "XL", "L", "XC", "C", "CD", "D", "CM", "M",
                "III", "VIII", "XIV", "XIX", "XXIV", "XLII", "XCVI", "CCLVI", "MMXXIV"
            ]

            for example in correct_examples:
                result = roman.validate_roman_numeral(example)
                print(f"  {example:8} = {result.value:4}  ✓ {result.status.value}")

            print("\nПримеры НЕКОРРЕКТНЫХ римских чисел:")
            incorrect_examples = [
                ("IIII", "Слишком много I (4 вместо IV)"),
                ("VV", "V не может повторяться"),
                ("XXXX", "Слишком много X (40 = XL)"),
                ("IC", "I не может вычитать C (99 = XCIX)"),
                ("VX", "V не может вычитать X (5 = V)"),
                ("IIV", "Неправильное вычитание (3 = III)"),
                ("XM", "X не может вычитать M (990 = CMXC)"),
                ("", "Пустая строка"),
                ("ABC", "Не римские символы"),
                ("IXIX", "Неправильный порядок"),
            ]

            for example, reason in incorrect_examples:
                result = roman.validate_roman_numeral(example)
                print(f"  {example:8} ✗ {result.status.value}: {reason}")

        elif choice == '6':
            print("\nЗапуск тестового прогона...")

            test_cases = [
                ("I", 1, True),
                ("IV", 4, True),
                ("IX", 9, True),
                ("XLII", 42, True),
                ("XCIX", 99, True),
                ("MMXXIV", 2024, True),
                ("CDXLIV", 444, True),
                ("MCMLXXXIV", 1984, True),
                ("IIII", None, False),
                ("VX", None, False),
                ("IC", None, False),
                ("XM", None, False),
                ("ABC", None, False),
            ]

            print(f"{'Римское':<12} {'Арабское':<8} {'Статус':<20} {'Тест'}")
            print("-" * 60)

            all_passed = True
            for roman_num, expected_arabic, should_be_valid in test_cases:
                result = roman.validate_roman_numeral(roman_num)

                is_valid = result.status == RomanNumeralValidation.VALID
                passed = (is_valid == should_be_valid) and (not expected_arabic or result.value == expected_arabic)

                status = "✓ PASS" if passed else "✗ FAIL"

                print(f"{roman_num:<12} {result.value or '-':<8} {result.status.value:<20} {status}")

                if not passed:
                    all_passed = False
                    if result.error_details:
                        print(f"    Ошибка: {result.error_details}")

            print("\n" + "=" * 60)
            print("РЕЗУЛЬТАТ ТЕСТОВ: " + ("ВСЕ ТЕСТЫ ПРОЙДЕНЫ ✓" if all_passed else "ЕСТЬ ОШИБКИ ✗"))

            print("\nТест обратной конвертации (1-100):")
            for i in range(1, 101):
                roman_num = roman.arabic_to_roman(i)
                back_to_arabic = roman.roman_to_arabic(roman_num)
                if i != back_to_arabic:
                    print(f"Ошибка: {i} -> {roman_num} -> {back_to_arabic}")
                    break
            else:
                print("Все числа 1-100 корректно конвертируются туда и обратно ✓")

        else:
            print("Неверный выбор. Попробуйте снова.")


if __name__ == "__main__":
    interactive_demo()