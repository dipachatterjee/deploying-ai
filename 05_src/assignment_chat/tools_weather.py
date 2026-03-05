from langchain.tools import tool
import requests
import json
from utils.logger import get_logger

_logs = get_logger(__name__)

UNIT_MAP = {
    "F": "imperial",
    "FAHRENHEIT": "imperial",
    "C": "metric",
    "CELSIUS": "metric",
    "K": "standard",
    "KELVIN": "standard"
}

@tool
def get_weather(location:str, unit:str, date:str = "TODAY") -> str:
    """
    An API call to a weather service is made.
    The API call is to https://api.openweathermap.org/data/2.5/weather
    and takes three parameters location, unit, and date.
    Accepted values for location are: any city
    Accepted values for unit are: F, fahrenheit, C, celsius, K, kelvin
    Accepted values for date are: Date in format (YYYY-MM-DD) OR "TODAY" OR "TOMORROW" OR "YESTERDAY".
    """
    _logs.debug(f'Getting weather for location {location}, date {date}, and unit {unit}')
    response = get_weather_from_service(location, unit, date)
    weather = get_weather_from_response(location, response)
    _logs.debug(f'Weather result: {weather}')
    return weather



def get_weather_from_service(location:str, unit:str, day:str):
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": location.title(),
        "units": UNIT_MAP.get(unit.upper(), "metric"),
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response



def get_weather_from_response(location:str, response:requests.Response) -> str:
    resp_dict = response.json()  # simpler than json.loads(response.text)
    weather_list = resp_dict.get("weather", [])
    main_data = resp_dict.get("main", {})
    if weather_list:
        description = weather_list[0].get("description", "No description")
    else:
        description = "No description"
    temp = main_data.get("temp", "No temperature")
    weather = f"Weather for {location.title()}: {description}, Temp: {temp}"
    return weather