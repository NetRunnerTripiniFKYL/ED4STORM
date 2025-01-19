from aiogram import F, Router
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import FSInputFile
import keyboards.inline_kb as ikb
from db.modules import modules
from hendlers.commands import auth_users
call_router = Router()


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
    
    # Проверяем, что в данных достаточно частей
    if len(data_parts) != 5:
        await callback.answer("Ошибка в данных. Попробуйте снова.", show_alert=True)
        return
    
    _, module_id, lesson_index, quiz_index, option_index = data_parts
    lesson = modules[module_id]["lessons"][int(lesson_index)]
    quiz = lesson["quizzes"][int(quiz_index)]
    correct_option = quiz["correct_option"]
    
    if int(option_index) == correct_option:
        await callback.answer("Правильно!", show_alert=True)
    else:
        await callback.answer("Неправильно. Попробуйте снова.", show_alert=True)