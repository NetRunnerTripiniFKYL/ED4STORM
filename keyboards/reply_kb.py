from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

reply_start = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Модули")],
    [KeyboardButton(text="Личный кабинет")]
    ],  resize_keyboard=True)

reply_cabinet = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Вернутся в меню")],
    [KeyboardButton(text="Мой прогресс")],
    [KeyboardButton(text="Показать данные")],
    [KeyboardButton(text="Перезаписать данные")]
    ],  resize_keyboard=True)