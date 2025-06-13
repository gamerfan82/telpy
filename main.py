from aiogram import Bot, Dispatcher, executor, types
import os
from keep_alive import keep_alive
keep_alive()

bot = Bot(token=os.environ.get('token'))
dp = Dispatcher(bot)

@dp.message_handler(commands=['start', 'help'])
async def welcome(message: types.Message):
    await message.reply("سلام خوش امدی.\n این یک نمونه تست است")

@dp.message_handler(commands=['logo'])
async def logo(message: types.Message):
    await message.answer_photo('https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTuz2BDT2OoYGewQiUQg2fWGhjM8PizG8vtJQ&s')

@dp.message_handler()
async def echo(message: types.Message):
    await message.reply(message.text)


if __name__ == '__main__':
    executor.start_polling(dp)
