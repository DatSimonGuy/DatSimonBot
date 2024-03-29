import python_weather
import asyncio
import os
from utils.types import Group
import threading
import schedule

def AwaitSchedule():
    while True:
        schedule.run_pending()
        asyncio.run(asyncio.sleep(1))

async def GetWeather(cities: list):
    weather_message = ""
    weather = python_weather.Client(unit=python_weather.METRIC)
    for city in cities:
        city_weather = await weather.get(city)
        if city_weather is None:
            weather_message = f"{weather_message}\n{city} not found"
            continue
        weather_message = f"{weather_message}\n{city}:\n{city_weather.temperature} °C in {city}\n{city_weather.description}\nwind: {city_weather.wind_speed}km/h {city_weather.wind_direction}\n"
    await weather.close()
    return weather_message

async def ClearMorningMessage():
    for folder in os.listdir("data"):
        group = Group.LoadGroup(folder)
        group.resetDay()

async def MorningMessage(group: Group):
    group.morning_message_sent = True
    group.saveSelf()
    if not group.weather_cities:
        return "Gm!\nEnjoy your coffee! ☕️"
    cities = group.weather_cities
    weather_message = await GetWeather(cities)
    return f"Gm!\nHave today's weather:\n{weather_message}\nEnjoy your coffee! ☕️"

thread = threading.Thread(target=AwaitSchedule)
thread.start()
schedule.every().day.at("00:00").do(asyncio.run(ClearMorningMessage()))