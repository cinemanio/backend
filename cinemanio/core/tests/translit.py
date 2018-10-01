from transliterate import translit
from parameterized import parameterized

from cinemanio.core.tests.base import BaseTestCase


class TranslitTest(BaseTestCase):
    @parameterized.expand(
        [
            ("Ирония судьбы, или с легким паром!", "Ironiya sudby, ili s legkim parom!"),
            ("Алексей Мягков", "Aleksey Myagkov"),
            ("Андрей Тарковский", "Andrey Tarkovskiy"),
            ("Наталья Бондарчук", "Natalya Bondarchuk"),
            ("Илья", "Ilya"),
            ("Николай Гринько", "Nikolay Grinko"),
            ("Фридрих Горенштейн", "Fridrikh Gorenshteyn"),
            ("Людмила Фейгинова", "Lyudmila Feyginova"),
            ("Юлиан Семёнов", "Yulian Semyonov"),
            ("Георгий Тейх", "Georgiy Teykh"),
            ("Анатолий Солоницын", "Anatoliy Solonitsyn"),
        ]
    )
    def test_ru_transliteration(self, text, result):
        self.assertEqual(translit(text, "ru", reversed=True), result)
