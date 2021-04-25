from aiogram import Bot, Dispatcher, executor, types
import Token
from threading import Thread
import time
import datetime
import asyncio
import requests
import aioschedule

bot = Bot(token=Token.token) #bot and its atributes declaration
dp = Dispatcher(bot)
usersNotifications = {}

@dp.message_handler(commands=['weather'])
async def main_void(message: types.Message):
    city = (message.text).replace("/weather ", "")
    await bot.send_message(message.chat.id, CurrentWeather(city))

@dp.message_handler(commands=['SN'])
async def main_void(message: types.Message):
    lst = (message.text).split()
    password = lst[1]
    City = lst[2]
    if (password == Token.password):
        if (City == "Stop" or City == "stop"):
            try:
                DowngradeDict(message.chat.id)
                await bot.send_message(message.chat.id, "You have been successfully removed from the notification list.")
            except:
                print("Error")
        else:
            UpdateDict(message.chat.id, City)
            await bot.send_message(message.chat.id, "You have been successfully added to the notification list. Your city: " + City)
    else:
        await bot.send_message(message.chat.id, "Invalid password.")

def UpdateDict(newID, City):
    global usersNotifications
    usersNotifications[newID] = City
    fileDict = open("UsersNotifications.txt", "w")
    fileDict.write(str(usersNotifications))
    fileDict.close()

def DowngradeDict(deleteID):
    global usersNotifications
    del usersNotifications[deleteID]
    fileDict = open("UsersNotifications.txt", "w")
    fileDict.write(str(usersNotifications))
    fileDict.close()

def OpenDict():
    fileDict = open("UsersNotifications.txt")
    global usersNotifications
    usersNotifications = eval(fileDict.read())
    fileDict.close()

def CurrentWeather(cityW):
    answerText = "Город: " + cityW + "\n\n"
    url = "https://api.openweathermap.org/data/2.5/weather?q=" + cityW + "&units=metric&lang=ru&appid=" + Token.apiKey
    response = requests.get(url)
    mainWeatherData = response.json()['weather'][0]
    answerText += "Текущая погода: " + mainWeatherData['description'] + ".\n"
    mainWeatherData = response.json()['main']
    answerText += "Температура воздуха " + str(mainWeatherData['temp']) + "°C, ощущается как " + str(mainWeatherData['feels_like']) + "°C.\n"
    answerText += "Давление составляет " + str(float(mainWeatherData['pressure']) / 10) + " кПа.\nВлажность: " + str(mainWeatherData['humidity']) + "%.\n"
    mainWeatherData = response.json()['clouds']
    answerText += "Облачность: " + str(mainWeatherData['all']) + "%.\n"

    mainWeatherData = response.json()['wind']
    answerText += "Ветер: " + str(mainWeatherData['speed']) + " м/с или " + str(float(mainWeatherData['speed']) * 3.6) + " км/ч. Направление: " + str(mainWeatherData['deg']) + "°."
    return answerText

def TodayWeather(cityW):
    answerText = "Город: " + cityW + "\n\n"
    #НАдо узнать координаты через апи, потом расковырять джейсон и посчитать/построить графики для сегодняшнего дня
    url = "https://api.openweathermap.org/data/2.5/weather?q=" + cityW + "&units=metric&lang=ru&appid=" + Token.apiKey
    response = requests.get(url)
    mainWeatherData = response.json()['weather'][0]
    answerText += "Текущая погода: " + mainWeatherData['description'] + ".\n"
    mainWeatherData = response.json()['main']
    answerText += "Температура воздуха " + str(mainWeatherData['temp']) + "°C, ощущается как " + str(mainWeatherData['feels_like']) + "°C.\n"
    answerText += "Давление составляет " + str(float(mainWeatherData['pressure']) / 10) + " кПа.\nВлажность: " + str(mainWeatherData['humidity']) + "%.\n"
    mainWeatherData = response.json()['clouds']
    answerText += "Облачность: " + str(mainWeatherData['all']) + "%.\n"

    mainWeatherData = response.json()['wind']
    answerText += "Ветер: " + str(mainWeatherData['speed']) + " м/с или " + str(float(mainWeatherData['speed']) * 3.6) + " км/ч. Направление: " + str(mainWeatherData['deg']) + "°."
    return answerText

async def scheduler():
    aioschedule.every().day.at("22:00").do(SendWeather)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)

async def SendWeather():
    global usersNotifications
    for i in usersNotifications:
        await bot.send_message(i, TodayWeather(usersNotifications[i]))

async def on_startup(_):
    asyncio.create_task(scheduler())

if __name__ == '__main__':
    OpenDict()
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)