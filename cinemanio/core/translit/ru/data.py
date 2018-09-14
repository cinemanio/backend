# -*- coding: utf-8 -*-

mapping = (
    u"abvgdeziyklmnoprstufhcCABVGDEZIYKLMNOPRSTUFH",
    u"абвгдезийклмнопрстуфхцЦАБВГДЕЗИЙКЛМНОПРСТУФХ",
)

reversed_specific_mapping = (
    u"эЭыЫ",
    u"eEyY"
)

pre_processor_mapping = {
    u"yo": u"ё",
    u"Yo": u"Ё",
    u"iy": u"ий",
    u"zh": u"ж",
    u"ts": u"ц",
    u"ch": u"ч",
    u"sh": u"ш",
    u"sch": u"щ",
    u"yu": u"ю",
    u"ya": u"я",
    u"kh": u"х",
    u"Zh": u"Ж",
    u"Ts": u"Ц",
    u"Ch": u"Ч",
    u"Sh": u"Ш",
    u"Sch": u"Щ",
    u"Yu": u"Ю",
    u"Ya": u"Я",
    u"Kh": u"Х",
}

reversed_specific_pre_processor_mapping = {
    u"ъ": u"",
    u"Ъ": u"",
    u"ь": u"",
    u"Ь": u"",
}
