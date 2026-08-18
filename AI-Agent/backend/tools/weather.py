import requests
from langchain_core.tools import tool
@tool
def get_weather(city:str,forecast:bool=False)->str:
   """ 
   Get the current weather or future forecast for any city.
   Use forecast=True when the user asks about future weather.
   """
   #Find city coordinates
   geocoding_url= "https://geocoding-api.open-meteo.com/v1/search"
   geocoding_params={
      "name":city,
      "count":1,
      "language":"en",
      "format":"json"
   }
   geocoding_response=requests.get(
      geocoding_url,
      params=geocoding_params,
      timeout=10
   )
   geocoding_response.raise_for_status()
   location_data=geocoding_response.json()

   #check whether city was found
   if"results" not in location_data:
      return f"Sorry, I could not find the city '{city}'."
   location=location_data["results"][0]
   latitude=location["latitude"]
   longitude=location["longitude"]

   city_name=location["name"]
   country=location.get("country","")
   #Future forecast
   if forecast:
      weather_url="https://api.open-meteo.com/v1/forecast"
      weather_params={
         "latitude":latitude,
         "longitude":longitude,
         "daily":(
            "weather_code,"
            "temperature_2m_max,"
            "wind_speed_10m_max"
         ),
         "forecast_days":3,
         "timezone":"auto",
         "temperature_unit":"celsius",
         "wind_speed_unit":"kmh"
      }
      weather_response=requests.get(
         weather_url,
         params=weather_params,
         timeout=10
      )
      weather_response.raise_for_status()
      daily=weather_response.json()["daily"]
      conditions = {
         0:"Clear",
         1:"Mainly clear",
         2: "Partly cloudy",
         3: "Cloudy",
         45: "Fog",
         61: "Rain",
         63: "Moderate rain",
         65: "Heavy rain",
         80: "Rain showers",
         82: "Heavy rain showers",
         95: "Thunderstorm"
      }
      result=[f"Forecast for{city_name},{country}:"]
      for i, date in enumerate(daily["time"]):
         condition=conditions.get(
            daily["weather_code"][i],
            "other"
         )
         temperature = daily["temperature_2m_max"][i]
         wind = daily["wind_speed_10m_max"][i]
         result.append(
            f"{date}:{condition},"
            f"{temperature}°C,"
            f"wind{wind} km/h"
         )
      return "\n".join(result)

   #get current weather
   weather_url="https://api.open-meteo.com/v1/forecast"
   weather_params={
      "latitude":latitude,
      "longitude":longitude,
      "current":(
         "temperature_2m,"
         "relative_humidity_2m,"
         "apparent_temperature,"
         "wind_speed_10m"
      ),
      "temperature_unit":"celsius",
      "wind_speed_unit":"kmh"
   }
   weather_response=requests.get(
      weather_url,
      params=weather_params,
      timeout=10
   )
   weather_response.raise_for_status()
   weather_data=weather_response.json()
   current=weather_data["current"]

   temperature=current["temperature_2m"]
   humidity=current["relative_humidity_2m"]
   apparent_temperature=current["apparent_temperature"]
   wind_speed=current["wind_speed_10m"]

   #return weather information
   return(
      f"Current weather in {city_name},{country}: "
      f"{temperature}°C, "
      f"feels like {apparent_temperature}°C, "
      f"humidity{humidity}%, "
      f"wind speed{wind_speed}km/h."
   )
