from aiogram import F, Router, types
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import FSInputFile
import keyboards.inline_kb as ikb
from db.modules import modules
from hendlers.commands import auth_users
import defs
import keyboards.reply_kb as rkb

call_router = Router()

#-----------------------------------------------------------------------------------------------------------#

#Message
@call_router.message(F.text == "Модули")
async def menu(message: Message):
    if message.from_user.id in auth_users:
        await message.answer("Доступные вам модули:", reply_markup=await ikb.modules_list())
    else:
        await message.answer("Вы не авторизованы! Пожалуйста, авторизуйтесь с помощью команды /start.")

# Обработка выбора модуля
@call_router.callback_query(F.data.startswith("module_"))
async def show_lessons(callback: CallbackQuery):
    module_id = callback.data.split("_")[1]
    lessons = modules[module_id]["lessons"]
    keyboard = InlineKeyboardBuilder()
    for index, lesson in enumerate(lessons):
        keyboard.add(InlineKeyboardButton(text=lesson["name"], callback_data=f"lesson_{module_id}_{index}"))
    await callback.message.answer("Выберите урок:", reply_markup=keyboard.as_markup())
    await callback.answer()

# Отправка урока
@call_router.callback_query(F.data.startswith("lesson_"))
async def send_lesson(callback: CallbackQuery):
    _, module_id, lesson_index = callback.data.split("_")
    lesson = modules[module_id]["lessons"][int(lesson_index)]
    await callback.answer()
    if "video" in lesson:
        video = FSInputFile(lesson["video"])
        await callback.message.answer_video(video)
    
    if "image" in lesson:
        photo = FSInputFile(lesson["image"])
        # Если есть и текст, и изображение - отправляем вместе
        if "text" in lesson:
            await callback.message.answer_photo(photo, caption=lesson["text"])
        else:
            await callback.message.answer_photo(photo)
    # Если есть только текст без изображения
    elif "text" in lesson:
        await callback.message.answer(lesson["text"])
        
    if "file" in lesson:
        document = FSInputFile(lesson["file"])
        await callback.message.answer_document(document)

    await callback.answer()
    
    # Отправка тестов
    for quiz_index, quiz in enumerate(lesson["quizzes"]):  # Предполагается, что "quizzes" - это список всех тестов в уроке
        keyboard = InlineKeyboardBuilder()
        for option_index, option in enumerate(quiz["options"]):
            
            # Формируем callback_data с правильным количеством частей
            keyboard.add(InlineKeyboardButton(text=option, callback_data=f"quiz_{module_id}_{lesson_index}_{quiz_index}_{option_index}"))
        await callback.message.answer(quiz["question"], reply_markup=keyboard.as_markup())

# Обработка ответа на тест
@call_router.callback_query(F.data.startswith("quiz_"))
async def handle_quiz(callback: CallbackQuery):
    data_parts = callback.data.split("_")
    
    if len(data_parts) != 5:
        await callback.answer("Ошибка в данных. Попробуйте снова.", show_alert=True)
        return
    
    _, module_id, lesson_index, quiz_index, option_index = data_parts
    lesson = modules[module_id]["lessons"][int(lesson_index)]
    quiz = lesson["quizzes"][int(quiz_index)]
    correct_option = quiz["correct_option"]
    
    is_correct = int(option_index) == correct_option
    defs.update_user_progress(callback.from_user.id, module_id, lesson_index, quiz_index, is_correct)
    
    if is_correct:
        await callback.answer("Правильно!", show_alert=True)
    else:
        await callback.answer("Неправильно. Попробуйте снова.", show_alert=True)

#-----------------------------------------------------------------------------------------------------------#
# Вернутся в меню
@call_router.message(F.text == "Вернутся в меню")
async def back_to_menu(message: Message):
    await message.answer("Вы вернулись в меню.", reply_markup=rkb.reply_start)

# Перезапись данных
@call_router.message(F.text == "Перезаписать данные")
async def rewrite_data(message: Message):
    defs.clear_user_data(message.from_user.id)
    user_data = {'photo': None, 'nickname': None, 'telegram_link': None}
    defs.set_user_data(message.from_user.id, user_data)
    await message.answer("Данные удалены. Пожалуйста, заново заполните свой профиль. Начнем с того, чтобы ты загрузил свою фотографию.", reply_markup=rkb.reply_cabinet)

# Мой прогресс
@call_router.message(F.text == "Мой прогресс")
async def show_progress(message: Message):
    progress = defs.get_user_progress(message.from_user.id)
    if not progress:
        await message.answer("У вас пока нет прогресса.")
        return
    
    progress_message = "Ваш прогресс:\n"
    for module_id, lessons in progress.items():
        progress_message += f"Модуль {modules[module_id]["name"]}:\n"
        for lesson_index, quizzes in lessons.items():
            progress_message += f"  Урок {modules[module_id]["lessons"][int(lesson_index)]["name"]}:\n"
            for quiz_index, is_correct in quizzes.items():
                status = "✅" if is_correct else "❌"
                progress_message += f"    Тест {quiz_index}: {status}\n"
    await message.answer(progress_message)

#-----------------------------------------------------------------------------------------------------------#

# Личный кабинет
@call_router.message(F.text == "Личный кабинет")
async def cabinet(message: Message):
    # Инициализация данных пользователя
    if defs.get_user_data(message.from_user.id) is None:
        user_data = {'photo': None, 'nickname': None, 'telegram_link': None}
        defs.set_user_data(message.from_user.id, user_data)
        await message.answer("Привет! Это твой личный кабинет. Начнем с того, чтобы ты загрузил свою фотографию.", reply_markup=rkb.reply_cabinet)
    else:
        await message.answer("Привет! Это твой личный кабинет.", reply_markup=rkb.reply_cabinet)

# Обработка получения фотографии
@call_router.message(F.photo)
async def photo_received(message: Message):
    user_data = defs.get_user_data(message.from_user.id)
    if user_data:
        user_data['photo'] = message.photo[-1].file_id
        defs.set_user_data(message.from_user.id, user_data)
        await message.answer("Фото получено! Теперь, пожалуйста, напиши свой ник (например, @example).")
    else:
        await message.answer("Произошла ошибка при получении фотографии. Попробуйте еще раз.")

# Обработка получения ника
@call_router.message(lambda message: message.text.startswith('@'))
async def nickname_received(message: types.Message):
    user = defs.get_user_data(message.from_user.id)
    if user:
        user['nickname'] = message.text  # Обновляем ник
        defs.set_user_data(message.from_user.id, user)  # Сохраняем обновленные данные
    await message.answer("Ник принят! Теперь, напиши ссылку на свой Telegram (например, https://t.me/******).")

# Обработка получения ссылки на Telegram
@call_router.message(lambda message: message.text.startswith('https://t.me/'))
async def telegram_link_received(message: types.Message):
    user = defs.get_user_data(message.from_user.id)
    if user:
        user['telegram_link'] = message.text  # Обновляем ссылку на Telegram
        defs.set_user_data(message.from_user.id, user)  # Сохраняем обновленные данные
    await message.answer(
        f"Супер! Вот твои данные:\n\n"
        f"Фото: {user['photo']}\n"
        f"Ник: {user['nickname']}\n"
        f"Ссылка на Telegram: {user['telegram_link']}\n\n"
        f"Если хочешь изменить какую-то информацию, просто напиши мне."
    )
# Обработка команд для отображения данных пользователя
@call_router.message(F.text == "Показать данные")
async def show_profile(message: types.Message):
    user = defs.get_user_data(message.from_user.id)
    if user:
        profile_info = (
            f"Твой профиль:\n\n"
            f"Фото: {user['photo'] if user['photo'] else 'Не загружено'}\n"
            f"Ник: {user['nickname'] if user['nickname'] else 'Не задан'}\n"
            f"Ссылка на Telegram: {user['telegram_link'] if user['telegram_link'] else 'Не указана'}"
        )
    else:
        profile_info = "Ты не заполнил свой профиль."
    await message.answer(profile_info)