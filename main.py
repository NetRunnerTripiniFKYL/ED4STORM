# Импортируем необходимые модули
from config import TOKEN
import logging
import asyncio
from aiogram import Bot, Dispatcher
from hendlers.commands import router as commands_router
from hendlers.callback import call_router as callback_router
# Логирование для отслеживания ошибок и событий
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(TOKEN)
dp = Dispatcher()

# Основная функция для запуска бота
async def main():
    dp.include_router(commands_router)
    dp.include_router(callback_router)
    await dp.start_polling(bot) 

# Запуск бота
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Bot stopped")

