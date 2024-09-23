from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# Кнопки для обычной клавиатуры
btn_create_profile_1c = KeyboardButton('Заявка на создание пользователя в 1С')
btn_create_que_1c = KeyboardButton('Заявка на консультацию с IT работником компании "ALGORITM23"')

# Создание обычной клавиатуры
btn_profile_menu = ReplyKeyboardMarkup(resize_keyboard=True)
btn_profile_menu.row(btn_create_profile_1c, btn_create_que_1c)


# Функция для создания inline клавиатуры с уникальным идентификатором
def create_inline_keyboard(request_id):
    inline_keyboard = InlineKeyboardMarkup()
    btn_answer_inline = InlineKeyboardButton(
        text="Пользователь создан",
        callback_data=f"user_created_{request_id}"
    )
    inline_keyboard.add(btn_answer_inline)
    return inline_keyboard

# Функция для создания inline клавиатуры с уникальным идентификатором
def create_inline_keyboard_Otmena(request_id):
    inline_keyboard_Otmena = InlineKeyboardMarkup()
    btn_answer_inline_Otmena = InlineKeyboardButton(
        text="Отклонить заявку",
        callback_data=f"user_created_Otmena_{request_id}"
    )
    inline_keyboard_Otmena.add(btn_answer_inline_Otmena)
    return inline_keyboard_Otmena