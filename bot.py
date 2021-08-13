import logging
from aiogram.dispatcher.filters.builtin import Command 
import requests
import datetime
import os

from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram_calendar import simple_cal_callback, SimpleCalendar
from aiogram import dispatcher
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from config import open_weather_token
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor 


logging.basicConfig(level=logging.INFO)

class Form(StatesGroup):
    weather = State() 

TOKEN = os.environ.get("TOKEN")
bot = Bot(token=TOKEN, parse_mode=types.ParseMode.HTML)  #Создаем бота, передаем токен и подключаем html 
dp = Dispatcher(bot, storage=MemoryStorage()) #Создаем диспетчер, который управляет handler


@dp.message_handler(commands=["start"])
async def start_command(message: types.Message): #Создаем ф-ию, которая реагирует на сообщение /start
    print(message.from_user.username,"использует бота")
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button = ["/weather", "/calendar"]
    keyboard.add(*button)
              
    text = "Привет, на связи Сурикат!\n\nСписок команд:\n/weather - посмотреть погоду в твоем городе"
    await bot.send_message(message.from_user.id, text, reply_markup=keyboard)


@dp.message_handler(commands=['weather', 'profile'], state='*')
async def command(message: types.Message):
    await message.reply("Напиши мне свой город")
    await Form.weather.set()
    print(message.from_user.username,"использует бота для погоды")


@dp.message_handler(state=Form.weather)
async def get_stats(message: types.Message, state: FSMContext):

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
            f"<b>Погода в городе:</b>  {city}\n<b>Страна:</b> {country}\n"
            f"<b>Температура:</b> {round(cur_weather)} °С, {ws}\n<b>Макс/мин температура:</b> {round(temp_max)} °С / {round(temp_min)} °С\n"
            f"<b>Скорость ветра:</b> {round(wind)} м/c\n"
            f"<b>Влажность:</b> {humidity}%\n<b>Рассвет:</b> {sunrise}\n<b>Закат:</b> {sunset}\n<b>Световой день:</b> {lenght_day}\n"
        )
    
        await state.finish()

    except: #вывод ошибки
        await message.reply("Ты что-то напутал, напиши ещё раз свой город")


@dp.message_handler(commands=['calendar'])
async def nav_cal_handler(message: types.Message):
    await message.answer("Выберите дату: ", reply_markup=await SimpleCalendar().start_calendar())

@dp.callback_query_handler(simple_cal_callback.filter())
async def process_simple_calendar(callback_query: types.CallbackQuery, callback_data: dict):
    selected, date = await SimpleCalendar().process_selection(callback_query, callback_data)
    if selected:
        await callback_query.message.answer(
            f'Ты выбрал {date.strftime("%d.%m.%Y")}'
        )


if __name__ == "__main__":
    executor.start_polling(dp) #Запускаем бота

