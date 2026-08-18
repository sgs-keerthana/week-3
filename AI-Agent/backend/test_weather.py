from tools.weather import get_weather
result=get_weather.invoke({
    "city":"salem",
    "forecast":True
})
print(result)