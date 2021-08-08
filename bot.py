import requests
import datetime
import os

from aiogram import dispatcher
from config import open_weather_token
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor 

TOKEN = os.environ.get("TOKEN")
bot = Bot(token=TOKEN)  #Создаем бота и передаем токен
dp = Dispatcher(bot) #Создаем диспетчер, который управляет handler

@dp.message_handler(commands=["start"])
async def start_command(message: types.Message): #Создаем ф-ию, которая реагирует на сообщение /start
    print(message.from_user.username,"использует бота-suricat")
    await message.reply("Привет, на связи Сурикат! Если ты хочешь, чтобы я магическим способом узнал погоду, напиши мне свой город.")


@dp.message_handler()
async def get_weather(message: types.Message):

    smile = {
        "Clear": "Ясно \U00002600",
        "Clouds": "Облачно \U00002601",
        "Rain": "Дождь \U00002614",
        "Thunderstorm": "Гроза \U000026A1",
        "Snow": "Снег \U0001F328",
        "Mist": "Туман \U0001F32B"
    }

    try: #Формируем наш запрос через переменную r
        r = requests.get( 
            f"https://api.openweathermap.org/data/2.5/weather?q={message.text}&appid={open_weather_token}&units=metric" #Для запроса требуется city и open_wether_token
        )

        data = r.json() #вывод запроса

        city = data["name"]
        country = data["sys"]["country"] #Страна
        cur_weather = data["main"]["temp"] #текущая температура

        weather_dis = data["weather"][0]["main"]
        if weather_dis in smile: #Если значение совпадет с одним из ключей словаря, то мы забираем его значение
            ws = smile[weather_dis]
        else:
            ws = "Я хер знает, сам посмотри и не трать мое время :/"

        #Находится в блоке main, после обращаемся к ключу temp
        humidity = data["main"]["humidity"] #влажность 
        temp_max = data["main"]["temp_max"] #Макс темп
        temp_min = data["main"]["temp_min"] #Мин темп
        wind = data["wind"]["speed"] #скорость ветра
        sunrise = datetime.datetime.fromtimestamp(data["sys"]["sunrise"]).strftime('%d.%m.%Y %H:%M') #рассвет
        sunset = datetime.datetime.fromtimestamp(data["sys"]["sunset"]).strftime('%d.%m.%Y %H:%M') #закат
        lenght_day = datetime.datetime.fromtimestamp(data["sys"]["sunset"]) - datetime.datetime.fromtimestamp(data["sys"]["sunrise"]) #Продолжительность дня

        await message.reply(f"*** {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')} ***\n"
            f"Погода в городе: {city}\nСтрана: {country}\n"
            f"Температура: {cur_weather}C° {ws}\nМаксимальная температура: {temp_max}C°\nМинимальная температура: {temp_min}C°\n"
            f"Скорость ветра: {wind}\n"
            f"Влажность: {humidity}%\nРассвет: {sunrise}\nЗакат: {sunset}\nПродолжительность дня: {lenght_day}\n"
            f"*** Хорошего дня! А я пойду самосовершенствоваться) ***"
        )

    except: #вывод ошибки
        await message.reply("Ты что-то напутал, напиши ещё раз свой город")


if __name__ == "__main__":
    executor.start_polling(dp) #Запускаем бота

