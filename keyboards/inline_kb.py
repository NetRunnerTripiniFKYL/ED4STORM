from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from db.modules import modules

async def modules_list():
    keyboard = InlineKeyboardBuilder()
    for module_id, module in modules.items():
        keyboard.add(InlineKeyboardButton(text=module["name"], callback_data=f"module_{module_id}"))
    keyboard.adjust(1)
    return keyboard.as_markup()