from aiogram import types

main_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
main_keyboard.add('Проверить почту')
main_keyboard.add('Настройки')

start_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
start_keyboard.add('Настройки')
