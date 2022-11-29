from aiogram import types, Dispatcher
from configurations import dp, bot


@dp.message_handler()
async def other_commands(message: types.Message):
    await bot.send_message(message.from_user.id, "Такой команды нет")


def register_handlers_other(dp: Dispatcher):
    dp.register_message_handler(other_commands)
