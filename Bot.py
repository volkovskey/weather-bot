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
async def weather(message: types.Message):
    try:
        city = (message.text).replace("/weather ", "")
        await bot.send_message(message.chat.id, CurrentWeather(city))
    except:
        print("Error parsing")

@dp.message_handler(commands=['short'])
async def sn(message: types.Message):
    lst = (message.text).split()
    password = lst[1]
    lst.pop(0)
    City = ""
    for i in lst:
        City += i + " "
    City = City[0:-1]
    if (password == Token.password):
        if (City == "Stop" or City == "stop"):
            try:
                DowngradeDict(message.chat.id)
                await bot.send_message(message.chat.id, "You have been successfully removed from the notification list.")
            except:
                print("Error")
        else:
            UpdateDict(message.chat.id, "False " + City)
            await bot.send_message(message.chat.id, "You have been successfully added to the notification list. Your city: " + City)
    else:
        await bot.send_message(message.chat.id, "Invalid password.")

@dp.message_handler(commands=['long'])
async def sn(message: types.Message):
    lst = (message.text).split()
    password = lst[1]
    lst.pop(0)
    City = ""
    for i in lst:
        City += i + " "
    City = City[0:-1]
    if (password == Token.password):
        if (City == "Stop" or City == "stop"):
            try:
                DowngradeDict(message.chat.id)
                await bot.send_message(message.chat.id, "You have been successfully removed from the notification list.")
            except:
                print("Error")
        else:
            UpdateDict(message.chat.id, "True " + City)
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
    answerText += "Температура воздуха " + str(mainWeatherData['temp']) + " °C, ощущается как " + str(mainWeatherData['feels_like']) + " °C.\n"
    answerText += "Давление составляет " + str(float(mainWeatherData['pressure']) / 10) + " кПа.\nВлажность: " + str(mainWeatherData['humidity']) + "%.\n"
    mainWeatherData = response.json()['clouds']
    answerText += "Облачность: " + str(mainWeatherData['all']) + "%.\n"

    mainWeatherData = response.json()['wind']
    answerText += "Ветер: " + str(mainWeatherData['speed']) + " м/с или " + str(float(mainWeatherData['speed']) * 3.6) + " км/ч. Направление: " + str(mainWeatherData['deg']) + "°."
    return answerText

def Hours(hour):
    a = ""
    if hour >= 24:
        a = str(hour - 24)
        if len(str(a)) == 1:
            a = "0" + a + ":00"
        else:
            a = a + ":00"
    else:
        a = str(hour)
        if len(str(a)) == 1:
            a = "0" + a + ":00"
        else:
            a = a + ":00"
    return a

def TodayWeatherShort(cityW):
    answerText = "Город: " + cityW + "\nКороткая информация:\n\n"
    
    url = "http://api.openweathermap.org/geo/1.0/direct?q=" + cityW + "&limit=1&appid=" + Token.apiKey
    response = requests.get(url)
    geoData = response.json()[0]
    lat = geoData['lat']
    lon = geoData['lon']

    url = "https://api.openweathermap.org/data/2.5/onecall?lat=" + str(lat) + "&lon=" + str(lon) + "&units=metric&lang=ru&exclude=daily&appid=" + Token.apiKey
    response = requests.get(url)
    hourData =  response.json()['hourly']
    for i in range(0, 24):
        answerText += Hours(i + 8) + "    " + "🌡: " + str(int(hourData[i]['temp'])) + "°C (" + str(int(hourData[i]['feels_like'])) + "°C) | 💧: " + str(hourData[i]['pop'] * 100) + " % | ☁️: " + str(hourData[i]['clouds']) + " %\n"
    return answerText

def TodayWeather(cityW):
    answerText = "Город: " + cityW + "\nПолная информация:\n\n"
    
    url = "http://api.openweathermap.org/geo/1.0/direct?q=" + cityW + "&limit=1&appid=" + Token.apiKey
    response = requests.get(url)
    geoData = response.json()[0]
    lat = geoData['lat']
    lon = geoData['lon']

    url = "https://api.openweathermap.org/data/2.5/onecall?lat=" + str(lat) + "&lon=" + str(lon) + "&units=metric&lang=ru&exclude=daily&appid=" + Token.apiKey
    response = requests.get(url)
    hourData =  response.json()['hourly']
    answerText1 = ""
    answerText2 = ""
    for i in range(0, 12):
        answerText1 += Hours(i + 8) + "    " + hourData[i]['weather'][0]['description'] + "\n🌡: " + str(hourData[i]['temp']) + "°C (" + str(hourData[i]['feels_like']) + "°C) | давл: " + str(float(hourData[i]['pressure']) / 10) + "кПа | т. росы: " + str(hourData[i]['dew_point']) + "°C | УФ: " + str(hourData[i]['uvi']) + " | ☁️:" + str(hourData[i]['clouds']) + "% | 🌬: " + str(hourData[i]['wind_speed']) + " м/с или " + str(round(float(hourData[i]['wind_speed'] * 3.6), 2)) + " км/ч (" + str(hourData[i]['wind_deg']) + "°) | 💧: " + str(hourData[i]['pop'] * 100) + "%\n\n"
    for i in range(12, 24):
        answerText2 += Hours(i + 8) + "    " + hourData[i]['weather'][0]['description'] + "\n🌡: " + str(hourData[i]['temp']) + "°C (" + str(hourData[i]['feels_like']) + "°C) | давл: " + str(float(hourData[i]['pressure']) / 10) + "кПа | т. росы: " + str(hourData[i]['dew_point']) + "°C | УФ: " + str(hourData[i]['uvi']) + " | ☁️:" + str(hourData[i]['clouds']) + "% | 🌬: " + str(hourData[i]['wind_speed']) + " м/с или " + str(round(float(hourData[i]['wind_speed'] * 3.6), 2)) + " км/ч (" + str(hourData[i]['wind_deg']) + "°) | 💧: " + str(hourData[i]['pop'] * 100) + "%\n\n"
    answerArr = [answerText, answerText1, answerText2]
    return answerArr

async def scheduler():
    aioschedule.every().day.at("22:00").do(SendWeather)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)

async def SendWeather():
    global usersNotifications
    for i in usersNotifications:
        settings = usersNotifications[i].split()
        isFullInfo = settings[0]
        settings.pop(0)

        city = ""
        for j in settings:
            city += j + " "
        city = city[0:-1]

        await bot.send_message(i, TodayWeatherShort(city))
        arrText = TodayWeather(city)

        if bool(isFullInfo) == True:
            await bot.send_message(i, arrText[0] + arrText[1], disable_notification=True)
            await bot.send_message(i, arrText[0] + arrText[2], disable_notification=True)
        
        

async def on_startup(_):
    asyncio.create_task(scheduler())

if __name__ == '__main__':
    OpenDict()
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)