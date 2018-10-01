# -*- coding: utf-8 -*-

mapping = ("abvgdeziyklmnoprstufhcCABVGDEZIYKLMNOPRSTUFH", "абвгдезийклмнопрстуфхцЦАБВГДЕЗИЙКЛМНОПРСТУФХ")

reversed_specific_mapping = ("эЭыЫ", "eEyY")

pre_processor_mapping = {
    "yo": "ё",
    "Yo": "Ё",
    "iy": "ий",
    "zh": "ж",
    "ts": "ц",
    "ch": "ч",
    "sh": "ш",
    "sch": "щ",
    "yu": "ю",
    "ya": "я",
    "kh": "х",
    "Zh": "Ж",
    "Ts": "Ц",
    "Ch": "Ч",
    "Sh": "Ш",
    "Sch": "Щ",
    "Yu": "Ю",
    "Ya": "Я",
    "Kh": "Х",
}

reversed_specific_pre_processor_mapping = {"ъ": "", "Ъ": "", "ь": "", "Ь": ""}
