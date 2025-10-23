#!/usr/bin/env python3
import urllib.request
import json

# Get ISS location
iss_response = urllib.request.urlopen('http://api.open-notify.org/iss-now.json')
iss_data = json.loads(iss_response.read())

lat = float(iss_data['iss_position']['latitude'])
lon = float(iss_data['iss_position']['longitude'])

# Get weather at ISS location
weather_url = f'https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true'
weather_response = urllib.request.urlopen(weather_url)
weather_data = json.loads(weather_response.read())

weather = weather_data['current_weather']

print(f"\n🛰️  ISS Location: {lat:.2f}°, {lon:.2f}°")
print(f"🌡️  Temperature: {weather['temperature']}°C")
print(f"💨 Wind Speed: {weather['windspeed']} km/h")
print(f"🕐 Time: {weather['time']}")
