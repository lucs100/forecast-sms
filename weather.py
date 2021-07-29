from dotenv import load_dotenv
from datetime import datetime
from twilio.rest import Client
import requests, json, os, geocoder, schedule, time

load_dotenv()
WEATHERTOKEN = os.getenv('WEATHERTOKEN')
FROMNUMBER = os.getenv('FROMNUMBER')
TONUMBER = os.getenv('TONUMBER')
TWILIO_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
client = Client(TWILIO_SID, TWILIO_TOKEN)

testMode = False

def getWeatherData():
    g = geocoder.ip('me')
    lat, lon = g.latlng
    part = "minutely,hourly,alerts"

    data = requests.get(f"https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lon}&exclude={part}&appid={WEATHERTOKEN}&units=metric")
    datajson = data.json()
    # should rly refactor into a class lol
    dict = {
        "date": datetime.fromtimestamp(datajson["daily"][0]["dt"]).strftime("%A, %B %d, %Y"),
        "sunrise": datetime.fromtimestamp(datajson["daily"][0]["sunrise"]).strftime("%I:%M %p").lstrip("0"),
        "sunset": datetime.fromtimestamp(datajson["daily"][0]["sunset"]).strftime("%I:%M %p").lstrip("0"),

        "max": round(datajson["daily"][0]["temp"]["max"], 1),
        "min": round(datajson["daily"][0]["temp"]["min"], 1),

        "pop": int(float(datajson["daily"][0]["pop"])*100)
    }
    return dict

def generateReport(dict):
    string = "\n"
    string += (f"Today is {dict['date']}.\nGood morning!\n")
    string += (f"Sunrise: {dict['sunrise']}\nSunset: {dict['sunset']}\n")
    string += (f"Max Temp: {dict['max']}°C\nMin Temp: {dict['min']}°C\n")
    string += (f"PoP: {dict['pop']}%\n")
    return string

def sendMessage():
    message = client.messages.create(
        body = generateReport(getWeatherData()),
        from_=FROMNUMBER,
        to=TONUMBER
    )
    return True

if testMode:
    print(generateReport(getWeatherData()))
else:
    sched = "09:55"
    schedule.every().day.at(sched).do(sendMessage)
    print(f"Message scheduled for {sched}!")

while True:
    schedule.run_pending()
    time.sleep(10)