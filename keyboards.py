from aiogram.types import KeyBoardButton, ReplyKeyBoardMarkup 

btnweather = KeyBoardButton("Погода ⛅")
btncube = KeyBoardButton("Кости 🎲")

greet_kb = ReplyKeyBoardMarkup().add(btnweather, btncube)
