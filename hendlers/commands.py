# Импортируем библиотеку aiogram для работы с ботом
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters.command import Command
from config import CODE as ACCESS_CODE
import defs # Импортируем функции для работы с данными пользователей
import keyboards.reply_kb as rkb

# Создаем роутер для обработки команд
router = Router()

# Загружаем список авторизованных пользователей
auth_users = defs.load_authorized_users()

# Обработчик команды /start
@router.message(Command("start"))
async def cmd_start(message: Message):
    if message.from_user.id in auth_users:
        await message.answer("Вы уже авторизованы! Можете взаимодействовать с ботом.", reply_markup=rkb.reply_start)
    else:
        await message.answer("Добро пожаловать! Введите секретный код для авторизации.")

# Обработчик ввода кода
@router.message(F.text == ACCESS_CODE)
async def handle_message(message: Message):
    user_id = message.from_user.id

    if user_id in auth_users:
        await message.answer("Вы уже авторизованы! Ваше сообщение обработано.", reply_markup=rkb.reply_start)
    elif message.text == ACCESS_CODE:
        auth_users.add(user_id)
        defs.save_authorized_users(auth_users)  # Сохраняем после успешной авторизации
        await message.answer("Код верен! Теперь вы можете использовать бота.", reply_markup=rkb.reply_start)
    else:
        await message.answer("Неверный код. Попробуйте снова.")

